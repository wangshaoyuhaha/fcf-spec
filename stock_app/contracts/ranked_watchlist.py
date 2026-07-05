"""STOCK-APP-D6 ranked watchlist and candidate report handoff.

This module produces operator-review handoff artifacts from scored candidates.
It does not create buy/sell instructions and does not enable real trading.
"""

import json
from datetime import datetime
from datetime import timezone
from pathlib import Path

from stock_app.contracts.limit_up_potential import HIGH_POTENTIAL
from stock_app.contracts.limit_up_potential import LOW_POTENTIAL
from stock_app.contracts.limit_up_potential import MEDIUM_POTENTIAL
from stock_app.contracts.limit_up_potential import REJECTED_LEVEL
from stock_app.contracts.limit_up_potential import WATCH_ONLY_LEVEL
from stock_app.contracts.limit_up_potential import evaluate_limit_up_potential

DISPLAY_LEVELS = {HIGH_POTENTIAL, MEDIUM_POTENTIAL, LOW_POTENTIAL, WATCH_ONLY_LEVEL}


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def _sort_key(item):
    level_rank = {
        HIGH_POTENTIAL: 0,
        MEDIUM_POTENTIAL: 1,
        LOW_POTENTIAL: 2,
        WATCH_ONLY_LEVEL: 3,
        REJECTED_LEVEL: 4,
    }
    return (level_rank.get(item["potential_level"], 9), -float(item["limit_up_potential_score"]))


def build_ranked_watchlist(records, trade_date="UNKNOWN", source_manifest_id=None):
    """Build ranked watchlist from raw candidate records."""
    evaluated = [evaluate_limit_up_potential(record) for record in records]
    ranked = sorted(evaluated, key=_sort_key)

    watchlist = []
    excluded = []
    for index, item in enumerate(ranked, start=1):
        row = {
            "rank": index,
            "symbol": item["symbol"],
            "name": item["name"],
            "limit_up_potential_score": item["limit_up_potential_score"],
            "potential_level": item["potential_level"],
            "score_breakdown": item["score_breakdown"],
            "reason_codes": item["reason_codes"],
            "risk_flags": item["risk_flags"],
            "data_quality_state": item["data_quality_state"],
            "confidence_level": item["confidence_level"],
            "data_sources": item["data_sources"],
            "operator_review_required": True,
            "paper_only": True,
            "real_action_blocked": True,
        }
        if item["potential_level"] == REJECTED_LEVEL:
            excluded.append(row)
        else:
            watchlist.append(row)

    return {
        "app": "STOCK-APP",
        "contract_version": "STOCK_APP_RANKED_WATCHLIST_V1",
        "stage": "STOCK-APP-D6",
        "trade_date": trade_date,
        "source_manifest_id": source_manifest_id,
        "generated_at_utc": _utc_now(),
        "input_count": len(records),
        "candidate_count": len(watchlist),
        "excluded_count": len(excluded),
        "ranked_watchlist": watchlist,
        "excluded": excluded,
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "guaranteed_limit_up_claim_allowed": False,
    }


def build_candidate_report(records, trade_date="UNKNOWN", source_manifest_id=None):
    """Build candidate report and operator review packet."""
    watchlist = build_ranked_watchlist(records, trade_date, source_manifest_id)
    level_counts = {
        HIGH_POTENTIAL: 0,
        MEDIUM_POTENTIAL: 0,
        LOW_POTENTIAL: 0,
        WATCH_ONLY_LEVEL: 0,
        REJECTED_LEVEL: len(watchlist["excluded"]),
    }
    for item in watchlist["ranked_watchlist"]:
        level_counts[item["potential_level"]] = level_counts.get(item["potential_level"], 0) + 1

    return {
        "app": "STOCK-APP",
        "contract_version": "STOCK_APP_CANDIDATE_REPORT_V1",
        "stage": "STOCK-APP-D6",
        "trade_date": trade_date,
        "source_manifest_id": source_manifest_id,
        "generated_at_utc": _utc_now(),
        "summary": {
            "input_count": watchlist["input_count"],
            "candidate_count": watchlist["candidate_count"],
            "excluded_count": watchlist["excluded_count"],
            "level_counts": level_counts,
        },
        "ranked_watchlist": watchlist["ranked_watchlist"],
        "excluded": watchlist["excluded"],
        "operator_review_packet": {
            "operator_review_required": True,
            "review_before_any_action": True,
            "ai_can_explain_only": True,
            "ai_can_modify_score": False,
            "real_action_blocked": True,
        },
        "handoff_to_ai_context": {
            "allowed": True,
            "read_only": True,
            "schema_validation_required": True,
            "score_modification_allowed": False,
        },
        "paper_only": True,
        "real_action_blocked": True,
        "buy_instruction_allowed": False,
        "sell_instruction_allowed": False,
        "guaranteed_limit_up_claim_allowed": False,
    }


def write_candidate_report(records, output_path, trade_date="UNKNOWN", source_manifest_id=None):
    """Write candidate report JSON artifact."""
    report = build_candidate_report(records, trade_date, source_manifest_id)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "ok": True,
        "output_path": str(path),
        "candidate_count": report["summary"]["candidate_count"],
        "excluded_count": report["summary"]["excluded_count"],
        "operator_review_required": True,
        "paper_only": True,
        "real_action_blocked": True,
    }
