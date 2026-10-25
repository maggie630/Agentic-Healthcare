from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from patient_store.database import initialize

if __name__ == "__main__":
    path = initialize()
    print(f"Database initialized successfully: {path}")
