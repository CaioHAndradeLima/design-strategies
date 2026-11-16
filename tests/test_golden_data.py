import unittest
from pathlib import Path

from design_strategies.data import load_golden, load_platforms, validate_golden

ROOT = Path(__file__).resolve().parents[1]


class GoldenDataTests(unittest.TestCase):
    def test_platforms_non_empty(self) -> None:
        platforms = load_platforms(ROOT / "data/platforms.json")
        self.assertGreaterEqual(len(platforms), 3)

    def test_golden_cases_labeled(self) -> None:
        cases = load_golden(ROOT / "data/golden.json")
        self.assertGreaterEqual(len(cases), 8)
        for case in cases:
            self.assertTrue(case.id)

    def test_golden_refs(self) -> None:
        platforms = load_platforms(ROOT / "data/platforms.json")
        cases = load_golden(ROOT / "data/golden.json")
        validate_golden(platforms, cases)


if __name__ == "__main__":
    unittest.main()