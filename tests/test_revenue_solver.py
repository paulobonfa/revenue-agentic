import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOLVER = ROOT / "skills/revenue-mechanics/scripts/revenue_solver.py"


class TestRevenueSolverWorkflows(unittest.TestCase):
    def run_solver(self, mode, payload, expected_code=0):
        proc = subprocess.run(
            [sys.executable, str(SOLVER), mode, "--json", json.dumps(payload)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(proc.returncode, expected_code, proc.stderr or proc.stdout)
        parsed = json.loads(proc.stdout)
        self.assertEqual(parsed["ok"], expected_code == 0)
        return parsed

    def test_media_funnel(self):
        result = self.run_solver("media-funnel", {
            "budget": 12000,
            "cpm": 40,
            "ctr": 0.02,
            "session_realization_rate": 0.92,
            "downstream_rates": [0.07, 0.18],
            "average_value": 650,
        })["result"]
        self.assertAlmostEqual(result["outcomes"], 69.552)
        self.assertEqual(result["reliability"]["tier"], "CORE_A")

    def test_reverse_funnel(self):
        result = self.run_solver("reverse-funnel", {
            "target_outcome": 100,
            "conversion_rates": [0.08, 0.20],
        })["result"]
        self.assertAlmostEqual(result["required_initial_volume"], 6250)

    def test_cro_target(self):
        result = self.run_solver("cro-target", {
            "current_value": 0.08,
            "target_growth": 1.25,
            "upper_bound": 1,
        })["result"]
        self.assertAlmostEqual(result["required_value"], 0.10)
        self.assertIn("ceteris paribus", result["assumption"])

    def test_ecommerce(self):
        result = self.run_solver("ecommerce", {
            "sessions": 50000,
            "conversion_rate": 0.024,
            "units_per_order": 1.6,
            "average_selling_price": 112.5,
        })["result"]
        self.assertAlmostEqual(result["revenue"], 216000)

    def test_b2b(self):
        result = self.run_solver("b2b", {
            "bookings_target": 1200000,
            "win_rate": 0.25,
            "average_deal_value": 25000,
        })["result"]
        self.assertAlmostEqual(result["required_opportunities"], 192)

    def test_subscription(self):
        result = self.run_solver("subscription", {
            "active0": 500,
            "churn_rate": 0.04,
            "new_customers_per_period": 60,
            "periods": 12,
            "arpa": 200,
            "cac": 900,
            "contribution_margin": 0.75,
        })["result"]
        self.assertAlmostEqual(result["active_end"], 887.290242670233, places=6)
        self.assertEqual(result["ltv_payback_reliability"]["tier"], "CONDITIONAL")

    def test_scale(self):
        result = self.run_solver("scale", {
            "input1": 20000,
            "input2": 30000,
            "outcome1": 100,
            "outcome2": 130,
            "revenue1": 50000,
            "revenue2": 62000,
            "structural_change": False,
        })["result"]
        self.assertEqual(result["mode"], "comparable-scale")
        self.assertAlmostEqual(result["marginal_cost"], 10000 / 30)

    def test_consistency(self):
        result = self.run_solver("consistency", {"checks": [
            {"name": "revenue", "observed": 804.66, "derived": 1016.07}
        ]})["result"]
        self.assertEqual(result["worst_tier"], "D")
        self.assertTrue(result["data_integrity_warning"])

    def test_fractional_subscription_period_is_rejected(self):
        result = self.run_solver("subscription", {
            "active0": 500,
            "churn_rate": 0.04,
            "new_customers_per_period": 60,
            "periods": 12.5,
            "arpa": 200,
        }, expected_code=2)
        self.assertIn("integer", result["error"])

    def test_empty_consistency_checks_are_rejected(self):
        result = self.run_solver("consistency", {"checks": []}, expected_code=2)
        self.assertIn("non-empty", result["error"])

    def test_structural_flag_must_be_boolean(self):
        result = self.run_solver("scale", {
            "input1": 20000,
            "input2": 30000,
            "outcome1": 100,
            "outcome2": 130,
            "structural_change": "false",
        }, expected_code=2)
        self.assertIn("boolean", result["error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
