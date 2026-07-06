from apps.watchlist_lifecycle_app_1.decision_model import (
    evaluate_watchlist_lifecycle_batch,
    evaluate_watchlist_lifecycle_state,
    validate_watchlist_lifecycle_evaluation,
)
from apps.watchlist_lifecycle_app_1.lifecycle_schema import (
    ACTIVE_WATCH,
    DROP_REVIEW,
    ENTRY_REVIEW,
    REVIEW_REQUIRED,
    STALE_REVIEW,
)


def _manifest(present=1, missing=0):
    return {
        "stage_id": "WATCHLIST-LIFECYCLE-D2",
        "manifest_id": "manifest-001",
        "source_record_count": present + missing,
        "present_source_count": present,
        "missing_source_count": missing,
        "missing_upstream_sources": [],
        "represented_upstream_sources": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
    }


def test_d4_new_candidate_starts_at_entry_review():
    evaluation = evaluate_watchlist_lifecycle_state(
        candidate={
            "candidate_id": "candidate-001",
            "symbol": "BTCUSDT",
            "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
        },
        source_manifest=_manifest(),
        previous_state=None,
    )

    assert evaluation["selected_state"] == ENTRY_REVIEW
    assert evaluation["lifecycle_record_valid"] is True
    assert evaluation["trade_action_allowed"] is False
    assert evaluation["real_execution_allowed"] is False

    validation = validate_watchlist_lifecycle_evaluation(evaluation)

    assert validation["valid"] is True
    assert validation["issues"] == []


def test_d4_previous_review_candidate_can_become_active_watch_when_sources_are_healthy():
    evaluation = evaluate_watchlist_lifecycle_state(
        candidate={
            "candidate_id": "candidate-002",
            "symbol": "AAPL",
            "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
        },
        source_manifest=_manifest(),
        previous_state=ENTRY_REVIEW,
    )

    assert evaluation["selected_state"] == ACTIVE_WATCH
    assert evaluation["lifecycle_record"]["transition_allowed"] is True


def test_d4_missing_or_stale_source_selects_stale_review():
    evaluation = evaluate_watchlist_lifecycle_state(
        candidate={
            "candidate_id": "candidate-003",
            "symbol": "MSFT",
            "risk_flags": ["SOURCE_STALE"],
            "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
        },
        source_manifest=_manifest(present=1, missing=1),
        previous_state=ACTIVE_WATCH,
    )

    assert evaluation["selected_state"] == STALE_REVIEW
    assert "source context requires stale review" in evaluation["decision_reasons"]


def test_d4_governance_or_signal_block_selects_review_required():
    evaluation = evaluate_watchlist_lifecycle_state(
        candidate={
            "candidate_id": "candidate-004",
            "symbol": "TSLA",
            "governance_status": "BLOCKED",
            "signal_validation_status": "PASS",
            "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
        },
        source_manifest=_manifest(),
        previous_state=ACTIVE_WATCH,
    )

    assert evaluation["selected_state"] == REVIEW_REQUIRED
    assert evaluation["trade_action_allowed"] is False
    assert evaluation["automatic_position_sizing_allowed"] is False


def test_d4_drop_risk_flag_selects_drop_review():
    evaluation = evaluate_watchlist_lifecycle_state(
        candidate={
            "candidate_id": "candidate-005",
            "symbol": "ETHUSDT",
            "risk_flags": ["DROP_REQUESTED"],
            "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
        },
        source_manifest=_manifest(),
        previous_state=ACTIVE_WATCH,
    )

    assert evaluation["selected_state"] == DROP_REVIEW
    assert evaluation["lifecycle_record"]["trade_action_allowed"] is False


def test_d4_batch_summary_counts_states_without_trade_surfaces():
    batch = evaluate_watchlist_lifecycle_batch(
        candidates=[
            {
                "candidate_id": "candidate-001",
                "symbol": "BTCUSDT",
                "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
            },
            {
                "candidate_id": "candidate-002",
                "symbol": "AAPL",
                "previous_state": ENTRY_REVIEW,
                "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
            },
            {
                "candidate_id": "candidate-003",
                "symbol": "ETHUSDT",
                "previous_state": ACTIVE_WATCH,
                "risk_flags": ["DROP_REQUESTED"],
                "source_app_ids": ["STOCK-APP-1", "MODEL-GOVERNANCE-APP-1"],
            },
        ],
        source_manifest=_manifest(),
    )

    assert batch["candidate_count"] == 3
    assert batch["state_counts"][ENTRY_REVIEW] == 1
    assert batch["state_counts"][ACTIVE_WATCH] == 1
    assert batch["state_counts"][DROP_REVIEW] == 1
    assert batch["trade_action_allowed"] is False
    assert batch["position_management_allowed"] is False
    assert batch["future_return_prediction_allowed"] is False
