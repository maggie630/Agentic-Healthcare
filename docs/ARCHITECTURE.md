# Architecture

```text
Synthetic Synthea CSV / demo fixtures
                 |
                 v
        scripts/seed_db.py
                 |
                 v
           SQLite database
      patients / records / appointments
                 ^
                 |
     PatientStoreService + Repository
                 ^
                 |
      MCP server (Streamable HTTP)
        get_patient / search_patients
        save_record_draft / approve_record
```

The service/repository separation keeps business rules testable without starting an MCP server. Database calls use parameterized SQL and foreign-key enforcement. The default server binds to loopback (`127.0.0.1`) and port `3001`.

This standalone module does not contain the main conversational orchestrator or other agent implementations because the private repository was not available.
