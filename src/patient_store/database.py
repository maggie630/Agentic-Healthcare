from __future__ import annotations
import sqlite3
from pathlib import Path
from .config import database_path

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    external_identifier TEXT NOT NULL UNIQUE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birth_date TEXT,
    administrative_gender TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS records (
    record_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL REFERENCES patients(patient_id) ON DELETE RESTRICT,
    record_type TEXT NOT NULL,
    title TEXT NOT NULL,
    encounter_date TEXT,
    content TEXT NOT NULL,
    confidence REAL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    provenance TEXT NOT NULL DEFAULT 'synthetic_demo',
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','approved')),
    created_by TEXT NOT NULL,
    approved_by TEXT,
    approved_at TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    CHECK ((status = 'draft' AND approved_by IS NULL AND approved_at IS NULL) OR
           (status = 'approved' AND approved_by IS NOT NULL AND approved_at IS NOT NULL))
);
CREATE TABLE IF NOT EXISTS appointments (
    appointment_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL REFERENCES patients(patient_id) ON DELETE RESTRICT,
    scheduled_at TEXT NOT NULL,
    category TEXT,
    reason TEXT,
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled','completed','cancelled','no_show')),
    source TEXT NOT NULL DEFAULT 'synthetic_demo',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_records_patient ON records(patient_id);
CREATE INDEX IF NOT EXISTS idx_records_status ON records(status);
CREATE INDEX IF NOT EXISTS idx_appointments_patient_date ON appointments(patient_id, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_patients_name ON patients(last_name, first_name);
"""

def connect(path: Path | str | None = None) -> sqlite3.Connection:
    db_path = Path(path) if path is not None else database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn

def initialize(path: Path | str | None = None) -> Path:
    db_path = Path(path) if path is not None else database_path()
    with connect(db_path) as conn:
        conn.executescript(SCHEMA_SQL)
    return db_path
