from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4
from pydantic import ValidationError
from .models import RecordDraftInput, PatientSearchInput
from .repositories import Repository

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

class PatientStoreService:
    def __init__(self, db_path=None, approver_token: str = ""):
        self.repo = Repository(db_path)
        self.approver_token = approver_token

    def get_patient(self, identifier: str) -> dict:
        if not identifier or len(identifier) > 120:
            raise ValueError("Provide a valid patient ID or external identifier")
        patient = self.repo.get_patient(identifier.strip())
        if not patient:
            raise ValueError("Patient not found")
        return {"ok": True, "patient": patient}

    def search_patients(self, query: str | None = None, limit: int = 20, offset: int = 0) -> dict:
        args = PatientSearchInput(query=query, limit=limit, offset=offset)
        patients = self.repo.search_patients(args.query, args.limit, args.offset)
        return {"ok": True, "count": len(patients), "limit": args.limit, "offset": args.offset, "patients": patients}

    def save_record_draft(self, **kwargs) -> dict:
        payload = RecordDraftInput(**kwargs).model_dump()
        record = self.repo.save_record_draft(payload, f"rec_{uuid4().hex}", utc_now())
        return {"ok": True, "message": "Record saved as draft; human approval is required before it is approved.", "record": record}

    def approve_record(self, record_id: str, approver_id: str, approval_token: str) -> dict:
        if not self.approver_token:
            raise PermissionError("Approval is disabled: configure APPROVAL_TOKEN first")
        if not approval_token or approval_token != self.approver_token:
            raise PermissionError("Approval authorization failed")
        if not approver_id or len(approver_id.strip()) > 120:
            raise PermissionError("A valid approver identifier is required")
        if not record_id or len(record_id) > 120:
            raise ValueError("A valid record ID is required")
        result = self.repo.approve_record(record_id.strip(), approver_id.strip(), utc_now())
        return {"ok": True, "record": result}
