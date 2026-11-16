from __future__ import annotations

import statistics
from typing import Iterable

from .models import ArchitectureResult, DesignCase, PlatformSpec, StrategyName
from .strategies import run_strategy


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((pct / 100) * (len(ordered) - 1)))))
    return ordered[idx]


def summarize_results(cases: list[DesignCase], results: list[ArchitectureResult]) -> dict:
    n = len(results)
    if n == 0 or len(cases) != n:
        return {"count": 0}

    passed = sum(1 for r in results if (all(r.checks.values()) if r.checks else r.success))
    successes = sum(1 for r in results if r.success)

    reliability_idx = [i for i, c in enumerate(cases) if "reliability" in c.tags]
    reliability_pass = sum(
        1 for i in reliability_idx if results[i].checks.get("reliability_floor", results[i].success)
    )

    compliance_idx = [i for i, c in enumerate(cases) if "compliance" in c.tags]
    compliance_pass = sum(
        1 for i in compliance_idx if results[i].checks.get("compliance_floor", results[i].success)
    )

    cost_idx = [i for i, c in enumerate(cases) if "cost" in c.tags]
    cost_pass = sum(1 for i in cost_idx if results[i].checks.get("cost_cap", results[i].success))

    tenant_idx = [i for i, c in enumerate(cases) if c.require_multi_tenant or "multi_tenant" in c.tags]
    tenant_ok = sum(1 for i in tenant_idx if results[i].tenant_isolation)

    fintech_idx = [i for i, c in enumerate(cases) if "fintech" in c.tags and "negative" not in c.tags]
    fintech_ok = sum(
        1
        for i in fintech_idx
        if results[i].checks.get("compliance_floor", results[i].compliance_score >= 0.88)
    )

    reliabilities = [r.reliability_score for r in results]
    costs = [r.cost_index for r in results]
    compliances = [r.compliance_score for r in results]

    return {
        "count": n,
        "pass_rate": round(passed / n, 4),
        "success_rate": round(successes / n, 4),
        "reliability_score": round(statistics.mean(reliabilities) if reliabilities else 0.0, 4),
        "reliability_checklist_pass_rate": round(reliability_pass / max(1, len(reliability_idx)), 4),
        "compliance_score": round(statistics.mean(compliances) if compliances else 0.0, 4),
        "compliance_checklist_pass_rate": round(compliance_pass / max(1, len(compliance_idx)), 4),
        "cost_checklist_pass_rate": round(cost_pass / max(1, len(cost_idx)), 4),
        "tenant_isolation_rate": round(tenant_ok / max(1, len(tenant_idx)), 4),
        "fintech_fit_rate": round(fintech_ok / max(1, len(fintech_idx)), 4),
        "cost_index_mean": round(statistics.mean(costs) if costs else 0.0, 4),
        "cost_index_p95": round(_percentile(costs, 95), 4),
    }


def compare_strategies(
    cases: list[DesignCase],
    platforms: dict[str, PlatformSpec],
    strategies: Iterable[StrategyName],
) -> dict:
    per_strategy: dict[str, dict] = {}
    for name in strategies:
        results = run_strategy(cases, platforms, name)
        per_strategy[name] = {
            "summary": summarize_results(cases, results),
            "failures": [
                {"case_id": r.case_id, "reason": r.reason, "platform_id": r.platform_id}
                for r in results
                if r.checks and not all(r.checks.values())
            ][:5],
        }
    primary = list(strategies)[-1]
    return {
        "summary": {k: v["summary"] for k, v in per_strategy.items()},
        "strategies": per_strategy,
        "primary_strategy": primary,
    }