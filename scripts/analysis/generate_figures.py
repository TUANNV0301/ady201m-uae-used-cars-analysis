"""Run the complete descriptive analysis and generate figures/tables."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from run_analysis import run  # noqa: E402

if __name__ == "__main__":
    result = run()
    print(f"Analysis finished. Charts: {result.get('charts')}")
