from __future__ import annotations as _annotations

import random
from pydantic import BaseModel
import string

from agents import (
    Agent,
    RunContextWrapper,
    Runner,
    TResponseInputItem,
    function_tool,
    handoff,
    GuardrailFunctionOutput,
    input_guardrail,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# =========================
# CONTEXT
# =========================

class ReceiptItem(BaseModel):
    """Represents an item listed on a receipt."""
    description: str | None = None
    amount: float | None = None
    quantity: int | None = None # Optional, as not all receipts have quantity per item

class InvoiceLineItem(BaseModel):
    """Represents a line item on an invoice."""
    description: str | None = None
    quantity: float | None = None # Using float for quantity to be flexible (e.g., hours)
    unit_price: float | None = None
    total: float | None = None

class ReceiptData(BaseModel):
    """Structured data extracted from a receipt PDF."""
    merchant_name: str | None = None
    transaction_date: str | None = None # Using str for simplicity, could be date/datetime
    total_amount: float | None = None
    items: list[ReceiptItem] | None = None # Was list[dict]
    currency: str | None = "USD"

class InvoiceData(BaseModel):
    """Structured data extracted from an invoice PDF."""
    invoice_number: str | None = None
    customer_name: str | None = None
    invoice_date: str | None = None # Using str for simplicity
    due_date: str | None = None # Using str for simplicity
    total_amount: float | None = None
    line_items: list[InvoiceLineItem] | None = None # Was list[dict]
    currency: str | None = "USD"

class QuickbooksAgentContext(BaseModel):
    """Context for QuickBooks integration agents."""
    user_query: str | None = None
    uploaded_pdf_path: str | None = None # Path to the uploaded PDF
    extracted_data: ReceiptData | InvoiceData | None = None # Holds data from PDF
    quickbooks_transaction_id: str | None = None # ID from QuickBooks after posting
    quickbooks_query_results: list[dict] | None = None # Results from QB query

def create_initial_context() -> QuickbooksAgentContext:
    """
    Factory for a new QuickbooksAgentContext.
    """
    return QuickbooksAgentContext()

# =========================
# TOOLS
# =========================

@function_tool(
    name_override="parse_pdf_tool",
    description_override="Parses a PDF file (e.g., receipt, invoice) and extracts structured data."
)
async def parse_pdf_tool(
    context: RunContextWrapper[QuickbooksAgentContext], pdf_file_path: str, document_type: str = "receipt" # "receipt" or "invoice"
) -> ReceiptData | InvoiceData | str:
    """
    Simulates parsing a PDF and extracting structured data using OpenAI.
    In a real scenario, this would involve API calls to OpenAI for text extraction and structuring.
    """
    print(f"Simulating PDF parsing for: {pdf_file_path} (type: {document_type})")
    context.context.uploaded_pdf_path = pdf_file_path

    # Simulate OpenAI PDF text extraction and structuring
    # For now, return mock data based on document_type
    if document_type == "receipt":
        mock_data = ReceiptData(
            merchant_name="Mock Merchant",
            transaction_date="2024-01-15",
            total_amount=125.50,
            items=[
                ReceiptItem(description="Item A", amount=75.00, quantity=1),
                ReceiptItem(description="Item B", amount=50.50, quantity=2)
            ]
        )
        context.context.extracted_data = mock_data
        return mock_data
    elif document_type == "invoice":
        mock_data = InvoiceData(
            invoice_number="INV-2024-001",
            customer_name="Mock Customer Inc.",
            invoice_date="2024-01-10",
            due_date="2024-02-10",
            total_amount=1500.00,
            line_items=[
                InvoiceLineItem(description="Consulting Services", quantity=10, unit_price=150.00, total=1500.00)
            ]
        )
        context.context.extracted_data = mock_data
        return mock_data
    else:
        return f"Unsupported document type: {document_type}. Please specify 'receipt' or 'invoice'."

@function_tool(
    name_override="create_quickbooks_journal_entry_tool",
    description_override="Creates a journal entry in QuickBooks using the provided structured data."
)
async def create_quickbooks_journal_entry_tool(
    context: RunContextWrapper[QuickbooksAgentContext], data: ReceiptData | InvoiceData
) -> str:
    """
    Simulates creating a journal entry in QuickBooks.
    In a real scenario, this would involve API calls to the QuickBooks API.
    """
    print(f"Simulating QuickBooks journal entry creation with data: {data.model_dump_json(indent=2)}")

    entry_type = "Unknown"
    details = ""

    if isinstance(data, ReceiptData):
        entry_type = "Receipt"
        details = f"Merchant: {data.merchant_name}, Amount: {data.total_amount}"
    elif isinstance(data, InvoiceData):
        entry_type = "Invoice"
        details = f"Invoice #: {data.invoice_number}, Customer: {data.customer_name}, Amount: {data.total_amount}"
    else:
        # This case should ideally not be reached if type checking is correct upstream
        # or if the Pydantic model validation for the union works as expected.
        entry_type = "Generic"
        # Try to get total_amount if available, otherwise it will be None.
        total_amount = getattr(data, 'total_amount', None)
        details = f"Amount: {total_amount}" if total_amount is not None else "No amount specified"

    # Simulate API call and get a transaction ID
    simulated_transaction_id = f"QB-JE-{random.randint(10000, 99999)}"
    context.context.quickbooks_transaction_id = simulated_transaction_id

    return f"Successfully created {entry_type} journal entry in QuickBooks. Transaction ID: {simulated_transaction_id}. Details: {details}"

@function_tool(
    name_override="get_quickbooks_data_tool",
    description_override="Retrieves data (e.g., reports, transaction lists) from QuickBooks based on a query."
)
async def get_quickbooks_data_tool(
    context: RunContextWrapper[QuickbooksAgentContext], query: str, date_range: str | None = None, account_type: str | None = None
) -> list[dict] | str:
    """
    Simulates retrieving data from QuickBooks.
    In a real scenario, this would involve API calls to the QuickBooks API with query parameters.
    """
    print(f"Simulating QuickBooks data retrieval for query: '{query}', Date Range: {date_range}, Account Type: {account_type}")

    # Simulate API call and return mock data
    mock_results = [
        {"transaction_id": "QB-TRX-001", "date": "2024-01-05", "description": "Office Supplies", "amount": -75.20, "account": "Expenses"},
        {"transaction_id": "QB-TRX-002", "date": "2024-01-08", "description": "Client Payment - Project X", "amount": 1200.00, "account": "Income"},
    ]
    if "expense" in query.lower():
        mock_results = [res for res in mock_results if res["amount"] < 0]
    elif "income" in query.lower() or "revenue" in query.lower():
        mock_results = [res for res in mock_results if res["amount"] > 0]

    context.context.quickbooks_query_results = mock_results
    if not mock_results:
        return f"No data found in QuickBooks for query: '{query}' with specified criteria."
    return mock_results

# =========================
# HOOKS
# =========================
# (Old airline-specific hooks like on_seat_booking_handoff and on_cancellation_handoff are removed)
# (Old airline-specific guardrails like relevance_guardrail and jailbreak_guardrail are removed)

# =========================
# AGENTS
# =========================

pdf_processing_agent = Agent[QuickbooksAgentContext](
    name="PDF Processing Agent",
    model="gpt-4.1", # Or your preferred model
    handoff_description="Processes PDF documents like receipts and invoices to extract structured data.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a PDF Processing Agent. Your goal is to help the user extract structured information from PDF documents.
    1. Ask the user to provide a path to the PDF file they want to process.
    2. Ask the user to specify the document type (e.g., 'receipt', 'invoice').
    3. Use the 'parse_pdf_tool' to extract data from the PDF.
    4. Present the extracted data to the user for confirmation.
    5. If the user confirms, you can suggest handing off to the QuickBooks Journal Agent to record this data, or await further instructions.
    If the user asks for something else, consider handing off to the Triage Agent.
    """,
    tools=[parse_pdf_tool],
    # input_guardrails=[...], # Add specific guardrails if needed
)

quickbooks_journal_agent = Agent[QuickbooksAgentContext](
    name="QuickBooks Journal Agent",
    model="gpt-4.1",
    handoff_description="Creates journal entries in QuickBooks from structured data.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a QuickBooks Journal Agent. You help users create journal entries in QuickBooks.
    1. You typically receive structured data (like from a receipt or invoice) from another agent (e.g., PDF Processing Agent). This data should be present in `context.context.extracted_data`.
    2. First, check if `context.context.extracted_data` actually contains data (i.e., it's not None).
    3. If `context.context.extracted_data` is None or does not seem to contain valid receipt or invoice information, inform the user that there is no data available to create a journal entry and suggest they process a PDF first or handoff to the Triage Agent. Do not attempt to call the tool without valid data.
    4. If data is available in `context.context.extracted_data`, confirm with the user that they want to create a journal entry using this specific data. You can summarize key fields from the data for confirmation.
    5. If the user confirms, use the 'create_quickbooks_journal_entry_tool'. You MUST pass the entire `context.context.extracted_data` object (which will be either a ReceiptData or InvoiceData model instance) as the 'data' argument to this tool.
    6. After the tool call, inform the user of the outcome (e.g., success and transaction ID, or any errors reported by the tool).
    If the user asks for something unrelated to creating a journal entry from the current `extracted_data`, consider handing off to the Triage Agent.
    """,
    tools=[create_quickbooks_journal_entry_tool],
    # input_guardrails=[...],
)

quickbooks_query_agent = Agent[QuickbooksAgentContext](
    name="QuickBooks Query Agent",
    model="gpt-4.1",
    handoff_description="Retrieves information and data from QuickBooks.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a QuickBooks Query Agent. You help users retrieve data and reports from QuickBooks.
    1. Ask the user what information they are looking for from QuickBooks (e.g., "show me all expenses last month", "find invoice #123").
    2. Clarify any necessary parameters for the query, such as date ranges, account types, specific transaction IDs, etc.
    3. Use the 'get_quickbooks_data_tool' with the formulated query and parameters.
    4. Present the retrieved data to the user.
    If the user asks for something else, consider handing off to the Triage Agent.
    """,
    tools=[get_quickbooks_data_tool],
    # input_guardrails=[...],
)

# Triage Agent will be updated in the next step.
# For now, define a basic one to avoid errors and allow other agents to handoff to it.
triage_agent = Agent[QuickbooksAgentContext](
    name="Triage Agent",
    model="gpt-4.1", # Or your preferred model
    handoff_description="Routes user requests to the appropriate QuickBooks agent (PDF, Journal, Query).",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    You are a Triage Agent for QuickBooks related tasks.
    Your primary role is to understand the user's need and hand them off to the correct specialist agent:
    - For processing PDFs (receipts, invoices): handoff to "PDF Processing Agent".
    - For creating journal entries in QuickBooks: handoff to "QuickBooks Journal Agent".
    - For querying data or reports from QuickBooks: handoff to "QuickBooks Query Agent".
    If the user's request is unclear, ask for clarification.
    """,
    handoffs=[pdf_processing_agent, quickbooks_journal_agent, quickbooks_query_agent],
    # input_guardrails=[...], # Consider general guardrails
)

# Setup basic handoff relationships (can be expanded)
# Specialist agents can hand back to Triage if the query is outside their scope.
pdf_processing_agent.handoffs.append(triage_agent)
pdf_processing_agent.handoffs.append(quickbooks_journal_agent) # Direct handoff after successful parse
quickbooks_journal_agent.handoffs.append(triage_agent)
quickbooks_query_agent.handoffs.append(triage_agent)


# These are no longer needed as they were airline specific.
# faq_agent = DummyAgent(name="FAQ Agent", model="gpt-4.1")
# seat_booking_agent = DummyAgent(name="Seat Booking Agent", model="gpt-4.1")
# flight_status_agent = DummyAgent(name="Flight Status Agent", model="gpt-4.1")
# cancellation_agent = DummyAgent(name="Cancellation Agent", model="gpt-4.1")
