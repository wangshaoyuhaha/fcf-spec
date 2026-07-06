from copy import deepcopy

from apps.watchlist_lifecycle_app_1.lifecycle_packet import (
    build_watchlist_lifecycle_packet,
    summarize_watchlist_lifecycle_packet,
    validate_watchlist_lifecycle_packet,
)


def _manifest():
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
            for item in [
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
        ],
        "source_record_count": 11,
        "present_source_count": 0,
        "missing_source_count": 11,
        "represented_upstream_sources": [
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
        ],
        "missing_upstream_sources": [],
    }


def test_d5_packet_builds_valid_paper_review_packet():
    packet = build_watchlist_lifecycle_packet(
        packet_id="wl-packet-001",
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

    assert packet["candidate_count"] == 2
    assert packet["source_manifest_valid"] is True
    assert packet["invalid_evaluation_count"] == 0
    assert packet["archive_ready"] is True
    assert packet["operator_review_required"] is True
    assert packet["trade_action_allowed"] is False
    assert packet["real_execution_allowed"] is False
    assert packet["position_management_allowed"] is False

    validation = validate_watchlist_lifecycle_packet(packet)

    assert validation["valid"] is True
    assert validation["issues"] == []


def test_d5_packet_summary_keeps_only_review_metadata():
    packet = build_watchlist_lifecycle_packet(
        packet_id="wl-packet-002",
        source_manifest=_manifest(),
        candidates=[
            {
                "candidate_id": "candidate-001",
                "symbol": "BTCUSDT",
                "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
            }
        ],
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    summary = summarize_watchlist_lifecycle_packet(packet)

    assert summary["packet_id"] == "wl-packet-002"
    assert summary["candidate_count"] == 1
    assert summary["operator_review_required"] is True
    assert summary["trade_action_allowed"] is False
    assert summary["real_execution_allowed"] is False
    assert summary["position_management_allowed"] is False
    assert summary["future_return_prediction_allowed"] is False
    assert summary["guaranteed_performance_claim_allowed"] is False
    assert "evaluations" not in summary
    assert "source_manifest" not in summary


def test_d5_packet_validator_rejects_trade_and_position_surfaces():
    packet = build_watchlist_lifecycle_packet(
        packet_id="wl-packet-003",
        source_manifest=_manifest(),
        candidates=[
            {
                "candidate_id": "candidate-001",
                "symbol": "BTCUSDT",
                "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
            }
        ],
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(packet)
    mutated["trade_action_allowed"] = True
    mutated["automatic_position_sizing_allowed"] = True
    mutated["future_return_prediction_allowed"] = True

    validation = validate_watchlist_lifecycle_packet(mutated)

    assert validation["valid"] is False
    assert "trade_action_allowed must be false" in validation["issues"]
    assert "automatic_position_sizing_allowed must be false" in validation["issues"]
    assert "future_return_prediction_allowed must be false" in validation["issues"]


def test_d5_packet_validator_rejects_invalid_evaluation_count():
    packet = build_watchlist_lifecycle_packet(
        packet_id="wl-packet-004",
        source_manifest=_manifest(),
        candidates=[
            {
                "candidate_id": "candidate-001",
                "symbol": "BTCUSDT",
                "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
            }
        ],
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(packet)
    mutated["invalid_evaluation_count"] = 1
    mutated["archive_ready"] = False

    validation = validate_watchlist_lifecycle_packet(mutated)

    assert validation["valid"] is False
    assert "invalid_evaluation_count must be zero" in validation["issues"]
