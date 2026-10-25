import pytest
from patient_store.services import PatientStoreService

def test_approval_disabled_without_token(tmp_path):
    service = PatientStoreService(db_path=tmp_path / "none.db", approver_token="")
    with pytest.raises(PermissionError, match="Approval is disabled"):
        service.approve_record("rec1", "reviewer", "anything")
