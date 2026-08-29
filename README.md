# AI Customer Support Triage Workflow

An event-driven customer-support automation that receives a support request, uses Google Gemini to classify the issue, validates the AI response, routes tickets that require human attention, and sends a Gmail notification through n8n.

## Overview

This project demonstrates how to combine a browser-based form, webhooks, an LLM, JavaScript transformation logic, conditional routing, and email notifications into one maintainable workflow.

A customer submits a name and support message through the HTML form. The request is sent as JSON to an n8n webhook. Gemini classifies the request by category and urgency and determines whether human review is required. A JavaScript step parses and validates the model output. High-priority or sensitive requests are routed to a human-review branch, which sends a structured Gmail notification.

```text
Customer
   |
   v
HTML support form
   |
   |  HTTP POST / JSON
   v
n8n Webhook
   |
   v
Google Gemini classification
   |
   v
JavaScript JSON parsing and validation
   |
   v
IF: needs_human_review?
   |                         \
   | true                     \ false
   v                           v
Gmail notification             Normal processing
```

## Features

| Capability | Description |
|---|---|
| Form intake | Collects the customer name and support message in a responsive HTML interface. |
| Webhook ingestion | Receives support requests as JSON through an n8n Webhook node. |
| AI classification | Uses Gemini to identify category, urgency, and review requirements. |
| Structured output | Converts the model response into predictable JSON fields. |
| Validation | Checks that categories, urgency values, and Boolean fields are valid. |
| Conditional routing | Sends tickets requiring attention through the human-review branch. |
| Email notification | Sends a structured Gmail alert to the support inbox. |
| Local Python prototype | Includes standalone Python scripts showing the same logic outside n8n. |

## Workflow fields

The webhook expects a JSON request with the following fields:

```json
{
  "id": 1,
  "customer": "Maria Santos",
  "message": "I was charged twice for my subscription this month."
}
```

Gemini is instructed to return:

```json
{
  "category": "Billing",
  "urgency": "High",
  "needs_human_review": true,
  "reason": "The customer reported a duplicate charge and requested a refund."
}
```

Supported categories are `Billing`, `Technical`, `Account`, `Shipping`, and `General`. Supported urgency values are `Low`, `Normal`, and `High`.

## Repository structure

```text
.
├── static/
│   └── test_form.html       # Responsive browser form and webhook client
├── triage.py                # Offline keyword-based prototype
├── triage_ai.py             # Standalone Gemini-based prototype
├── webhook.py               # Flask webhook implementation
├── support_message.json     # Fictional local test input
├── requirements.txt         # Python dependencies
├── .gitignore               # Local secrets and generated files excluded from Git
└── README.md                # Project documentation
```

Generated files such as `human_review.json`, Python bytecode, and the virtual environment are intentionally excluded from version control.

## n8n workflow

The n8n implementation uses the following node sequence:

```text
Webhook → Gemini → Code → IF → Gmail
```

The Webhook node receives the form submission. The Gemini node generates the classification. The Code node parses the JSON text and preserves the original ticket fields. The IF node checks `needs_human_review`. The Gmail node sends an alert when the True branch is selected.

For local testing, use the Webhook node's Test URL while the workflow is listening. For automatic processing, activate the workflow and use the Production URL in the HTML form. Do not use a Test URL for a permanent public form.

## Local Python setup

The Python scripts provide a code-based version of the workflow and are useful for understanding the underlying implementation.

### Windows PowerShell

```powershell
cd C:\Users\Owner\ai-support-triage
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Set the Gemini API key only in your local terminal:

```powershell
$env:GEMINI_API_KEY = Read-Host "Enter your Gemini API key"
```

Run the standalone AI prototype:

```powershell
python triage_ai.py
```

Run the local Flask webhook:

```powershell
$env:WEBHOOK_TOKEN = "use-a-local-development-token"
python webhook.py
```

The local endpoint accepts `POST` requests at `/triage` and listens at `http://127.0.0.1:5000`.

## Testing the HTML form

1. Activate the n8n workflow.
2. Set the n8n Production Webhook URL in `static/test_form.html`.
3. Open the HTML form through a local web server rather than relying on a file opened directly from disk.
4. Submit a fictional customer-support request.
5. Confirm that the n8n execution reaches Gemini, Code, IF, and Gmail.
6. Confirm that the email arrives in the configured support inbox.

Example test data:

```text
Customer name: Maria Santos
Support message: I was charged twice for my subscription this month. Please refund the extra charge.
```

Expected classification:

```text
Category: Billing
Urgency: High
Human review: true
```

## Security notes

Never commit API keys, Gmail credentials, n8n credentials, real production webhook URLs, or private customer data. Keep secrets in environment variables or n8n credential storage. The webhook URL in the HTML should be treated as public if the form is published, so use authentication or a server-side proxy before deploying the form publicly.

The local Flask server is intended for development and learning. A production deployment should use a production WSGI server, HTTPS, authentication, input limits, rate limiting, structured logging, retry handling, duplicate prevention, and a persistent database.

AI output should be treated as untrusted input. Validate the response before routing, sending messages, updating records, or taking other actions. Keep a human approval step for refunds, account changes, and other sensitive operations.

## Limitations and next improvements

This project is a learning and portfolio implementation. It currently uses a JSON file for local output and sends Gmail notifications for the human-review path. A production version should store tickets in a database, preserve an audit trail, support retries and idempotency, monitor model quality, and provide a review interface for support staff.

Potential extensions include Gmail ingestion, Slack notifications, Google Sheets reporting, CRM integration, multilingual classification, attachment extraction, confidence thresholds, and a human correction loop.

## Portfolio summary

Built an AI-powered customer-support triage workflow using n8n, Google Gemini, webhooks, JavaScript, HTML, Python, Flask, and Gmail. The system accepts support requests through a browser form, classifies them by category and urgency, validates structured model output, routes tickets requiring human review, and sends automated email notifications.
