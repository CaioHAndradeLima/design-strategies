from __future__ import annotations

from .metrics import compare_strategies
from .models import DesignCase, PlatformSpec, StrategyName
from .strategies import DEFAULT_STRATEGIES


def evaluate(
    cases: list[DesignCase],
    platforms: dict[str, PlatformSpec],
    *,
    strategies: tuple[StrategyName, ...] | None = None,
) -> dict:
    names = strategies or DEFAULT_STRATEGIES
    return compare_strategies(cases, platforms, names)


def evaluate_implementation_checklist(
    cases: list[DesignCase], platforms: dict[str, PlatformSpec]
) -> dict:
    from .strategies import run_strategy

    runs = run_strategy(cases, platforms, "enterprise_multi_tenant")
    passed = sum(1 for r in runs if r.checks and all(r.checks.values())) / max(1, len(runs))
    by_tag: dict[str, dict] = {}
    for tag in ("reliability", "cost", "compliance", "multi_tenant", "fintech", "audit"):
        subset = [c for c in cases if tag in c.tags]
        if not subset:
            continue
        sub_runs = run_strategy(subset, platforms, "enterprise_multi_tenant")
        sub_pass = sum(1 for r in sub_runs if r.checks and all(r.checks.values())) / len(subset)
        by_tag[tag] = {"pass_rate": round(sub_pass, 4), "count": len(subset)}
    return {"overall_pass_rate": round(passed, 4), "by_tag": by_tag, "checklist_complete": len(by_tag) >= 5}