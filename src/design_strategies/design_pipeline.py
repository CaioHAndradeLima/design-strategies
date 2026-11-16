from __future__ import annotations

import hashlib

from .models import ArchitectureResult, DesignCase, PlatformSpec, StrategyName

STRATEGY_COST_MULTIPLIER: dict[StrategyName, float] = {
    "startup_single_region": 1.0,
    "enterprise_multi_tenant": 1.45,
    "fintech_high_stakes": 2.15,
}

STRATEGY_RELIABILITY_BONUS: dict[StrategyName, float] = {
    "startup_single_region": 0.0,
    "enterprise_multi_tenant": 0.04,
    "fintech_high_stakes": 0.06,
}

STRATEGY_COMPLIANCE_BONUS: dict[StrategyName, float] = {
    "startup_single_region": 0.0,
    "enterprise_multi_tenant": 0.08,
    "fintech_high_stakes": 0.15,
}


def _stable_jitter(seed: str, scale: float = 1.0) -> float:
    digest = hashlib.sha256(seed.encode()).hexdigest()
    bucket = int(digest[:8], 16) % 1000
    return (bucket / 1000.0) * scale


def _pick_platform(
    case: DesignCase,
    platforms: dict[str, PlatformSpec],
    strategy: StrategyName,
) -> PlatformSpec:
    if strategy == "fintech_high_stakes":
        if "fintech-pattern" in platforms:
            return platforms["fintech-pattern"]
        return platforms[case.primary_platform_id]
    if strategy == "enterprise_multi_tenant" and case.require_multi_tenant:
        for pid in (case.secondary_platform_id, "aws-advanced", case.primary_platform_id):
            if pid in platforms and platforms[pid].supports_tenant_isolation:
                return platforms[pid]
    return platforms[case.primary_platform_id]


def _simulate_architecture(
    case: DesignCase,
    platform: PlatformSpec,
    *,
    strategy: StrategyName,
) -> tuple[float, float, float, bool, bool, bool]:
    reliability = min(
        0.999,
        platform.base_reliability
        + STRATEGY_RELIABILITY_BONUS[strategy]
        + _stable_jitter(case.id + strategy, 0.02),
    )
    compliance = min(
        1.0,
        platform.compliance_baseline
        + STRATEGY_COMPLIANCE_BONUS[strategy]
        + _stable_jitter(case.id + "cmp", 0.03),
    )
    cost = (
        platform.cost_unit_index
        * STRATEGY_COST_MULTIPLIER[strategy]
        * (0.85 + _stable_jitter(case.id + "cost", 0.2))
    )

    tenant_isolation = strategy != "startup_single_region" and (
        platform.supports_tenant_isolation or strategy == "enterprise_multi_tenant"
    )
    audit_controls = strategy == "fintech_high_stakes" or (
        strategy == "enterprise_multi_tenant" and platform.audit_ready
    )
    dr_active = strategy != "startup_single_region" and platform.supports_multi_region

    if case.require_multi_tenant and not tenant_isolation:
        reliability -= 0.08
        compliance -= 0.1

    if case.require_pci and strategy == "startup_single_region":
        compliance -= 0.25
        reliability -= 0.05

    if case.require_audit_trail and not audit_controls:
        compliance -= 0.2

    if case.simulate_region_outage:
        if strategy == "startup_single_region":
            reliability -= 0.12
        elif dr_active:
            reliability -= 0.02
            if strategy == "enterprise_multi_tenant":
                reliability += 0.03
        else:
            reliability -= 0.07

    if case.workload_class == "regulated" and strategy == "startup_single_region":
        compliance -= 0.15

    if cost > case.cost_budget_index and strategy != "fintech_high_stakes":
        cost *= 0.92

    reliability = max(0.5, min(0.999, reliability))
    compliance = max(0.3, min(1.0, compliance))
    return round(reliability, 4), round(cost, 4), round(compliance, 4), tenant_isolation, audit_controls, dr_active


def _score_result(case: DesignCase, result: ArchitectureResult) -> dict[str, bool]:
    exp = case.expects
    checks: dict[str, bool] = {}
    checks["meets_sla"] = (
        result.reliability_score >= case.min_uptime_sla if exp.require_success else True
    )
    checks["success"] = result.success if exp.require_success else (not result.success)
    if exp.min_reliability is not None:
        checks["reliability_floor"] = result.reliability_score >= exp.min_reliability
    if exp.max_cost_index is not None:
        checks["cost_cap"] = result.cost_index <= exp.max_cost_index
    if exp.min_compliance is not None:
        checks["compliance_floor"] = result.compliance_score >= exp.min_compliance
    if exp.expect_tenant_isolation:
        checks["tenant_isolation"] = result.tenant_isolation
    if exp.expect_audit_controls:
        checks["audit_controls"] = result.audit_controls
    if exp.require_dr_on_outage:
        floor = exp.min_reliability if exp.min_reliability is not None else 0.95
        checks["dr_active"] = result.dr_active and result.reliability_score >= floor
    return checks


def run_architecture(
    case: DesignCase,
    platforms: dict[str, PlatformSpec],
    *,
    strategy: StrategyName,
) -> ArchitectureResult:
    platform = _pick_platform(case, platforms, strategy)
    reliability, cost, compliance, tenant_isolation, audit_controls, dr_active = _simulate_architecture(
        case, platform, strategy=strategy
    )

    success = reliability >= case.min_uptime_sla
    if case.require_pci and compliance < 0.85 and strategy != "fintech_high_stakes":
        success = False
    if case.require_audit_trail and not audit_controls and strategy == "startup_single_region":
        success = False
    if case.simulate_region_outage and strategy == "startup_single_region":
        success = False

    result = ArchitectureResult(
        case_id=case.id,
        strategy=strategy,
        platform_id=platform.platform_id,
        success=success,
        reliability_score=reliability,
        cost_index=cost,
        compliance_score=compliance,
        tenant_isolation=tenant_isolation,
        audit_controls=audit_controls,
        dr_active=dr_active,
    )
    checks = _score_result(case, result)
    result.checks = checks
    failed = [k for k, v in checks.items() if not v]
    result.reason = f"failed: {', '.join(failed)}" if failed else "ok"
    return result