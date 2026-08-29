import json
import os

from google import genai

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in this PowerShell window")

with open("support_message.json", "r", encoding="utf-8") as file:
    ticket = json.load(file)

client = genai.Client(api_key=api_key)

prompt = f"""
You are a customer-support triage assistant.

Read this support ticket:
Customer: {ticket['customer']}
Message: {ticket['message']}

Return only valid JSON with exactly these fields:
category: one of Billing, Technical, Account, Shipping, or General
urgency: one of Low, Normal, or High
needs_human_review: true or false
reason: a short explanation
"""

response = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt,
)

raw_text = response.text.strip()

if raw_text.startswith("```"):
    raw_text = raw_text.replace("```json", "", 1).replace("```", "", 1).strip()

try:
    ai_result = json.loads(raw_text)
except json.JSONDecodeError:
    raise RuntimeError("AI did not return valid JSON:\n" + raw_text)

required_fields = {
    "category",
    "urgency",
    "needs_human_review",
    "reason",
}

missing_fields = required_fields - ai_result.keys()
if missing_fields:
    raise RuntimeError(f"AI response is missing fields: {missing_fields}")

valid_categories = {"Billing", "Technical", "Account", "Shipping", "General"}
valid_urgencies = {"Low", "Normal", "High"}

if ai_result["category"] not in valid_categories:
    raise RuntimeError("Invalid category returned by AI")

if ai_result["urgency"] not in valid_urgencies:
    raise RuntimeError("Invalid urgency returned by AI")

if not isinstance(ai_result["needs_human_review"], bool):
    raise RuntimeError("needs_human_review must be true or false")

final_result = {
    "ticket_id": ticket["id"],
    "customer": ticket["customer"],
    "original_message": ticket["message"],
    **ai_result,
}

if final_result["needs_human_review"]:
    with open("human_review.json", "w", encoding="utf-8") as file:
        json.dump(final_result, file, indent=2)
    print("Ticket routed to human_review.json")
else:
    print("Ticket does not require human review")

print(json.dumps(final_result, indent=2))
