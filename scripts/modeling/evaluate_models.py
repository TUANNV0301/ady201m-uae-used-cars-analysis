"""Evaluate the transparent Year + Mileage linear regression baseline."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from run_analysis import load_and_clean, model_evaluation  # noqa: E402

if __name__ == "__main__":
    frame, _ = load_and_clean()
    result = model_evaluation(frame)
    print(json.dumps(result, ensure_ascii=False, indent=2))
