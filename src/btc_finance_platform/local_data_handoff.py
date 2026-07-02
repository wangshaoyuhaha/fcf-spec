import json
from datetime import datetime
from datetime import timezone
from pathlib import Path
from typing import Any

from btc_finance_platform.local_data_bridge import build_local_data_audit_report
from btc_finance_platform.local_data_bridge import build_local_paper_analysis_inputs


PAPER_ONLY_FLAGS = {
    "paper_only": True,
    "real_exchange_api": False,
    "real_api_key_required": False,
    "wallet_private_key_required": False,
    "real_order": False,
    "real_execution": False,
    "real_balance": False,
    "real_position": False,
    "real_money_impact": False,
    "operator_review_required": True,
}


def _paper_flags() -> dict[str, Any]:
    return dict(PAPER_ONLY_FLAGS)


def _is_positive_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and value > 0


def build_local_data_quality_gate(file_paths: list[Any]) -> dict[str, Any]:
    analysis_inputs = build_local_paper_analysis_inputs(file_paths)
    audit_report = build_local_data_audit_report(file_paths)
    items = analysis_inputs["items"]

    checks = {
        "has_items": len(items) > 0,
        "all_symbols_present": all(bool(item["symbol"]) for item in items),
        "all_prices_positive": all(_is_positive_number(item["price"]) for item in items),
        "all_reference_prices_positive": all(
            _is_positive_number(item["reference_price"]) for item in items
        ),
        "audit_report_ok": audit_report["ok"] is True,
        "source_manifest_present": "source_manifest" in analysis_inputs,
        "source_files_have_sha256": audit_report["checks"]["source_files_have_sha256"] is True,
        "record_count_matches_manifest": audit_report["checks"]["record_count_matches_manifest"] is True,
        "paper_only_preserved": analysis_inputs["paper_only"] is True,
        "no_real_exchange_api": analysis_inputs["real_exchange_api"] is False,
        "no_real_api_key_required": analysis_inputs["real_api_key_required"] is False,
        "no_wallet_private_key_required": analysis_inputs["wallet_private_key_required"] is False,
        "no_real_order": analysis_inputs["real_order"] is False,
        "no_real_execution": analysis_inputs["real_execution"] is False,
        "no_real_balance": analysis_inputs["real_balance"] is False,
        "no_real_position": analysis_inputs["real_position"] is False,
        "no_real_money_impact": analysis_inputs["real_money_impact"] is False,
        "operator_review_required": analysis_inputs["operator_review_required"] is True,
    }

    return {
        "ok": all(checks.values()),
        "type": "local_data_quality_gate",
        "gate": "pass" if all(checks.values()) else "fail",
        "count": analysis_inputs["count"],
        "symbols": analysis_inputs["symbols"],
        "checks": checks,
        **_paper_flags(),
    }


def build_local_analysis_handoff_package(file_paths: list[Any]) -> dict[str, Any]:
    analysis_inputs = build_local_paper_analysis_inputs(file_paths)
    audit_report = build_local_data_audit_report(file_paths)
    quality_gate = build_local_data_quality_gate(file_paths)

    return {
        "ok": quality_gate["ok"] is True and audit_report["ok"] is True,
        "type": "local_analysis_handoff_package",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "gate": quality_gate["gate"],
        "count": analysis_inputs["count"],
        "symbols": analysis_inputs["symbols"],
        "analysis_inputs": analysis_inputs,
        "audit_report": audit_report,
        "quality_gate": quality_gate,
        "next_step": "paper_analysis_only_after_operator_review",
        **_paper_flags(),
    }


def write_local_analysis_handoff_package(
    file_paths: list[Any],
    output_path: Any,
) -> dict[str, Any]:
    package = build_local_analysis_handoff_package(file_paths)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(package, indent=2, sort_keys=True), encoding="utf-8")

    return {
        "ok": True,
        "type": "local_analysis_handoff_package_written",
        "output_file": str(path),
        "package": package,
        **_paper_flags(),
    }
