from copy import deepcopy

from apps.watchlist_lifecycle_app_1.final_handoff import (
    COMPLETED_STAGES,
    build_watchlist_lifecycle_closeout_summary,
    build_watchlist_lifecycle_final_handoff,
    validate_watchlist_lifecycle_final_handoff,
)
from apps.watchlist_lifecycle_app_1.lifecycle_packet import build_watchlist_lifecycle_packet


def _manifest():
    source_names = [
        "DATA-APP-1",
        "STOCK-APP-1",
        "AI-CONTEXT-1",
        "UI-APP-1",
        "OPERATOR-REVIEW-APP-1",
        "REPORT-ARCHIVE-APP-1",
        "DATA-QUALITY-OPS-APP-1",
        "MARKET-SCENARIO-APP-1",
        "BACKTEST-REVIEW-APP-1",
        "SIGNAL-VALIDATION-APP-1",
        "MODEL-GOVERNANCE-APP-1",
    ]

    return {
        "app_id": "WATCHLIST-LIFECYCLE-APP-1",
        "stage_id": "WATCHLIST-LIFECYCLE-D2",
        "source_loader_version": "1.0.0",
        "generated_at_utc": "2026-07-06T00:00:00+00:00",
        "source_root": ".",
        "read_only": True,
        "content_loaded": False,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "operator_review_required": True,
        "source_records": [
            {
                "app_id": item,
                "source_kind": "fixture",
                "relative_path": "docs/" + item.lower(),
                "exists": False,
                "status": "MISSING",
                "path_type": "missing",
                "size_bytes": 0,
                "file_count": 0,
                "sha256": None,
                "modified_at_utc": None,
                "content_loaded": False,
                "read_only": True,
                "source_content_mutation_allowed": False,
                "source_deletion_allowed": False,
                "source_overwrite_allowed": False,
            }
            for item in source_names
        ],
        "source_record_count": len(source_names),
        "present_source_count": 0,
        "missing_source_count": len(source_names),
        "represented_upstream_sources": source_names,
        "missing_upstream_sources": [],
    }


def _packet():
    return build_watchlist_lifecycle_packet(
        packet_id="wl-packet-final",
        source_manifest=_manifest(),
        candidates=[
            {
                "candidate_id": "candidate-001",
                "symbol": "BTCUSDT",
                "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
            },
            {
                "candidate_id": "candidate-002",
                "symbol": "AAPL",
                "previous_state": "ENTRY_REVIEW",
                "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
            },
        ],
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )


def test_d6_final_handoff_builds_valid_closeout():
    handoff = build_watchlist_lifecycle_final_handoff(
        packet=_packet(),
        handoff_id="wl-handoff-001",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    assert handoff["completed_stages"] == COMPLETED_STAGES
    assert handoff["packet_valid"] is True
    assert handoff["final_closeout_ready"] is True
    assert handoff["branch_ready_for_merge_review"] is True
    assert handoff["operator_review_required"] is True
    assert handoff["core_freeze_preserved"] is True

    validation = validate_watchlist_lifecycle_final_handoff(handoff)

    assert validation["valid"] is True
    assert validation["issues"] == []


def test_d6_closeout_summary_excludes_large_packet_payload():
    handoff = build_watchlist_lifecycle_final_handoff(
        packet=_packet(),
        handoff_id="wl-handoff-002",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    summary = build_watchlist_lifecycle_closeout_summary(handoff)

    assert summary["handoff_id"] == "wl-handoff-002"
    assert summary["completed_stage_count"] == 6
    assert summary["packet_valid"] is True
    assert summary["final_closeout_ready"] is True
    assert summary["branch_ready_for_merge_review"] is True
    assert summary["trade_action_allowed"] is False
    assert summary["real_execution_allowed"] is False
    assert summary["position_management_allowed"] is False
    assert summary["tag_allowed"] is False
    assert summary["release_allowed"] is False
    assert summary["deploy_allowed"] is False
    assert "packet_summary" not in summary


def test_d6_final_handoff_disables_all_execution_and_release_surfaces():
    handoff = build_watchlist_lifecycle_final_handoff(
        packet=_packet(),
        handoff_id="wl-handoff-003",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    for key in [
        "operator_review_bypass_allowed",
        "p48_core_expansion_allowed",
        "p1_p47_core_mutation_allowed",
        "source_content_mutation_allowed",
        "source_deletion_allowed",
        "source_overwrite_allowed",
        "score_mutation_allowed",
        "reason_code_mutation_allowed",
        "risk_flag_deletion_allowed",
        "trade_action_allowed",
        "buy_instruction_allowed",
        "sell_instruction_allowed",
        "order_ticket_allowed",
        "real_execution_allowed",
        "broker_connection_allowed",
        "exchange_connection_allowed",
        "api_key_storage_allowed",
        "wallet_private_key_access_allowed",
        "real_account_access_allowed",
        "real_position_access_allowed",
        "position_management_allowed",
        "automatic_position_sizing_allowed",
        "automatic_portfolio_action_allowed",
        "future_return_prediction_allowed",
        "guaranteed_performance_claim_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ]:
        assert handoff[key] is False


def test_d6_final_handoff_validator_rejects_release_or_trade_mutation():
    handoff = build_watchlist_lifecycle_final_handoff(
        packet=_packet(),
        handoff_id="wl-handoff-004",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(handoff)
    mutated["trade_action_allowed"] = True
    mutated["real_execution_allowed"] = True
    mutated["release_allowed"] = True
    mutated["deploy_allowed"] = True

    validation = validate_watchlist_lifecycle_final_handoff(mutated)

    assert validation["valid"] is False
    assert "trade_action_allowed must be false" in validation["issues"]
    assert "real_execution_allowed must be false" in validation["issues"]
    assert "release_allowed must be false" in validation["issues"]
    assert "deploy_allowed must be false" in validation["issues"]
