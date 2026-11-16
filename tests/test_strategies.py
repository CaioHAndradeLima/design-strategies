import unittest
from pathlib import Path

from design_strategies.data import load_golden, load_platforms, validate_golden
from design_strategies.design_pipeline import run_architecture
from design_strategies.strategies import run_strategy

ROOT = Path(__file__).resolve().parents[1]


class StrategyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.platforms = load_platforms(ROOT / "data/platforms.json")
        cls.cases = load_golden(ROOT / "data/golden.json")
        validate_golden(cls.platforms, cls.cases)

    def test_enterprise_tenant_isolation(self) -> None:
        case = next(c for c in self.cases if c.id == "saas-multi-tenant")
        result = run_architecture(case, self.platforms, strategy="enterprise_multi_tenant")
        self.assertTrue(result.tenant_isolation)
        self.assertTrue(result.checks.get("tenant_isolation"))

    def test_fintech_audit_controls(self) -> None:
        case = next(c for c in self.cases if c.id == "pci-agent-lane")
        result = run_architecture(case, self.platforms, strategy="fintech_high_stakes")
        self.assertTrue(result.audit_controls)
        self.assertGreaterEqual(result.compliance_score, 0.9)

    def test_startup_region_outage_fails_drill(self) -> None:
        case = next(c for c in self.cases if c.id == "region-outage-drill")
        result = run_architecture(case, self.platforms, strategy="startup_single_region")
        self.assertFalse(result.checks.get("dr_active", True))

    def test_fintech_beats_startup_on_compliance(self) -> None:
        case = next(c for c in self.cases if c.id == "pci-agent-lane")
        fintech = run_architecture(case, self.platforms, strategy="fintech_high_stakes")
        startup = run_architecture(case, self.platforms, strategy="startup_single_region")
        self.assertGreater(fintech.compliance_score, startup.compliance_score)

    def test_negative_control_mis_sized_basic(self) -> None:
        case = next(c for c in self.cases if c.id == "basic-under-regulated-load")
        result = run_strategy([case], self.platforms, "startup_single_region")[0]
        self.assertTrue(result.checks.get("success"))


if __name__ == "__main__":
    unittest.main()