# OmniServe n8n Workflows

This folder contains importable n8n workflows for the OmniServe AI customer-operations system.

## Included workflow

### `omniserve-customer-intake.json`

A working customer-intake flow:

1. **Customer Intake Webhook** receives a POST request.
2. **Validate and Route Case** validates the request, creates a case number, selects a department, assigns a priority, and determines whether human review is required.
3. **Save Case to Supabase** calls the `create_customer_case` PostgreSQL RPC.
4. **Return Case Response** returns the routed case and Supabase result.

## Import into n8n

1. Download `omniserve-customer-intake.json`.
2. In n8n, open **Overview**.
3. Select **Import from File**.
4. Open the **Save Case to Supabase** node.
5. Select your Supabase service-role Header Auth credential.
6. Test the workflow before activating it.

## Required Supabase credential

Create an n8n **Header Auth** credential:

- **Name:** `apikey`
- **Value:** your Supabase secret/service-role key
- **Allowed HTTP Request Domain:** `https://rjudsonxkaohbqhxmvvw.supabase.co`

The workflow does not contain or expose an API key.

## Test request

```powershell
$body = @{
  name = "Alejandro"
  email = "test@example.com"
  message = "My invoice has an incorrect charge and I need help"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:5678/webhook-test/omniserve-customer-intake" `
  -Method POST `
  -ContentType "application/json" `
  -Body $body
```

Use the production URL `/webhook/omniserve-customer-intake` only after activating the workflow.

## Security

- Never commit Supabase secret/service-role keys.
- Keep the workflow inactive until the credential and Supabase RPC are tested.
- Use the Supabase publishable key only in frontend applications; server-side n8n operations that call the protected RPC require the service-role credential.
