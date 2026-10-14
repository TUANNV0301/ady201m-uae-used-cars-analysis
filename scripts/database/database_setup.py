"""Build the normalized SQLite database from the source CSV."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from run_analysis import DB_PATH, create_database, load_and_clean  # noqa: E402

if __name__ == "__main__":
    frame, _ = load_and_clean()
    create_database(frame)
    print(f"Created {DB_PATH} with {len(frame):,} listings")
