"""Run with: python3 -m unittest discover -s tests -v"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "tests" / "fixtures"
SCRIPT = ROOT / "scripts" / "check_regression.py"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


class CheckRegression(unittest.TestCase):
    def test_passing_results_exit_zero(self):
        r = run(str(FIX / "results_pass.json"), "--baseline", str(FIX / "baseline_fixture.json"))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("no regression", r.stdout)

    def test_regressing_results_exit_one_and_name_category(self):
        r = run(str(FIX / "results_regress.json"), "--baseline", str(FIX / "baseline_fixture.json"))
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("category 'injection' dropped", r.stdout)
        self.assertNotIn("category 'refund' dropped", r.stdout)

    def test_thresholds_are_configurable(self):
        r = run(str(FIX / "results_regress.json"), "--baseline", str(FIX / "baseline_fixture.json"),
                "--max-overall-drop", "100", "--max-category-drop", "100")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_update_baseline_requires_confirmation(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "baseline.json"
            r = run(str(FIX / "results_pass.json"), "--baseline", str(target), "--update-baseline")
            self.assertEqual(r.returncode, 2)
            self.assertFalse(target.exists())

    def test_update_baseline_with_confirmation_writes_file(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / "baseline.json"
            r = run(str(FIX / "results_pass.json"), "--baseline", str(target), "--update-baseline", "--confirm", "UPDATE")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            data = json.loads(target.read_text())
            self.assertEqual(data["categories"]["injection"], {"passed": 3, "total": 3})

    def test_missing_baseline_is_usage_error(self):
        r = run(str(FIX / "results_pass.json"), "--baseline", str(FIX / "nope.json"))
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
