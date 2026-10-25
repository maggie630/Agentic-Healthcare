from patient_store.database import initialize, connect

def test_appointment_foreign_key_and_status(tmp_path):
    db = tmp_path / "test.db"; initialize(db)
    with connect(db) as conn:
        try:
            conn.execute("INSERT INTO appointments(appointment_id,patient_id,scheduled_at,created_at,updated_at) VALUES('a1','missing','2026-01-01','now','now')")
            assert False, "Expected foreign key violation"
        except Exception:
            conn.rollback()
        try:
            conn.execute("INSERT INTO appointments(appointment_id,patient_id,scheduled_at,status,created_at,updated_at) VALUES('a2','missing','2026-01-01','invalid','now','now')")
            assert False, "Expected constraint violation"
        except Exception:
            conn.rollback()
