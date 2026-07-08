from __future__ import annotations

from app.sidecar_topology_review.source_loader import load_completed_sidecar_inventory


ZONE_ORDER = {
    "data_ingestion_and_quarantine": 10,
    "context_and_interpretation": 20,
    "governance_and_review_gate": 30,
    "presentation_and_immutable_archive": 40,
}


def build_zone_summary() -> dict[str, tuple[str, ...]]:
    result: dict[str, list[str]] = {zone: [] for zone in ZONE_ORDER}
    for row in load_completed_sidecar_inventory():
        result[str(row["zone"])].append(str(row["sidecar_id"]))
    return {zone: tuple(items) for zone, items in result.items()}


def validate_zone_contract() -> dict[str, object]:
    rows = load_completed_sidecar_inventory()
    zones = {str(row["zone"]) for row in rows}
    unknown_zones = tuple(sorted(zones - set(ZONE_ORDER)))
    empty_zones = tuple(sorted(zone for zone, items in build_zone_summary().items() if not items))
    return {
        "zone_contract_required": True,
        "known_zone_count": len(ZONE_ORDER),
        "unknown_zones": unknown_zones,
        "empty_zones": empty_zones,
        "isolation_zone_valid": not unknown_zones and not empty_zones,
        "risk_flag_downgrade_allowed": False,
        "reason_code_deletion_allowed": False,
        "operator_review_bypass_allowed": False,
    }
