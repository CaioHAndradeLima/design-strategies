from __future__ import annotations

import json
from pathlib import Path

from .models import DesignCase, DesignExpectations, PlatformSpec


def load_platforms(path: Path) -> dict[str, PlatformSpec]:
    raw = json.loads(path.read_text())
    out: dict[str, PlatformSpec] = {}
    for platform_id, row in raw["platforms"].items():
        out[platform_id] = PlatformSpec(
            platform_id=platform_id,
            base_reliability=float(row["base_reliability"]),
            cost_unit_index=float(row["cost_unit_index"]),
            compliance_baseline=float(row.get("compliance_baseline", 0.5)),
            supports_multi_region=bool(row.get("supports_multi_region", False)),
            supports_tenant_isolation=bool(row.get("supports_tenant_isolation", False)),
            audit_ready=bool(row.get("audit_ready", False)),
            tier=row.get("tier", "standard"),
        )
    return out


def _load_expectations(row: dict) -> DesignExpectations:
    exp = row.get("expects", {})
    if not exp:
        return DesignExpectations()
    allowed = {f.name for f in DesignExpectations.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    filtered = {k: v for k, v in exp.items() if k in allowed}
    return DesignExpectations(**filtered)


def load_golden(path: Path) -> list[DesignCase]:
    raw = json.loads(path.read_text())
    cases: list[DesignCase] = []
    for row in raw["cases"]:
        cases.append(
            DesignCase(
                id=row["id"],
                workload_tag=row.get("workload_tag", "mvp"),
                scenario=row["scenario"],
                primary_platform_id=row.get("primary_platform_id", "aws-basic"),
                secondary_platform_id=row.get("secondary_platform_id", "aws-intermediate"),
                workload_class=row.get("workload_class", "mvp"),  # type: ignore[arg-type]
                simulate_region_outage=bool(row.get("simulate_region_outage", False)),
                require_multi_tenant=bool(row.get("require_multi_tenant", False)),
                require_audit_trail=bool(row.get("require_audit_trail", False)),
                require_pci=bool(row.get("require_pci", False)),
                cost_budget_index=float(row.get("cost_budget_index", 1.0)),
                min_uptime_sla=float(row.get("min_uptime_sla", 0.99)),
                expects=_load_expectations(row),
                tags=row.get("tags", []),
            )
        )
    return cases


def validate_golden(platforms: dict[str, PlatformSpec], cases: list[DesignCase]) -> None:
    for case in cases:
        if case.primary_platform_id not in platforms:
            raise ValueError(
                f"case {case.id} references unknown primary platform {case.primary_platform_id}"
            )
        if case.secondary_platform_id not in platforms:
            raise ValueError(
                f"case {case.id} references unknown secondary platform {case.secondary_platform_id}"
            )