from copy import deepcopy

from apps.risk_exposure_app_1.contract import get_risk_exposure_contract, validate_risk_exposure_contract
from apps.risk_exposure_app_1.exposure_schema import (
    create_paper_risk_exposure_record,
    validate_paper_risk_exposure_record,
)
from apps.risk_exposure_app_1.final_handoff import (
    COMPLETED_STAGES,
    build_risk_exposure_final_handoff,
    validate_risk_exposure_final_handoff,
)
from apps.risk_exposure_app_1.review_model import (
    build_paper_risk_exposure_review,
    validate_paper_risk_exposure_review,
)
from apps.risk_exposure_app_1.review_packet import (
    build_risk_exposure_packet,
    validate_risk_exposure_packet,
)
from apps.risk_exposure_app_1.source_loader import (
    build_risk_exposure_source_manifest,
    validate_risk_exposure_source_manifest,
)


def _source_manifest():
    return build_risk_exposure_source_manifest(root_path=".")


def _candidates():
    return [
        {
            "candidate_id": "candidate-001",
            "symbol": "BTCUSDT",
            "asset_class": "CRYPTO",
            "sector": "DIGITAL_ASSET",
            "theme": "BTC",
            "risk_flags": [],
        },
        {
            "candidate_id": "candidate-002",
            "symbol": "AAPL",
            "asset_class": "STOCK",
            "sector": "TECH",
            "theme": "MEGA_CAP",
            "risk_flags": [],
        },
        {
            "candidate_id": "candidate-003",
            "symbol": "MSFT",
            "asset_class": "STOCK",
            "sector": "TECH",
            "theme": "MEGA_CAP",
            "risk_flags": ["MODEL_GOVERNANCE_REVIEW"],
        },
    ]


def test_risk_exposure_contract_preserves_safety_boundary():
    contract = get_risk_exposure_contract()
    validation = validate_risk_exposure_contract(contract)

    assert validation["valid"] is True
    assert validation["issues"] == []

    flags = contract["boundary_flags"]
    assert flags["paper_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["real_risk_management_allowed"] is False
    assert flags["position_management_allowed"] is False
    assert flags["automatic_position_sizing_allowed"] is False
    assert flags["risk_based_rebalance_allowed"] is False
    assert flags["trade_action_allowed"] is False
    assert flags["future_return_prediction_allowed"] is False


def test_risk_exposure_source_manifest_is_metadata_only():
    manifest = _source_manifest()
    validation = validate_risk_exposure_source_manifest(manifest)

    assert validation["valid"] is True
    assert manifest["content_loaded"] is False
    assert manifest["read_only"] is True
    assert manifest["real_risk_management_allowed"] is False
    assert manifest["position_management_allowed"] is False
    assert manifest["automatic_position_sizing_allowed"] is False
    assert manifest["trade_action_allowed"] is False
    assert manifest["source_record_count"] == 13


def test_paper_risk_exposure_record_rejects_execution_and_risk_flag_mutation():
    record = create_paper_risk_exposure_record(
        risk_exposure_record_id="risk-exp-001",
        candidate_id="candidate-001",
        symbol="BTCUSDT",
        asset_class="CRYPTO",
        sector="DIGITAL_ASSET",
        theme="BTC",
        risk_exposure_state="PAPER_RISK_REVIEW",
        risk_review_reason="review only",
        observed_risk_flags=[],
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_paper_risk_exposure_record(record)

    assert validation["valid"] is True
    assert record["real_risk_management_allowed"] is False
    assert record["position_management_allowed"] is False
    assert record["trade_action_allowed"] is False
    assert record["risk_flag_deletion_allowed"] is False
    assert record["risk_flag_downgrade_allowed"] is False


def test_paper_risk_exposure_record_validator_catches_mutation():
    record = create_paper_risk_exposure_record(
        risk_exposure_record_id="risk-exp-002",
        candidate_id="candidate-002",
        symbol="AAPL",
        asset_class="STOCK",
        sector="TECH",
        theme="MEGA_CAP",
        risk_exposure_state="PAPER_RISK_REVIEW",
        risk_review_reason="review only",
        observed_risk_flags=[],
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(record)
    mutated["real_risk_management_allowed"] = True
    mutated["risk_flag_deletion_allowed"] = True
    mutated["sell_instruction_allowed"] = True

    validation = validate_paper_risk_exposure_record(mutated)

    assert validation["valid"] is False
    assert "real_risk_management_allowed must be false" in validation["issues"]
    assert "risk_flag_deletion_allowed must be false" in validation["issues"]
    assert "sell_instruction_allowed must be false" in validation["issues"]


def test_paper_risk_exposure_review_builds_review_without_controls_or_sizing():
    review = build_paper_risk_exposure_review(candidates=_candidates(), source_manifest=_source_manifest())
    validation = validate_paper_risk_exposure_review(review)

    assert validation["valid"] is True
    assert review["candidate_count"] == 3
    assert review["real_risk_management_allowed"] is False
    assert review["position_management_allowed"] is False
    assert review["position_size_suggestion_allowed"] is False
    assert review["risk_based_rebalance_allowed"] is False
    assert review["trade_action_allowed"] is False
    assert review["future_return_prediction_allowed"] is False
    assert "GOVERNANCE_RISK_REVIEW" in review["state_counts"]


def test_risk_exposure_packet_is_archive_ready_and_review_only():
    packet = build_risk_exposure_packet(
        packet_id="risk-exposure-packet-001",
        candidates=_candidates(),
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_risk_exposure_packet(packet)

    assert validation["valid"] is True
    assert packet["archive_ready"] is True
    assert packet["operator_review_required"] is True
    assert packet["real_risk_management_allowed"] is False
    assert packet["automatic_position_sizing_allowed"] is False
    assert packet["automatic_portfolio_action_allowed"] is False
    assert packet["trade_action_allowed"] is False


def test_risk_exposure_final_handoff_is_merge_review_only():
    packet = build_risk_exposure_packet(
        packet_id="risk-exposure-packet-002",
        candidates=_candidates(),
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_risk_exposure_final_handoff(
        packet=packet,
        handoff_id="risk-exposure-handoff-001",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_risk_exposure_final_handoff(handoff)

    assert validation["valid"] is True
    assert handoff["completed_stages"] == COMPLETED_STAGES
    assert handoff["branch_ready_for_merge_review"] is True
    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False


def test_risk_exposure_final_handoff_rejects_release_execution_or_rebalance_mutation():
    packet = build_risk_exposure_packet(
        packet_id="risk-exposure-packet-003",
        candidates=_candidates(),
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_risk_exposure_final_handoff(
        packet=packet,
        handoff_id="risk-exposure-handoff-002",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(handoff)
    mutated["real_execution_allowed"] = True
    mutated["risk_based_rebalance_allowed"] = True
    mutated["release_allowed"] = True
    mutated["deploy_allowed"] = True

    validation = validate_risk_exposure_final_handoff(mutated)

    assert validation["valid"] is False
    assert "real_execution_allowed must be false" in validation["issues"]
    assert "risk_based_rebalance_allowed must be false" in validation["issues"]
    assert "release_allowed must be false" in validation["issues"]
    assert "deploy_allowed must be false" in validation["issues"]
