# PDF Processing and QuickBooks Integration Agents Demo

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![NextJS](https://img.shields.io/badge/Built_with-NextJS-blue)
![OpenAI API](https://img.shields.io/badge/Powered_by-OpenAI_API-orange)

This repository contains a demo of an agentic system built on top of the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/).
The demo showcases agents that can:
- Parse PDF documents (like receipts and invoices) to extract structured information.
- Create journal entries in QuickBooks (simulated) using the extracted data.
- Retrieve data from QuickBooks (simulated) based on user queries.

It is composed of two parts:

1. A Python backend that handles the agent orchestration logic using the Agents SDK. This backend implements the new PDF processing and QuickBooks integration functionalities.

2. A Next.js UI allowing the visualization of the agent orchestration process and providing a chat interface.

![Demo Screenshot](screenshot.jpg)
*(Note: The screenshot might reflect the previous customer service functionality and may need an update to show the new UI interactions if they differ significantly.)*

## How to use

### Setting your OpenAI API key

You can set your OpenAI API key in your environment variables by running the following command in your terminal:

```bash
export OPENAI_API_KEY=your_api_key
```

You can also follow [these instructions](https://platform.openai.com/docs/libraries#create-and-export-an-api-key) to set your OpenAI key at a global level.

Alternatively, you can set the `OPENAI_API_KEY` environment variable in an `.env` file at the root of the `python-backend` folder. You will need to install the `python-dotenv` package to load the environment variables from the `.env` file.

### Install dependencies

Install the dependencies for the backend by running the following commands:

```bash
cd python-backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the UI, you can run:

```bash
cd ui
npm install
```

### Run the app

You can either run the backend independently if you want to use a separate UI, or run both the UI and backend at the same time.

#### Run the backend independently

From the `python-backend` folder, run:

```bash
python -m uvicorn api:app --reload --port 8000
```

The backend will be available at: [http://localhost:8000](http://localhost:8000)

#### Run the UI & backend simultaneously

From the `ui` folder, run:

```bash
npm run dev
```

The frontend will be available at: [http://localhost:3000](http://localhost:3000)

This command will also start the backend.

## Customization

This app is designed for demonstration purposes. Feel free to update the agent prompts, tools, and Pydantic models (for extracted data) to fit your specific PDF processing needs or to integrate with actual financial systems like QuickBooks. You could:
- Implement real PDF parsing using libraries like `PyPDF2` or cloud services.
- Integrate with the actual OpenAI API for text understanding and data structuring.
- Connect to the QuickBooks API (or other accounting software) to make real journal entries and data queries.
- Add new agents for other financial tasks or document types.

The modular structure makes it easy to extend or modify the orchestration logic for your needs.

## Demo Flows

The following flows illustrate the new PDF processing and QuickBooks integration capabilities. Note that PDF parsing and QuickBooks interactions are simulated in the current version.

### Demo Flow #1: Processing a PDF Invoice and Creating a Journal Entry

1.  **User initiates PDF processing:**
    *   User: "I have a PDF invoice I need to process."
    *   The Triage Agent recognizes the intent and hands off to the PDF Processing Agent.

2.  **PDF Processing Agent gathers information:**
    *   PDF Processing Agent: "Okay, I can help with that. Please provide the file path for the PDF invoice."
    *   User: "/path/to/my_invoice.pdf"
    *   PDF Processing Agent: "And is this a 'receipt' or an 'invoice'?"
    *   User: "invoice"
    *   PDF Processing Agent: (Calls `parse_pdf_tool` with `/path/to/my_invoice.pdf` and type "invoice")
    *   PDF Processing Agent: "I've processed the invoice. Here's the extracted data: Invoice Number: INV-2024-001, Customer: Mock Customer Inc., Amount: $1500.00. Does this look correct?"
    *   User: "Yes, that's correct."

3.  **Handoff to QuickBooks Journal Agent for entry creation:**
    *   PDF Processing Agent: "Great. Would you like me to create a journal entry for this in QuickBooks?"
    *   User: "Yes, please."
    *   PDF Processing Agent hands off to QuickBooks Journal Agent (with extracted data in context).
    *   QuickBooks Journal Agent: "I will now create a journal entry for Invoice INV-2024-001 for Mock Customer Inc. with a total of $1500.00."
    *   QuickBooks Journal Agent: (Calls `create_quickbooks_journal_entry_tool` with the structured data)
    *   QuickBooks Journal Agent: "Successfully created Invoice journal entry in QuickBooks. Transaction ID: QB-JE-12345. Is there anything else?"

This flow demonstrates how the system can guide a user through PDF processing, data extraction (simulated), confirmation, and then create a corresponding journal entry in QuickBooks (simulated).

### Demo Flow #2: Retrieving Data from QuickBooks

1.  **User requests data from QuickBooks:**
    *   User: "Can you show me my expenses from last month?"
    *   The Triage Agent recognizes the intent and hands off to the QuickBooks Query Agent.

2.  **QuickBooks Query Agent gathers details and fetches data:**
    *   QuickBooks Query Agent: "I can help with that. To confirm, you're looking for expenses from last month. Are there any specific expense accounts you're interested in, or all expenses?"
    *   User: "All expenses are fine."
    *   QuickBooks Query Agent: (Calls `get_quickbooks_data_tool` with query "all expenses", date\_range "last month")
    *   QuickBooks Query Agent: "Okay, I found the following expenses for last month:
        *   Transaction ID: QB-TRX-001, Date: 2024-01-05, Description: Office Supplies, Amount: -$75.20, Account: Expenses
        *   (other simulated expense entries)...
        Would you like details on any of these, or a different report?"
    *   User: "No, that's all for now, thanks!"

This flow shows how the system can handle user requests for data retrieval from QuickBooks, (simulated) querying the system, and presenting the information back to the user.

## Contributing

You are welcome to open issues or submit PRs to improve this app, however, please note that we may not review all suggestions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
