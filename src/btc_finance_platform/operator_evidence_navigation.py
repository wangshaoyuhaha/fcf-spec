from __future__ import annotations

from typing import Any

from btc_finance_platform.operator_evidence_console import build_operator_evidence_console_manifest
from btc_finance_platform.operator_evidence_console import build_operator_evidence_section_lookup


def build_operator_evidence_navigation_index() -> dict[str, Any]:
    manifest = build_operator_evidence_console_manifest()
    routes = []
    for section in manifest["sections"]:
        routes.append({
            "route": "/evidence/" + section["section_id"],
            "section_id": section["section_id"],
            "title": section["title"],
            "artifact": section["artifact"],
            "read_only": True,
        })

    return {
        "ok": True,
        "type": "operator_evidence_navigation_index",
        "root_route": "/evidence",
        "release_tag": manifest["release_tag"],
        "route_count": len(routes),
        "routes": routes,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def resolve_operator_evidence_route(route: str) -> dict[str, Any]:
    normalized = "/" + str(route).strip().strip("/")
    index = build_operator_evidence_navigation_index()

    if normalized == "/evidence":
        return {
            "ok": True,
            "type": "operator_evidence_route_resolution",
            "route": normalized,
            "view": "overview",
            "route_count": index["route_count"],
            "read_only": True,
            "deploy_enabled": False,
            "real_trading_enabled": False,
        }

    route_map = {item["route"]: item for item in index["routes"]}
    section = route_map.get(normalized)
    if section is None:
        return {
            "ok": False,
            "type": "operator_evidence_route_resolution",
            "route": normalized,
            "error": "UNKNOWN_EVIDENCE_ROUTE",
            "read_only": True,
            "deploy_enabled": False,
            "real_trading_enabled": False,
        }

    lookup = build_operator_evidence_section_lookup(section["section_id"])
    return {
        "ok": True,
        "type": "operator_evidence_route_resolution",
        "route": normalized,
        "view": "section",
        "section_id": section["section_id"],
        "section": lookup["section"],
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
    }


def build_operator_evidence_breadcrumb(section_id: str | None = None) -> dict[str, Any]:
    crumbs = [
        {"label": "Operator Evidence Console", "route": "/evidence"},
    ]

    if section_id:
        lookup = build_operator_evidence_section_lookup(section_id)
        if lookup["ok"] and lookup["section"]:
            crumbs.append({
                "label": lookup["section"]["title"],
                "route": "/evidence/" + section_id,
            })

    return {
        "ok": True,
        "type": "operator_evidence_breadcrumb",
        "section_id": section_id,
        "crumb_count": len(crumbs),
        "crumbs": crumbs,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
    }


def build_operator_evidence_navigation_overview() -> dict[str, Any]:
    index = build_operator_evidence_navigation_index()
    return {
        "ok": True,
        "type": "operator_evidence_navigation_overview",
        "root_route": index["root_route"],
        "release_tag": index["release_tag"],
        "route_count": index["route_count"],
        "available_sections": [route["section_id"] for route in index["routes"]],
        "summary": "Local read-only navigation overview for operator evidence console.",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def search_operator_evidence_sections(query: str) -> dict[str, Any]:
    needle = str(query).strip().lower()
    index = build_operator_evidence_navigation_index()
    matches = []

    for route in index["routes"]:
        haystack = " ".join([
            route["section_id"],
            route["title"],
            route["artifact"],
        ]).lower()
        if needle and needle in haystack:
            matches.append(route)

    return {
        "ok": True,
        "type": "operator_evidence_section_search",
        "query": query,
        "match_count": len(matches),
        "matches": matches,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
    }


def evaluate_operator_evidence_navigation_safety() -> dict[str, Any]:
    index = build_operator_evidence_navigation_index()
    all_routes_read_only = all(route["read_only"] is True for route in index["routes"])
    passed = (
        index["paper_only"] is True
        and index["local_only"] is True
        and index["read_only"] is True
        and index["deploy_enabled"] is False
        and index["real_trading_enabled"] is False
        and index["operator_review_required"] is True
        and all_routes_read_only
    )
    return {
        "ok": passed,
        "type": "operator_evidence_navigation_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "route_count": index["route_count"],
        "all_routes_read_only": all_routes_read_only,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_operator_evidence_navigation_readable_map() -> dict[str, Any]:
    index = build_operator_evidence_navigation_index()
    return {
        "ok": True,
        "type": "operator_evidence_navigation_readable_map",
        "title": "P18 Local Evidence Console Navigation Map",
        "release_tag": index["release_tag"],
        "root_route": index["root_route"],
        "items": [
            {
                "label": route["title"],
                "route": route["route"],
                "artifact": route["artifact"],
                "read_only": route["read_only"],
            }
            for route in index["routes"]
        ],
        "item_count": index["route_count"],
        "safety_summary": "paper-only, local-only, read-only, no deploy, no real trading",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_operator_evidence_navigation_export_packet() -> dict[str, Any]:
    index = build_operator_evidence_navigation_index()
    overview = build_operator_evidence_navigation_overview()
    readable_map = build_operator_evidence_navigation_readable_map()
    safety_gate = evaluate_operator_evidence_navigation_safety()
    return {
        "ok": safety_gate["ok"],
        "type": "operator_evidence_navigation_export_packet",
        "phase": "P18-D7-D9",
        "release_tag": index["release_tag"],
        "index": index,
        "overview": overview,
        "readable_map": readable_map,
        "safety_gate": safety_gate,
        "export_mode": "LOCAL_STATIC_READ_ONLY",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_operator_evidence_navigation_closeout_checkpoint() -> dict[str, Any]:
    packet = build_operator_evidence_navigation_export_packet()
    return {
        "ok": packet["ok"],
        "type": "operator_evidence_navigation_closeout_checkpoint",
        "phase": "P18-D7-D9",
        "release_tag": packet["release_tag"],
        "completed": [
            "navigation_readable_map",
            "navigation_export_packet",
            "navigation_closeout_checkpoint",
        ],
        "route_count": packet["index"]["route_count"],
        "safety_gate_status": packet["safety_gate"]["status"],
        "next_phase_candidate": "P19 Local Evidence Console Archive View",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
