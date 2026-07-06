from copy import deepcopy

from apps.portfolio_review_app_1.contract import get_portfolio_review_contract, validate_portfolio_review_contract
from apps.portfolio_review_app_1.exposure_schema import (
    create_paper_exposure_record,
    validate_paper_exposure_record,
)
from apps.portfolio_review_app_1.final_handoff import (
    COMPLETED_STAGES,
    build_portfolio_review_final_handoff,
    validate_portfolio_review_final_handoff,
)
from apps.portfolio_review_app_1.review_model import (
    build_paper_portfolio_review,
    validate_paper_portfolio_review,
)
from apps.portfolio_review_app_1.review_packet import (
    build_portfolio_review_packet,
    validate_portfolio_review_packet,
)
from apps.portfolio_review_app_1.source_loader import (
    build_portfolio_review_source_manifest,
    validate_portfolio_review_source_manifest,
)


def _source_manifest():
    return build_portfolio_review_source_manifest(root_path=".")


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
            "risk_flags": [],
        },
    ]


def test_portfolio_review_contract_preserves_safety_boundary():
    contract = get_portfolio_review_contract()
    validation = validate_portfolio_review_contract(contract)

    assert validation["valid"] is True
    assert validation["issues"] == []

    flags = contract["boundary_flags"]
    assert flags["paper_only"] is True
    assert flags["operator_review_required"] is True
    assert flags["position_management_allowed"] is False
    assert flags["automatic_position_sizing_allowed"] is False
    assert flags["automatic_portfolio_action_allowed"] is False
    assert flags["trade_action_allowed"] is False
    assert flags["future_return_prediction_allowed"] is False


def test_portfolio_review_source_manifest_is_metadata_only():
    manifest = _source_manifest()
    validation = validate_portfolio_review_source_manifest(manifest)

    assert validation["valid"] is True
    assert manifest["content_loaded"] is False
    assert manifest["read_only"] is True
    assert manifest["position_management_allowed"] is False
    assert manifest["automatic_position_sizing_allowed"] is False
    assert manifest["trade_action_allowed"] is False
    assert manifest["source_record_count"] == 12


def test_paper_exposure_record_rejects_position_and_trade_surfaces():
    record = create_paper_exposure_record(
        exposure_record_id="exp-001",
        candidate_id="candidate-001",
        symbol="BTCUSDT",
        asset_class="CRYPTO",
        sector="DIGITAL_ASSET",
        theme="BTC",
        paper_exposure_state="PAPER_EXPOSURE_REVIEW",
        review_reason="review only",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_paper_exposure_record(record)

    assert validation["valid"] is True
    assert record["position_management_allowed"] is False
    assert record["position_size_suggestion_allowed"] is False
    assert record["trade_action_allowed"] is False
    assert record["future_return_prediction_allowed"] is False


def test_paper_exposure_record_validator_catches_mutation():
    record = create_paper_exposure_record(
        exposure_record_id="exp-002",
        candidate_id="candidate-002",
        symbol="AAPL",
        asset_class="STOCK",
        sector="TECH",
        theme="MEGA_CAP",
        paper_exposure_state="PAPER_EXPOSURE_REVIEW",
        review_reason="review only",
        created_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(record)
    mutated["automatic_position_sizing_allowed"] = True
    mutated["buy_instruction_allowed"] = True

    validation = validate_paper_exposure_record(mutated)

    assert validation["valid"] is False
    assert "automatic_position_sizing_allowed must be false" in validation["issues"]
    assert "buy_instruction_allowed must be false" in validation["issues"]


def test_paper_portfolio_review_builds_review_without_position_sizing():
    review = build_paper_portfolio_review(candidates=_candidates(), source_manifest=_source_manifest())
    validation = validate_paper_portfolio_review(review)

    assert validation["valid"] is True
    assert review["candidate_count"] == 3
    assert review["position_management_allowed"] is False
    assert review["position_size_suggestion_allowed"] is False
    assert review["portfolio_rebalance_allowed"] is False
    assert review["trade_action_allowed"] is False
    assert review["future_return_prediction_allowed"] is False


def test_portfolio_review_packet_is_archive_ready_and_review_only():
    packet = build_portfolio_review_packet(
        packet_id="portfolio-review-packet-001",
        candidates=_candidates(),
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_portfolio_review_packet(packet)

    assert validation["valid"] is True
    assert packet["archive_ready"] is True
    assert packet["operator_review_required"] is True
    assert packet["automatic_position_sizing_allowed"] is False
    assert packet["automatic_portfolio_action_allowed"] is False
    assert packet["trade_action_allowed"] is False


def test_portfolio_review_final_handoff_is_merge_review_only():
    packet = build_portfolio_review_packet(
        packet_id="portfolio-review-packet-002",
        candidates=_candidates(),
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_portfolio_review_final_handoff(
        packet=packet,
        handoff_id="portfolio-review-handoff-001",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    validation = validate_portfolio_review_final_handoff(handoff)

    assert validation["valid"] is True
    assert handoff["completed_stages"] == COMPLETED_STAGES
    assert handoff["branch_ready_for_merge_review"] is True
    assert handoff["tag_allowed"] is False
    assert handoff["release_allowed"] is False
    assert handoff["deploy_allowed"] is False


def test_portfolio_review_final_handoff_rejects_release_or_execution_mutation():
    packet = build_portfolio_review_packet(
        packet_id="portfolio-review-packet-003",
        candidates=_candidates(),
        source_manifest=_source_manifest(),
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    handoff = build_portfolio_review_final_handoff(
        packet=packet,
        handoff_id="portfolio-review-handoff-002",
        generated_at_utc="2026-07-06T00:00:00+00:00",
    )

    mutated = deepcopy(handoff)
    mutated["real_execution_allowed"] = True
    mutated["release_allowed"] = True
    mutated["deploy_allowed"] = True

    validation = validate_portfolio_review_final_handoff(mutated)

    assert validation["valid"] is False
    assert "real_execution_allowed must be false" in validation["issues"]
    assert "release_allowed must be false" in validation["issues"]
    assert "deploy_allowed must be false" in validation["issues"]
