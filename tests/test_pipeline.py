"""Pipeline checks runnable with pytest or `python -m unittest discover -s tests`."""
import math
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "analysis"))
from run_analysis import (  # noqa: E402
    DB_PATH,
    FIGURES_DIR,
    create_database,
    load_and_clean,
    model_evaluation,
)


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frame, cls.audit = load_and_clean()

    def test_source_rows_and_cleaning(self):
        self.assertEqual(len(self.frame), 10_000)
        self.assertEqual(len(self.audit["columns"]), 12)
        self.assertEqual(self.audit["cylinders_missing_normalized"], 155)
        self.assertEqual(self.audit["duplicate_rows_removed"], 0)
        self.assertTrue(self.frame["Location"].str.strip().eq(self.frame["Location"]).all())

    def test_database_relations_and_integrity(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temp:
            path = Path(temp) / "test.sqlite"
            create_database(self.frame, path)
            conn = sqlite3.connect(path)
            try:
                self.assertEqual(conn.execute("SELECT COUNT(*) FROM car_listing").fetchone()[0], 10_000)
                self.assertEqual(conn.execute("PRAGMA integrity_check").fetchone()[0], "ok")
                self.assertEqual(conn.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertGreater(conn.execute("SELECT COUNT(*) FROM make").fetchone()[0], 1)
            finally:
                conn.close()

    def test_regression_split_and_metrics(self):
        result = model_evaluation(self.frame)
        self.assertEqual(result["n_train"], 8_000)
        self.assertEqual(result["n_test"], 2_000)
        for model in ["baseline_train_median", "linear_regression"]:
            self.assertTrue(math.isfinite(result[model]["MAE_AED"]))
            self.assertTrue(math.isfinite(result[model]["RMSE_AED"]))

    def test_generated_figures_exist(self):
        self.assertTrue((FIGURES_DIR / "price_vs_mileage.svg").is_file())
        self.assertTrue((FIGURES_DIR / "median_price_by_year.svg").is_file())


if __name__ == "__main__":
    unittest.main()
