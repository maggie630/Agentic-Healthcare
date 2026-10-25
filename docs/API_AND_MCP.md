# MCP tools

## `get_patient(identifier)`
Accepts internal `patient_id` or unique `external_identifier`. Returns the selected patient fields or a structured error.

## `search_patients(query=None, limit=20, offset=0)`
Searches internal/external IDs and names. `limit` is 1–100; `offset` is non-negative. Results are ordered by family and given name.

## `save_record_draft(patient_id, record_type, title, content, created_by, encounter_date=None, confidence=None, provenance='synthetic_demo')`
Validates input and patient existence, inserts a record with `draft` status, and returns its ID/status. It cannot approve records.

## `approve_record(record_id, approver_id, approval_token)`
Requires the token configured by `APPROVAL_TOKEN`, a named approver, and an existing draft. Writes status, approver and timestamp atomically. The token is a local demo control only, not production-grade authentication.

## Transport

The server uses the official Python MCP SDK's Streamable HTTP transport. Default local address is `http://127.0.0.1:3001/mcp`; verify the path/transport expected by the chosen MCP client and pinned SDK. Do not expose the unauthenticated development endpoint to a public network.
