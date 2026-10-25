from __future__ import annotations
import argparse, csv, sys
from pathlib import Path
from datetime import datetime, timezone
from uuid import uuid4
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from patient_store.database import initialize, connect
from patient_store.repositories import Repository

NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
DEMO_PATIENTS = [
    {"patient_id":"syn-pat-001","external_identifier":"SYNTH-0001","first_name":"Aarav","last_name":"Sample","birth_date":"1998-04-12","administrative_gender":"unknown","created_at":NOW,"updated_at":NOW},
    {"patient_id":"syn-pat-002","external_identifier":"SYNTH-0002","first_name":"Mira","last_name":"Example","birth_date":"1987-09-03","administrative_gender":"unknown","created_at":NOW,"updated_at":NOW},
    {"patient_id":"syn-pat-003","external_identifier":"SYNTH-0003","first_name":"Kiran","last_name":"Demo","birth_date":"2001-01-21","administrative_gender":"unknown","created_at":NOW,"updated_at":NOW},
]

def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        yield reader.fieldnames, from_reader(reader)

def from_reader(reader):
    # Materialize one file at a time; Synthea cohorts are expected to be small for this demo.
    return list(reader)

def seed_demo(repo: Repository) -> int:
    count = 0
    for p in DEMO_PATIENTS:
        try:
            repo.insert_patient(p); count += 1
        except Exception as exc:
            print(f"Skipped demo row {p['patient_id']}: {exc}")
    return count

def seed_synthea(data_dir: Path, max_patients: int = 200) -> dict[str, int]:
    patients_path = data_dir / "patients.csv"
    if not patients_path.exists():
        raise FileNotFoundError(f"Missing {patients_path}; provide Synthea output/csv directory")
    with patients_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required = {"Id", "FIRST", "LAST", "BIRTHDATE"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError(f"Synthea patients.csv must include: {', '.join(sorted(required))}")
        patient_rows = list(reader)[:max_patients]
    allowed_ids = {str(r.get("Id", "")).strip() for r in patient_rows if r.get("Id")}
    repo = Repository()
    stats = {"patients_processed": 0, "appointments_processed": 0, "chart_context_records_processed": 0, "skipped": 0}
    with connect() as conn:
        for row in patient_rows:
            source_id = (row.get("Id") or "").strip()
            if not source_id:
                stats["skipped"] += 1; continue
            patient = {"patient_id": f"syn-{source_id}", "external_identifier": f"SYNTHEA-{source_id}",
                "first_name": (row.get("FIRST") or "Synthetic").strip() or "Synthetic",
                "last_name": (row.get("LAST") or "Patient").strip() or "Patient",
                "birth_date": (row.get("BIRTHDATE") or "").strip() or None,
                "administrative_gender": (row.get("GENDER") or "").strip().lower() or None,
                "created_at": NOW, "updated_at": NOW}
            try:
                repo.insert_patient(patient); stats["patients_processed"] += 1
            except Exception as exc:
                stats["skipped"] += 1; print(f"Skipped patient {source_id}: {exc}")
        # Map Synthea encounters into appointments only when the patient is in the selected cohort.
        encounters_path = data_dir / "encounters.csv"
        if encounters_path.exists():
            with encounters_path.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                if reader.fieldnames and {"Id", "START", "PATIENT"}.issubset(set(reader.fieldnames)):
                    for row in reader:
                        source_patient = (row.get("PATIENT") or "").strip()
                        if source_patient not in allowed_ids: continue
                        start = (row.get("START") or "").strip()
                        if not start: stats["skipped"] += 1; continue
                        status = "completed" if (row.get("STOP") or "").strip() else "scheduled"
                        try:
                            conn.execute("INSERT OR IGNORE INTO appointments(appointment_id,patient_id,scheduled_at,category,reason,status,source,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?)",
                                (f"syn-appt-{row.get('Id')}", f"syn-{source_patient}", start, row.get("ENCOUNTERCLASS"), row.get("DESCRIPTION"), status, "synthea_csv", NOW, NOW))
                            stats["appointments_processed"] += 1
                        except Exception as exc:
                            stats["skipped"] += 1; print(f"Skipped encounter: {exc}")
        # Store synthetic conditions and medication rows as unapproved chart-context drafts, not clinical decisions.
        for filename, label in (("conditions.csv", "condition_context"), ("medications.csv", "medication_context")):
            path = data_dir / filename
            if not path.exists(): continue
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                if not reader.fieldnames or not {"PATIENT", "DESCRIPTION"}.issubset(set(reader.fieldnames)):
                    print(f"Skipping {filename}: expected PATIENT and DESCRIPTION columns"); continue
                for row in reader:
                    source_patient = (row.get("PATIENT") or "").strip()
                    if source_patient not in allowed_ids: continue
                    description = (row.get("DESCRIPTION") or "").strip()
                    if not description: continue
                    source_row_id = row.get("Id") or uuid4().hex
                    content = f"Synthetic source chart context only. Category: {label}. Description: {description}."
                    try:
                        conn.execute("INSERT OR IGNORE INTO records(record_id,patient_id,record_type,title,encounter_date,content,confidence,provenance,status,created_by,approved_by,approved_at,created_at,updated_at) VALUES(?,?,?,?,?,?,NULL,'synthea_csv','draft','synthea_import',NULL,NULL,?,?)",
                            (f"syn-rec-{label}-{source_row_id}", f"syn-{source_patient}", label, label.replace('_',' ').title(), row.get("START"), content, NOW, NOW))
                        stats["chart_context_records_processed"] += 1
                    except Exception as exc:
                        stats["skipped"] += 1; print(f"Skipped chart context row: {exc}")
    return stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed synthetic-only demo data or a MITRE Synthea CSV cohort.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true", help="Load clearly synthetic built-in demo patients")
    group.add_argument("--synthea-dir", type=Path, help="Path to Synthea output/csv directory")
    parser.add_argument("--max-patients", type=int, default=200, help="Maximum patients to import from Synthea (1-2000)")
    args = parser.parse_args()
    if not 1 <= args.max_patients <= 2000:
        parser.error("--max-patients must be between 1 and 2000")
    initialize()
    if args.demo:
        count = seed_demo(Repository())
        print(f"Demo seeding finished. Rows processed: {count}; synthetic fixtures only.")
    else:
        stats = seed_synthea(args.synthea_dir, args.max_patients)
        print("Synthea import finished:")
        for key, value in stats.items(): print(f"  {key}: {value}")
        print("Conditions/medications are stored only as draft synthetic chart context; no clinical decisions are made.")
