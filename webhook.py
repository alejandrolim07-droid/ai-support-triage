import json
import os
from flask import Flask, jsonify, request
from google import genai

app = Flask(__name__)

api_key = os.environ.get("GEMINI_API_KEY")
webhook_token = os.environ.get("WEBHOOK_TOKEN", "dev-secret")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in this PowerShell window")

client = genai.Client(api_key=api_key)

@app.post("/triage")
def triage_ticket():
    provided_token = request.headers.get("X-Webhook-Token")
    if provided_token != webhook_token:
        return jsonify({"error": "Unauthorized"}), 401

    ticket = request.get_json(silent=True)
    if not ticket:
        return jsonify({"error": "Request body must be JSON"}), 400

    required_fields = {"id", "customer", "message"}
    missing_fields = required_fields - ticket.keys()
    if missing_fields:
        return jsonify({"error": f"Missing fields: {sorted(missing_fields)}"}), 400

    prompt = f"""
You are a customer-support triage assistant.

Customer: {ticket['customer']}
Message: {ticket['message']}

Return only valid JSON with exactly these fields:
category: one of Billing, Technical, Account, Shipping, or General
urgency: one of Low, Normal, or High
needs_human_review: true or false
reason: a short explanation
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
        )

        raw_text = response.text.strip()
        if raw_text.startswith("```"):
            raw_text = raw_text.replace("```json", "", 1).replace("```", "", 1).strip()

        ai_result = json.loads(raw_text)

        valid_categories = {"Billing", "Technical", "Account", "Shipping", "General"}
        valid_urgencies = {"Low", "Normal", "High"}

        if ai_result.get("category") not in valid_categories:
            raise ValueError("Invalid category")
        if ai_result.get("urgency") not in valid_urgencies:
            raise ValueError("Invalid urgency")
        if not isinstance(ai_result.get("needs_human_review"), bool):
            raise ValueError("Invalid human-review value")

        result = {
            "ticket_id": ticket["id"],
            "customer": ticket["customer"],
            "original_message": ticket["message"],
            **ai_result,
        }

        if result["needs_human_review"]:
            with open("human_review.json", "w", encoding="utf-8") as file:
                json.dump(result, file, indent=2)

        return jsonify(result), 200

    except Exception as error:
        return jsonify({"error": "Triage failed", "details": str(error)}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
