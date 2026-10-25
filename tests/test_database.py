from patient_store.database import initialize, connect

def test_initializes_tables_and_foreign_keys(tmp_path):
    db = tmp_path / "test.db"
    initialize(db)
    with connect(db) as conn:
        names = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"patients", "records", "appointments"}.issubset(names)
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
