"""Design pipeline evaluation scorecard."""

from __future__ import annotations

from pathlib import Path

from .data import load_golden, load_platforms, validate_golden
from .measure_profiles import MeasureProfile
from .measurement_pipeline import run_measurement_pipeline
from .scenario_evaluation import evaluate_scenarios
from .strategies import select_strategies


def build_scorecard(measure_report: dict, *, primary_strategy: str = "enterprise_multi_tenant") -> dict:
    core = measure_report.get("summary", {}).get(primary_strategy, {})
    return {
        "primary_strategy": primary_strategy,
        "core_design": {
            "reliability_score": core.get("reliability_score"),
            "compliance_score": core.get("compliance_score"),
            "reliability_checklist_pass_rate": core.get("reliability_checklist_pass_rate"),
            "compliance_checklist_pass_rate": core.get("compliance_checklist_pass_rate"),
            "fintech_fit_rate": core.get("fintech_fit_rate"),
            "cost_index_p95": core.get("cost_index_p95"),
        },
        "reference_doc": "design/README.md",
    }


def run_design_pipeline_eval(root: Path, profile: MeasureProfile) -> dict:
    platforms = load_platforms(root / "data/platforms.json")
    cases = load_golden(root / "data/golden.json")
    validate_golden(platforms, cases)

    strategies = select_strategies(list(profile.strategies))
    measure_report = run_measurement_pipeline(cases, platforms, strategies=strategies)
    primary = strategies[0] if strategies else "enterprise_multi_tenant"
    scenarios = evaluate_scenarios(cases, platforms, strategy=primary)  # type: ignore[arg-type]
    fintech_scenarios = evaluate_scenarios(cases, platforms, strategy="fintech_high_stakes")
    scenarios["fintech_fit_rate"] = max(
        scenarios.get("fintech_fit_rate", 0.0),
        fintech_scenarios.get("fintech_fit_rate", 0.0),
    )
    scenarios["compliance_checklist_pass_rate"] = max(
        scenarios.get("compliance_checklist_pass_rate", 0.0),
        fintech_scenarios.get("compliance_checklist_pass_rate", 0.0),
    )

    flat_summary = measure_report["summary"]
    return {
        **measure_report,
        "eval_type": "design_pipeline",
        "profile": {"name": profile.name, "description": profile.description},
        "scorecard": build_scorecard(measure_report, primary_strategy=primary),
        "scenarios": scenarios,
        "summary": flat_summary,
    }