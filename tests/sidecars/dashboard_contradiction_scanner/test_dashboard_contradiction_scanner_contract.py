"""Tests for the dashboard contradiction scanner boundary contract."""

from fcf.sidecars.dashboard_contradiction_scanner import (
    build_contract,
    validate_contract,
)


def test_contract_is_valid() -> None:
    contract = build_contract()

    assert validate_contract(contract) == []
    assert contract["app_id"] == "DASHBOARD-CONTRADICTION-SCANNER-APP-1"
    assert contract["output_kind"] == "PAPER_ONLY_CONTRADICTION_FINDINGS"
    assert contract["human_review_required"] is True
    assert contract["archive_required"] is True


def test_safety_boundaries_are_locked() -> None:
    boundaries = build_contract()["boundaries"]

    assert boundaries["paper_only"] is True
    assert boundaries["local_only"] is True
    assert boundaries["read_only"] is True
    assert boundaries["sidecar_only"] is True
    assert boundaries["operator_review_required"] is True

    assert boundaries["core_mutation_allowed"] is False
    assert boundaries["p48_core_expansion_allowed"] is False
    assert boundaries["source_mutation_allowed"] is False
    assert boundaries["risk_flag_deletion_allowed"] is False
    assert boundaries["risk_flag_downgrade_allowed"] is False
    assert boundaries["automatic_review_pass_allowed"] is False
    assert boundaries["real_trading_allowed"] is False
    assert boundaries["real_execution_allowed"] is False


def test_traceability_fields_are_required() -> None:
    fields = set(build_contract()["required_trace_fields"])

    assert fields == {
        "correlation_id",
        "research_run_id",
        "source_artifact_ids",
        "validation_baseline_id",
    }


def test_scanner_defines_governance_contradictions() -> None:
    contradiction_classes = set(build_contract()["contradiction_classes"])

    assert "RISK_FLAG_MISSING" in contradiction_classes
    assert "RISK_FLAG_DOWNGRADED" in contradiction_classes
    assert "SUMMARY_RAW_CONFLICT" in contradiction_classes
    assert "REVIEW_STATE_MISMATCH" in contradiction_classes
    assert "LIFECYCLE_STATE_MISMATCH" in contradiction_classes
    assert "VALIDATION_STATE_MISMATCH" in contradiction_classes


def test_execution_capabilities_are_forbidden() -> None:
    forbidden = set(build_contract()["forbidden_capabilities"])

    assert {
        "BUY",
        "SELL",
        "ORDER",
        "EXECUTE",
        "POSITION_SIZE",
        "PORTFOLIO_ACTION",
        "BROKER_CONNECTION",
        "EXCHANGE_CONNECTION",
        "API_KEY_ACCESS",
        "OPERATOR_REVIEW_BYPASS",
    }.issubset(forbidden)


def test_invalid_boundary_is_rejected() -> None:
    contract = build_contract()
    contract["boundaries"]["risk_flag_downgrade_allowed"] = True

    assert "invalid_boundary:risk_flag_downgrade_allowed" in validate_contract(
        contract
    )
