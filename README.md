# Accounting Agents Demo

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![NextJS](https://img.shields.io/badge/Built_with-NextJS-blue)
![OpenAI API](https://img.shields.io/badge/Powered_by-OpenAI_API-orange)

This repository contains a demo showcasing how OpenAI Agents can parse receipts and interact with QuickBooks.
It is composed of two parts:

1. A python backend that defines agents for document parsing and QuickBooks journal entry creation.

2. A Next.js UI allowing the visualization of the agent orchestration process and providing a chat interface.

![Demo Screenshot](screenshot.jpg)

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

The agents provided here are basic examples. Feel free to tweak the prompts or extend the tools to support your own accounting workflows.

## Demo Flows

### Demo flow

1. **Parse a receipt PDF**
   - User: "Parse https://example.com/receipt.pdf"
   - The Triage Agent routes the request to the Document Parser Agent which downloads the PDF and extracts vendor, date, and total using the OpenAI API.

2. **Create a journal entry**
   - After parsing, ask the system to create a journal entry.
   - The Journal Entry Agent sends the extracted data to QuickBooks (stubbed in this demo) and returns an entry id.

3. **Retrieve an entry**
   - User: "Look up entry QB-ACM-001"
   - The QuickBooks Lookup Agent fetches the information from QuickBooks and returns the stored details.

## Contributing

You are welcome to open issues or submit PRs to improve this app, however, please note that we may not review all suggestions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
