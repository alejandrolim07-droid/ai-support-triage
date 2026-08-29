import json

with open("support_message.json", "r", encoding="utf-8") as file:
    ticket = json.load(file)

message = ticket["message"].lower()

if any(word in message for word in ["charged", "charge", "refund", "payment"]):
    category = "Billing"
else:
    category = "General"

if any(word in message for word in ["twice", "charged twice", "urgent", "cannot access"]):
    urgency = "High"
else:
    urgency = "Normal"

needs_human_review = category == "Billing" or urgency == "High"

result = {
    "ticket_id": ticket["id"],
    "customer": ticket["customer"],
    "category": category,
    "urgency": urgency,
    "needs_human_review": needs_human_review,
    "original_message": ticket["message"]
}

print(json.dumps(result, indent=2))
