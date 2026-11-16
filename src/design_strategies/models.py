from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

StrategyName = Literal[
    "startup_single_region",
    "enterprise_multi_tenant",
    "fintech_high_stakes",
]

WorkloadClass = Literal["mvp", "saas", "regulated"]


@dataclass
class PlatformSpec:
    platform_id: str
    base_reliability: float
    cost_unit_index: float
    compliance_baseline: float = 0.5
    supports_multi_region: bool = False
    supports_tenant_isolation: bool = False
    audit_ready: bool = False
    tier: str = "standard"


@dataclass
class DesignExpectations:
    min_reliability: float | None = None
    max_cost_index: float | None = None
    min_compliance: float | None = None
    expect_tenant_isolation: bool = False
    expect_audit_controls: bool = False
    require_dr_on_outage: bool = False
    require_success: bool = True


@dataclass
class DesignCase:
    id: str
    workload_tag: str
    scenario: str
    primary_platform_id: str
    secondary_platform_id: str = "aws-intermediate"
    workload_class: WorkloadClass = "mvp"
    simulate_region_outage: bool = False
    require_multi_tenant: bool = False
    require_audit_trail: bool = False
    require_pci: bool = False
    cost_budget_index: float = 1.0
    min_uptime_sla: float = 0.99
    expects: DesignExpectations = field(default_factory=DesignExpectations)
    tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchitectureResult:
    case_id: str
    strategy: StrategyName
    platform_id: str
    success: bool
    reliability_score: float = 0.0
    cost_index: float = 0.0
    compliance_score: float = 0.0
    tenant_isolation: bool = False
    audit_controls: bool = False
    dr_active: bool = False
    checks: dict[str, bool] = field(default_factory=dict)
    reason: str = ""