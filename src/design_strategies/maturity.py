from __future__ import annotations


def lab_maturity_snapshot() -> dict:
    return {
        "mvp_startup": {
            "recommended_strategy": "startup_single_region",
            "in_repo": True,
            "notes": "Lambda or single-region Cloud Run; minimize ops and cost while proving agent UX.",
        },
        "growing_saas": {
            "recommended_strategy": "enterprise_multi_tenant",
            "in_repo": True,
            "notes": "ECS/Fargate or multi-service GCP with tenant isolation and async workers.",
        },
        "regulated_fintech": {
            "recommended_strategy": "fintech_high_stakes",
            "in_repo": True,
            "notes": "Audit, HITL, PCI-scoped lanes; ci-design-eval gate on compliance and reliability.",
        },
        "production_deployment_only": [
            "Live multi-region failover and chaos drills",
            "Real SOC2/PCI control evidence collection",
            "Per-tenant encryption and data residency policies",
            "OTel topology maps and cost allocation tags",
        ],
    }