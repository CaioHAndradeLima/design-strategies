from __future__ import annotations

from .evaluation import evaluate
from .models import DesignCase, PlatformSpec, StrategyName


def run_measurement_pipeline(
    cases: list[DesignCase],
    platforms: dict[str, PlatformSpec],
    *,
    strategies: tuple[StrategyName, ...],
) -> dict:
    report = evaluate(cases, platforms, strategies=strategies)
    return {
        "eval_type": "design_measure",
        "summary": report["summary"],
        "strategies": report["strategies"],
        "primary_strategy": report["primary_strategy"],
    }