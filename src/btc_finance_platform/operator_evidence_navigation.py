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
