from __future__ import annotations

from .models import DesignCase, PlatformSpec, StrategyName
from .strategies import run_strategy


def _subset_pass_rate(
    cases: list[DesignCase],
    platforms: dict[str, PlatformSpec],
    *,
    strategy: StrategyName,
    tag: str,
) -> dict:
    subset = [c for c in cases if tag in c.tags]
    if not subset:
        return {"count": 0, "pass_rate": 1.0}
    runs = run_strategy(subset, platforms, strategy)
    passed = sum(1 for r in runs if r.checks and all(r.checks.values()))
    return {"count": len(subset), "pass_rate": round(passed / len(subset), 4)}


def evaluate_scenarios(
    cases: list[DesignCase],
    platforms: dict[str, PlatformSpec],
    *,
    strategy: StrategyName = "enterprise_multi_tenant",
) -> dict:
    runs = run_strategy(cases, platforms, strategy)

    reliability_idx = [i for i, c in enumerate(cases) if "reliability" in c.tags]
    reliability_rate = sum(
        1 for i in reliability_idx if runs[i].checks.get("reliability_floor", runs[i].success)
    ) / max(1, len(reliability_idx))

    compliance_idx = [i for i, c in enumerate(cases) if "compliance" in c.tags]
    compliance_rate = sum(
        1 for i in compliance_idx if runs[i].checks.get("compliance_floor", runs[i].success)
    ) / max(1, len(compliance_idx))

    fintech_idx = [i for i, c in enumerate(cases) if "fintech" in c.tags and "negative" not in c.tags]
    fintech_rate = sum(1 for i in fintech_idx if runs[i].compliance_score >= 0.88) / max(
        1, len(fintech_idx)
    )

    return {
        "reliability": _subset_pass_rate(cases, platforms, strategy=strategy, tag="reliability"),
        "cost": _subset_pass_rate(cases, platforms, strategy=strategy, tag="cost"),
        "compliance": _subset_pass_rate(cases, platforms, strategy=strategy, tag="compliance"),
        "multi_tenant": _subset_pass_rate(cases, platforms, strategy=strategy, tag="multi_tenant"),
        "fintech": _subset_pass_rate(cases, platforms, strategy=strategy, tag="fintech"),
        "reliability_checklist_pass_rate": round(reliability_rate, 4),
        "compliance_checklist_pass_rate": round(compliance_rate, 4),
        "fintech_fit_rate": round(fintech_rate, 4),
    }