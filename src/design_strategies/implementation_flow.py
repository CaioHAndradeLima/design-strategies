from __future__ import annotations

CHECKLIST_ITEMS = (
    "single_region_baseline",
    "multi_az_resilience",
    "tenant_isolation",
    "async_workers",
    "observability_alarms",
    "compliance_controls",
    "fintech_hitl",
    "regression_gates",
)


def summarize_implementation_flow(checklist_eval: dict) -> dict:
    by_tag = checklist_eval.get("by_tag", {})
    covered = [item for item in CHECKLIST_ITEMS if _item_covered(item, by_tag, checklist_eval)]
    return {
        "checklist_items": list(CHECKLIST_ITEMS),
        "covered_in_repo": covered,
        "coverage_fraction": round(len(covered) / len(CHECKLIST_ITEMS), 3),
        "reference_doc": "design/aws-intermediate.md",
    }


def _item_covered(item: str, by_tag: dict, checklist_eval: dict) -> bool:
    mapping = {
        "single_region_baseline": "mvp" in by_tag or "reliability" in by_tag,
        "multi_az_resilience": checklist_eval.get("overall_pass_rate", 0) >= 0.65,
        "tenant_isolation": "multi_tenant" in by_tag,
        "async_workers": "reliability" in by_tag,
        "observability_alarms": checklist_eval.get("checklist_complete", False),
        "compliance_controls": "compliance" in by_tag,
        "fintech_hitl": "fintech" in by_tag,
        "regression_gates": checklist_eval.get("checklist_complete", False),
    }
    return mapping.get(item, False)