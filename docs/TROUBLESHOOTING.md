# Troubleshooting

- **`ModuleNotFoundError: patient_store`**: run commands from the project root; scripts add `src` to the path. For pytest, use `PYTHONPATH=src` on PowerShell: `$env:PYTHONPATH = "src"`.
- **PowerShell activation blocked**: use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` for the current terminal only, then activate `.venv`.
- **Port 3001 busy**: set `MCP_PORT` in `.env` to an unused local port.
- **Approval disabled**: set a long random `APPROVAL_TOKEN` in `.env` and restart the server. Do not commit it.
- **Synthea CSV missing columns**: expected `Id`, `FIRST`, `LAST`, and `BIRTHDATE`; `GENDER` is optional.
- **Foreign key errors**: ensure patients are seeded before importing child records.
- **Synthea import says skipped**: inspect duplicate IDs and printed row-level errors; the importer does not overwrite an existing patient ID.
- **MCP client cannot connect**: confirm the server process is running, transport is Streamable HTTP, address/path matches the client, and local firewall/proxy settings are not interfering.
