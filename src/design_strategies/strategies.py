from __future__ import annotations

from typing import Iterable

from .design_pipeline import run_architecture
from .models import ArchitectureResult, DesignCase, PlatformSpec, StrategyName

DEFAULT_STRATEGIES: tuple[StrategyName, ...] = (
    "startup_single_region",
    "enterprise_multi_tenant",
    "fintech_high_stakes",
)


def select_strategies(names: list[str] | None) -> tuple[StrategyName, ...]:
    if not names:
        return DEFAULT_STRATEGIES
    allowed = set(DEFAULT_STRATEGIES)
    out: list[StrategyName] = []
    for name in names:
        if name not in allowed:
            raise ValueError(f"Unknown strategy '{name}'")
        out.append(name)  # type: ignore[arg-type]
    return tuple(out)


def run_strategy(
    cases: Iterable[DesignCase],
    platforms: dict[str, PlatformSpec],
    strategy: StrategyName,
) -> list[ArchitectureResult]:
    return [run_architecture(case, platforms, strategy=strategy) for case in cases]