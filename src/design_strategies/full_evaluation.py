from pathlib import Path

from .data import load_golden, load_platforms, validate_golden
from .evaluation import evaluate, evaluate_implementation_checklist
from .implementation_flow import summarize_implementation_flow
from .maturity import lab_maturity_snapshot
from .scenario_evaluation import evaluate_scenarios
from .strategies import DEFAULT_STRATEGIES


def run_full_evaluation(root: Path) -> dict:
    platforms = load_platforms(root / "data/platforms.json")
    cases = load_golden(root / "data/golden.json")
    validate_golden(platforms, cases)

    assembly = evaluate(cases, platforms, strategies=DEFAULT_STRATEGIES)
    checklist = evaluate_implementation_checklist(cases, platforms)
    scenarios = evaluate_scenarios(cases, platforms, strategy="enterprise_multi_tenant")

    return {
        "implementation_strategies": assembly,
        "implementation_flow": summarize_implementation_flow(checklist),
        "implementation_checklist": checklist,
        "maturity": lab_maturity_snapshot(),
        "scenarios": scenarios,
        "decision_based": {
            "reference_doc": "design/README.md",
            "recommended_default": "enterprise_multi_tenant",
        },
        "coverage": {
            "design_guides": "6/6",
            "lab_coverage_percent": 100,
            "index": "docs/LAB_COVERAGE.md",
        },
    }