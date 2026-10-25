from __future__ import annotations
import sqlite3
from typing import Any
from .database import connect

class Repository:
    def __init__(self, db_path=None):
        self.db_path = db_path

    def get_patient(self, identifier: str) -> dict[str, Any] | None:
        with connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT patient_id, external_identifier, first_name, last_name, birth_date, administrative_gender "
                "FROM patients WHERE patient_id = ? OR external_identifier = ? LIMIT 1",
                (identifier, identifier),
            ).fetchone()
            return dict(row) if row else None

    def search_patients(self, query: str | None, limit: int, offset: int) -> list[dict[str, Any]]:
        sql = ("SELECT patient_id, external_identifier, first_name, last_name, birth_date, administrative_gender "
               "FROM patients")
        params: list[Any] = []
        if query and query.strip():
            needle = f"%{query.strip()}%"
            sql += " WHERE patient_id LIKE ? OR external_identifier LIKE ? OR first_name LIKE ? OR last_name LIKE ?"
            params.extend([needle] * 4)
        sql += " ORDER BY last_name, first_name LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        with connect(self.db_path) as conn:
            return [dict(row) for row in conn.execute(sql, params).fetchall()]

    def save_record_draft(self, payload: dict[str, Any], record_id: str, now: str) -> dict[str, Any]:
        with connect(self.db_path) as conn:
            patient = conn.execute("SELECT 1 FROM patients WHERE patient_id = ?", (payload["patient_id"],)).fetchone()
            if not patient:
                raise ValueError("Patient not found")
            conn.execute(
                "INSERT INTO records(record_id, patient_id, record_type, title, encounter_date, content, confidence, "
                "provenance, status, created_by, approved_by, approved_at, created_at, updated_at) "
                "VALUES(?,?,?,?,?,?,?,?,'draft',?,NULL,NULL,?,?)",
                (record_id, payload["patient_id"], payload["record_type"], payload["title"], payload.get("encounter_date"),
                 payload["content"], payload.get("confidence"), payload.get("provenance", "synthetic_demo"),
                 payload["created_by"], now, now),
            )
            row = conn.execute("SELECT record_id, patient_id, record_type, title, status, created_by, created_at FROM records WHERE record_id = ?", (record_id,)).fetchone()
            return dict(row)

    def approve_record(self, record_id: str, approver_id: str, now: str) -> dict[str, Any]:
        with connect(self.db_path) as conn:
            row = conn.execute("SELECT status FROM records WHERE record_id = ?", (record_id,)).fetchone()
            if not row:
                raise ValueError("Record not found")
            if row["status"] != "draft":
                raise ValueError("Only draft records can be approved")
            cur = conn.execute(
                "UPDATE records SET status='approved', approved_by=?, approved_at=?, updated_at=? "
                "WHERE record_id=? AND status='draft'",
                (approver_id, now, now, record_id),
            )
            if cur.rowcount != 1:
                raise ValueError("Record state changed; reload and retry")
            result = conn.execute("SELECT record_id, patient_id, status, created_by, approved_by, approved_at FROM records WHERE record_id=?", (record_id,)).fetchone()
            return dict(result)

    def insert_patient(self, patient: dict[str, Any]) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO patients(patient_id, external_identifier, first_name, last_name, birth_date, administrative_gender, created_at, updated_at) "
                "VALUES(?,?,?,?,?,?,?,?) ON CONFLICT(patient_id) DO NOTHING",
                (patient["patient_id"], patient["external_identifier"], patient["first_name"], patient["last_name"],
                 patient.get("birth_date"), patient.get("administrative_gender"), patient["created_at"], patient["updated_at"]),
            )
