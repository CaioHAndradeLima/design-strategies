import unittest
from pathlib import Path

from design_strategies.data import load_golden, load_platforms, validate_golden
from design_strategies.evaluation import evaluate
from design_strategies.measure_profiles import evaluate_gates, load_measure_profiles
from design_strategies.pipeline_evaluation import run_design_pipeline_eval

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "config/measure_profiles.json"


class MetricsGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.platforms = load_platforms(ROOT / "data/platforms.json")
        cls.cases = load_golden(ROOT / "data/golden.json")
        validate_golden(cls.platforms, cls.cases)

    def test_evaluate_three_strategies(self) -> None:
        report = evaluate(self.cases, self.platforms)
        for name in (
            "startup_single_region",
            "enterprise_multi_tenant",
            "fintech_high_stakes",
        ):
            self.assertIn(name, report["summary"])

    def test_fintech_beats_startup_on_fintech_fit(self) -> None:
        report = evaluate(self.cases, self.platforms)
        fintech = report["summary"]["fintech_high_stakes"]["fintech_fit_rate"]
        startup = report["summary"]["startup_single_region"]["fintech_fit_rate"]
        self.assertGreaterEqual(fintech, startup)

    def test_ci_design_eval_passes(self) -> None:
        profile = load_measure_profiles(PROFILES)["ci-design-eval"]
        report = run_design_pipeline_eval(ROOT, profile)
        gate = evaluate_gates(report, profile)
        self.assertTrue(gate["passed"], msg=gate.get("failures"))

    def test_ci_all_strategies_profile_loads(self) -> None:
        profiles = load_measure_profiles(PROFILES)
        self.assertIn("ci-design-eval", profiles)


if __name__ == "__main__":
    unittest.main()