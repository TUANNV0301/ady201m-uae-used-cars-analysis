"""Clean the source listing CSV and export a separate analysis copy."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from run_analysis import OUT_DIR, load_and_clean  # noqa: E402

if __name__ == "__main__":
    frame, audit = load_and_clean()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUT_DIR / "clean_car_listings.csv"
    frame.to_csv(output, index=False)
    print(f"Saved {len(frame):,} rows to {output}")
    print(audit)
