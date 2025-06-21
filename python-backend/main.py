from __future__ import annotations

import io
import json
import requests
from pydantic import BaseModel
from typing import Optional

from agents import (
    Agent,
    RunContextWrapper,
    Runner,
    function_tool,
    handoff,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX


class AccountingAgentContext(BaseModel):
    """Context for document processing and QuickBooks integration."""
    parsed_document: Optional[dict] = None
    last_journal_entry_id: Optional[str] = None


def create_initial_context() -> AccountingAgentContext:
    """Factory for a new AccountingAgentContext."""
    return AccountingAgentContext()


# =========================
# DATA MODELS
# =========================

class ReceiptData(BaseModel):
    vendor: str
    date: str
    total: float
    currency: str


# =========================
# TOOLS
# =========================

@function_tool(
    name_override="parse_pdf",
    description_override="Parse a PDF receipt and extract structured data",
)
async def parse_pdf(
    context: RunContextWrapper[AccountingAgentContext], pdf_url: str
) -> ReceiptData:
    """Download a PDF and extract key receipt fields."""
    response = requests.get(pdf_url)
    response.raise_for_status()
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(response.content))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)

    import openai

    client = openai.OpenAI()
    prompt = (
        "Extract the vendor name, date, total amount and currency from the "
        "following receipt text and respond with JSON matching the ReceiptData model:"
    )
    completion = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
        response_format={"type": "json_object"},
    )
    data = json.loads(completion.choices[0].message.content)
    receipt = ReceiptData(**data)
    context.context.parsed_document = receipt.model_dump()
    return receipt


@function_tool(
    name_override="create_journal_entry",
    description_override="Create a QuickBooks journal entry from the parsed data",
)
async def create_journal_entry(
    context: RunContextWrapper[AccountingAgentContext],
) -> str:
    """Send receipt data to QuickBooks as a journal entry."""
    if context.context.parsed_document is None:
        return "No parsed document available"

    data = ReceiptData(**context.context.parsed_document)
    # Normally you would use the QuickBooks SDK here. This demo simply mocks it.
    entry_id = "QB-" + data.vendor[:3].upper() + "-001"
    context.context.last_journal_entry_id = entry_id
    return f"Journal entry {entry_id} created for {data.vendor} totaling {data.total} {data.currency}"


@function_tool(
    name_override="get_journal_entry",
    description_override="Retrieve a journal entry from QuickBooks",
)
async def get_journal_entry(entry_id: str) -> str:
    """Stub that pretends to fetch a journal entry."""
    return f"Details for journal entry {entry_id}"


# =========================
# AGENTS
# =========================

def parser_instructions(
    run_context: RunContextWrapper[AccountingAgentContext], agent: Agent[AccountingAgentContext]
) -> str:
    return (
        f"{RECOMMENDED_PROMPT_PREFIX}\n"
        "You are a document parsing agent. Use the parse_pdf tool to extract data from receipts or invoices."
    )


document_parser_agent = Agent[AccountingAgentContext](
    name="Document Parser",
    model="gpt-4-turbo",
    handoff_description="Parse receipt PDFs using the parse_pdf tool",
    instructions=parser_instructions,
    tools=[parse_pdf],
)


def journal_entry_instructions(
    run_context: RunContextWrapper[AccountingAgentContext], agent: Agent[AccountingAgentContext]
) -> str:
    return (
        f"{RECOMMENDED_PROMPT_PREFIX}\n"
        "Create a QuickBooks journal entry using the create_journal_entry tool."
    )


journal_entry_agent = Agent[AccountingAgentContext](
    name="Journal Entry Agent",
    model="gpt-4-turbo",
    handoff_description="Create QuickBooks journal entries from parsed data",
    instructions=journal_entry_instructions,
    tools=[create_journal_entry],
)


def quickbooks_lookup_instructions(
    run_context: RunContextWrapper[AccountingAgentContext], agent: Agent[AccountingAgentContext]
) -> str:
    return (
        f"{RECOMMENDED_PROMPT_PREFIX}\n"
        "Retrieve QuickBooks data using the get_journal_entry tool."
    )


quickbooks_lookup_agent = Agent[AccountingAgentContext](
    name="QuickBooks Lookup Agent",
    model="gpt-4-turbo",
    handoff_description="Fetch journal entry information from QuickBooks",
    instructions=quickbooks_lookup_instructions,
    tools=[get_journal_entry],
)


triage_agent = Agent[AccountingAgentContext](
    name="Triage Agent",
    model="gpt-4-turbo",
    handoff_description="Route requests to the appropriate accounting agent",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX} "
        "Route the user to the correct agent for parsing documents or interacting with QuickBooks."
    ),
    handoffs=[
        document_parser_agent,
        journal_entry_agent,
        quickbooks_lookup_agent,
    ],
)

# Establish handoff loops
for agent in [document_parser_agent, journal_entry_agent, quickbooks_lookup_agent]:
    agent.handoffs.append(triage_agent)
