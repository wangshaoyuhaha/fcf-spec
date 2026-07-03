from __future__ import annotations

from typing import Any

from btc_finance_platform.operator_evidence_navigation import build_operator_evidence_navigation_closeout_checkpoint
from btc_finance_platform.operator_evidence_export import build_local_evidence_export_handoff_packet


def build_operator_evidence_archive_index() -> dict[str, Any]:
    return {
        "ok": True,
        "type": "operator_evidence_archive_index",
        "phase": "P19-D1-D3",
        "release_tag": "v14-learning-engine-paper",
        "archives": [
            {"archive_id": "p14_release", "title": "P14 Learning Engine Paper Release", "status": "RELEASED"},
            {"archive_id": "p15_post_release", "title": "P15 Post Release Continuity", "status": "COMPLETED"},
            {"archive_id": "p16_evidence_console", "title": "P16 Operator Evidence Console", "status": "COMPLETED"},
            {"archive_id": "p17_export_files", "title": "P17 Local Evidence Export Files", "status": "COMPLETED"},
            {"archive_id": "p18_navigation", "title": "P18 Local Evidence Navigation", "status": "COMPLETED"},
        ],
        "archive_count": 5,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def resolve_operator_evidence_archive(archive_id: str) -> dict[str, Any]:
    index = build_operator_evidence_archive_index()
    lookup = {item["archive_id"]: item for item in index["archives"]}
    archive = lookup.get(str(archive_id).strip())

    return {
        "ok": archive is not None,
        "type": "operator_evidence_archive_resolution",
        "archive_id": archive_id,
        "archive": archive,
        "read_only": True,
        "paper_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_operator_evidence_archive_overview() -> dict[str, Any]:
    index = build_operator_evidence_archive_index()
    export_handoff = build_local_evidence_export_handoff_packet()
    navigation_closeout = build_operator_evidence_navigation_closeout_checkpoint()

    return {
        "ok": True,
        "type": "operator_evidence_archive_overview",
        "release_tag": index["release_tag"],
        "archive_count": index["archive_count"],
        "archives": index["archives"],
        "export_handoff_status": export_handoff["handoff_status"],
        "navigation_safety_gate_status": navigation_closeout["safety_gate_status"],
        "summary": "Read-only archive view for released paper evidence.",
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def build_operator_evidence_archive_timeline() -> dict[str, Any]:
    index = build_operator_evidence_archive_index()
    timeline = [
        {
            "order": idx + 1,
            "archive_id": item["archive_id"],
            "title": item["title"],
            "status": item["status"],
            "read_only": True,
        }
        for idx, item in enumerate(index["archives"])
    ]

    return {
        "ok": True,
        "type": "operator_evidence_archive_timeline",
        "release_tag": index["release_tag"],
        "timeline_count": len(timeline),
        "timeline": timeline,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }


def search_operator_evidence_archives(query: str) -> dict[str, Any]:
    needle = str(query).strip().lower()
    index = build_operator_evidence_archive_index()
    matches = []

    for archive in index["archives"]:
        haystack = " ".join([
            archive["archive_id"],
            archive["title"],
            archive["status"],
        ]).lower()
        if needle and needle in haystack:
            matches.append(archive)

    return {
        "ok": True,
        "type": "operator_evidence_archive_search",
        "query": query,
        "match_count": len(matches),
        "matches": matches,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
    }


def evaluate_operator_evidence_archive_safety() -> dict[str, Any]:
    index = build_operator_evidence_archive_index()
    overview = build_operator_evidence_archive_overview()
    all_completed_or_released = all(
        item["status"] in {"COMPLETED", "RELEASED"}
        for item in index["archives"]
    )
    passed = (
        index["paper_only"] is True
        and index["local_only"] is True
        and index["read_only"] is True
        and index["deploy_enabled"] is False
        and index["real_trading_enabled"] is False
        and overview["operator_review_required"] is True
        and all_completed_or_released
    )

    return {
        "ok": passed,
        "type": "operator_evidence_archive_safety_gate",
        "status": "PASSED" if passed else "FAILED",
        "archive_count": index["archive_count"],
        "all_completed_or_released": all_completed_or_released,
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "deploy_enabled": False,
        "real_trading_enabled": False,
        "operator_review_required": True,
    }
