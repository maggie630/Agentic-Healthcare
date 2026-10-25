from datetime import datetime, timezone
from patient_store.database import initialize
from patient_store.repositories import Repository
from patient_store.services import PatientStoreService

def add_patient(repo):
    now = datetime.now(timezone.utc).isoformat()
    repo.insert_patient({"patient_id":"p1","external_identifier":"ext-1","first_name":"Mira","last_name":"Example","birth_date":"1990-01-01","administrative_gender":None,"created_at":now,"updated_at":now})

def test_get_and_search_patient(tmp_path):
    db = tmp_path / "test.db"; initialize(db); repo = Repository(db); add_patient(repo)
    service = PatientStoreService(db_path=db)
    assert service.get_patient("ext-1")["patient"]["patient_id"] == "p1"
    result = service.search_patients("Mira")
    assert result["count"] == 1
    assert result["patients"][0]["first_name"] == "Mira"

def test_search_rejects_unbounded_limit(tmp_path):
    db = tmp_path / "test.db"; initialize(db)
    service = PatientStoreService(db_path=db)
    try:
        service.search_patients(limit=1000)
        assert False, "Expected validation failure"
    except Exception:
        pass

def test_search_treats_sql_injection_as_text(tmp_path):
    db = tmp_path / "test.db"; initialize(db); repo = Repository(db); add_patient(repo)
    result = PatientStoreService(db_path=db).search_patients("%' OR 1=1 --")
    assert result["count"] == 0
