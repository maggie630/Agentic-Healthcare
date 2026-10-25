# Hospital Database Schema v1 — PROPOSAL

**Status:** Draft for AKAASH's review. Not frozen. Built without access to the original repository; confirm field names and ownership before merging.

## Design

SQLite is used for a local demo. IDs are application-generated strings. Timestamps are ISO 8601 UTC strings. Foreign keys are enabled for every connection. Synthetic-only data is allowed. This is FHIR-inspired only; it is not a FHIR implementation.

## `patients`

| Field | Type | Required | Meaning / constraints | Writer | Reader |
|---|---|---:|---|---|---|
| `patient_id` | TEXT | Yes | Internal primary key | Seed script / approved patient creation workflow | Patient Store, authorized consumers |
| `external_identifier` | TEXT | Yes | Unique synthetic source identifier | Seed script | Patient Store |
| `first_name` | TEXT | Yes | Synthetic given name | Seed script | Patient Store |
| `last_name` | TEXT | Yes | Synthetic family name | Seed script | Patient Store |
| `birth_date` | TEXT | No | Date as provided by source; validate during import | Seed script | Patient Store |
| `administrative_gender` | TEXT | No | Source administrative field, normalized where possible | Seed script | Patient Store |
| `created_at` | TEXT | Yes | UTC creation timestamp | Database workflow | Authorized consumers |
| `updated_at` | TEXT | Yes | UTC update timestamp | Database workflow | Authorized consumers |

## `records`

| Field | Type | Required | Meaning / constraints | Writer | Reader |
|---|---|---:|---|---|---|
| `record_id` | TEXT | Yes | Primary key | Patient Store | Patient Store, authorized consumers |
| `patient_id` | TEXT | Yes | Foreign key to `patients.patient_id` | Patient Store | Patient Store, authorized consumers |
| `record_type` | TEXT | Yes | Type/category label, not a clinical decision | Digitization adapter via Patient Store; demo workflow | Authorized consumers |
| `title` | TEXT | Yes | Short record title | Digitization adapter via Patient Store | Authorized consumers |
| `encounter_date` | TEXT | No | Source encounter date/time | Digitization adapter / approved importer | Authorized consumers |
| `content` | TEXT | Yes | Extracted or synthetic source content; never inferred treatment advice | Digitization adapter via Patient Store | Explicitly authorized consumers only |
| `confidence` | REAL | No | Optional overall confidence, constrained to 0–1; per-field confidence may remain in content until agreed | Digitization adapter | Authorized consumers |
| `provenance` | TEXT | Yes | Source label, defaults to `synthetic_demo` | Seed/import or digitization adapter | Auditors / authorized consumers |
| `status` | TEXT | Yes | `draft` or `approved`; defaults to `draft` | Patient Store only | Patient Store, authorized consumers |
| `created_by` | TEXT | Yes | Calling workflow/agent identity label; validate against real identity in production | Patient Store | Auditors / authorized consumers |
| `approved_by` | TEXT | No | Human approver identifier, required if approved | Approval workflow | Auditors / authorized consumers |
| `approved_at` | TEXT | No | UTC approval timestamp, required if approved | Approval workflow | Auditors / authorized consumers |
| `created_at` | TEXT | Yes | UTC creation timestamp | Patient Store | Authorized consumers |
| `updated_at` | TEXT | Yes | UTC update timestamp | Patient Store | Authorized consumers |

## `appointments`

| Field | Type | Required | Meaning / constraints | Writer | Reader |
|---|---|---:|---|---|---|
| `appointment_id` | TEXT | Yes | Primary key | Synthea adapter / approved workflow | Patient Store |
| `patient_id` | TEXT | Yes | Foreign key to patient | Synthea adapter / approved workflow | Patient Store |
| `scheduled_at` | TEXT | Yes | Scheduled/encounter timestamp | Synthea adapter only when mapping is meaningful | Authorized consumers |
| `category` | TEXT | No | Source category | Importer | Authorized consumers |
| `reason` | TEXT | No | Source reason, no inferred diagnosis | Importer / approved workflow | Authorized consumers |
| `status` | TEXT | Yes | `scheduled`, `completed`, `cancelled`, or `no_show` | Importer / approved workflow | Authorized consumers |
| `source` | TEXT | Yes | Provenance label; defaults to `synthetic_demo` | Importer | Auditors / authorized consumers |
| `created_at` | TEXT | Yes | UTC creation timestamp | Importer / workflow | Authorized consumers |
| `updated_at` | TEXT | Yes | UTC update timestamp | Importer / workflow | Authorized consumers |

## Relationships and lifecycle

- `patients` 1 → many `records`.
- `patients` 1 → many `appointments`.
- A record is inserted as `draft`. Only the approval workflow can transition it to `approved`; the transition records approver and timestamp. Re-approval is rejected.
- Patient deletion is restricted when records or appointments reference the patient.
- Search and retrieval return only the fields explicitly selected by the tool.

## Lane ownership assumptions

- MEGHANA: schema proposal, database initialization, seed adapter, patient_store interface and approval gate.
- CHARAN: image-to-structured-JSON extraction and per-field confidence contract; sends a draft through Patient Store, not direct SQL.
- VARSHINI: policy-only retrieval; no patient-data access.
- AKAASH: confirms schema, model/configuration decisions, MCP registration, orchestrator integration and cross-lane changes.

## Open questions for AKAASH

1. Is SQLite acceptable for the first integration, or does the main app require another database?
2. What exact field names and data types should align with CHARAN's Pydantic extraction contract?
3. Should per-field confidence be a dedicated JSON column, a structured content object, or a normalized child table?
4. Which MCP transport and client registration does the orchestrator support?
5. What authenticated human identity/role mechanism should replace the local demo approval token?
6. Should Synthea encounters map into `appointments`, `records`, or both, and which source statuses are required?
7. What audit retention and record versioning requirements exist in the main app?
