from datetime import datetime, timezone
import pytest
from patient_store.database import initialize
from patient_store.repositories import Repository
from patient_store.services import PatientStoreService

def setup(tmp_path):
    db = tmp_path / "test.db"; initialize(db); repo = Repository(db)
    now = datetime.now(timezone.utc).isoformat()
    repo.insert_patient({"patient_id":"p1","external_identifier":"ext-1","first_name":"Demo","last_name":"Patient","birth_date":None,"administrative_gender":None,"created_at":now,"updated_at":now})
    return db

def test_draft_requires_human_approval(tmp_path):
    db = setup(tmp_path); service = PatientStoreService(db_path=db, approver_token="secret")
    result = service.save_record_draft(patient_id="p1", record_type="admin_note", title="Synthetic note", content="Synthetic content only", created_by="test-agent", confidence=0.8)
    record = result["record"]
    assert record["status"] == "draft"
    with pytest.raises(PermissionError):
        service.approve_record(record["record_id"], "reviewer", "wrong")
    approved = service.approve_record(record["record_id"], "reviewer", "secret")
    assert approved["record"]["status"] == "approved"
    assert approved["record"]["approved_by"] == "reviewer"
    with pytest.raises(ValueError):
        service.approve_record(record["record_id"], "reviewer", "secret")

def test_missing_patient_rejected(tmp_path):
    db = setup(tmp_path); service = PatientStoreService(db_path=db)
    with pytest.raises(ValueError, match="Patient not found"):
        service.save_record_draft(patient_id="missing", record_type="note", title="x", content="y", created_by="test")

def test_confidence_bounds(tmp_path):
    db = setup(tmp_path); service = PatientStoreService(db_path=db)
    with pytest.raises(Exception):
        service.save_record_draft(patient_id="p1", record_type="note", title="x", content="y", created_by="test", confidence=1.5)
