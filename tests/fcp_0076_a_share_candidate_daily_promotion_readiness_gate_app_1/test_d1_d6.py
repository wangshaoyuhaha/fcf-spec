import json
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

import apps.fcp_0076_a_share_candidate_daily_promotion_readiness_gate_app_1 as fcp_0076
from apps.fcp_0075_a_share_external_candidate_daily_corpus_quality_quarantine_evidence_app_1 import (
    CandidateDailyCorpusQualityEvidence,
)
from apps.fcp_0076_a_share_candidate_daily_promotion_readiness_gate_app_1 import (
    AUTHORITY_DOMAIN_ORDER,
    CandidateDailyAuthorityReference,
    evaluate_candidate_daily_promotion_readiness,
)


def _quality():
    path = Path(
        "FCF_REGISTERED_EVIDENCE_FCP_0075_A_SHARE_EXTERNAL_CANDIDATE_DAILY_"
        "CORPUS_QUALITY_QUARANTINE.json"
    )
    payload = json.loads(path.read_text(encoding="ascii"))
    payload.pop("evidence_hash")
    return CandidateDailyCorpusQualityEvidence(**payload)


def _references(domains=AUTHORITY_DOMAIN_ORDER):
    return tuple(
        CandidateDailyAuthorityReference(
            artifact_id=f"authority-{index}",
            artifact_hash=f"{index:x}" * 64,
            domain=domain,
            observed_at_utc=f"2026-07-22T16:{index:02d}:00Z",
        )
        for index, domain in enumerate(domains, start=1)
    )


def _gate(references=()):
    return evaluate_candidate_daily_promotion_readiness(
        _quality(),
        tuple(references),
        evaluated_at_utc="2026-07-22T17:30:00Z",
    )


def test_closed_authority_domain_order_is_exact():
    assert AUTHORITY_DOMAIN_ORDER == (
        "PROVIDER_IDENTITY",
        "RIGHTS_AND_RETENTION",
        "REVISION_LINEAGE",
        "CORPORATE_ACTION_LINEAGE",
        "ADJUSTMENT_FACTOR_AUTHORITY",
        "TRADING_STATUS_AUTHORITY",
        "EXPECTED_CALENDAR_AUTHORITY",
        "POINT_IN_TIME_AVAILABILITY",
    )


def test_current_candidate_is_blocked_by_quality_and_all_authority_domains():
    gate = _gate()
    assert gate.blocker_codes[:3] == (
        "QUALITY_MALFORMED_ROW",
        "QUALITY_INVALID_OHLC",
        "QUALITY_STALE_TERMINAL",
    )
    assert gate.blocker_codes[3:] == tuple(
        f"MISSING_{domain}" for domain in AUTHORITY_DOMAIN_ORDER
    )
    assert gate.status == "BLOCKED_NOT_READY_FOR_OPERATOR_REVIEW"
    assert gate.ready_for_operator_review is False
    assert gate.candidate_promotion_allowed is False


def test_registered_authority_reference_removes_only_its_missing_blocker():
    gate = _gate(_references(AUTHORITY_DOMAIN_ORDER[:1]))
    assert "MISSING_PROVIDER_IDENTITY" not in gate.blocker_codes
    assert "MISSING_RIGHTS_AND_RETENTION" in gate.blocker_codes
    assert "QUALITY_MALFORMED_ROW" in gate.blocker_codes


def test_complete_authority_set_cannot_waive_observed_quality_failures():
    gate = _gate(_references())
    assert gate.blocker_codes == (
        "QUALITY_MALFORMED_ROW",
        "QUALITY_INVALID_OHLC",
        "QUALITY_STALE_TERMINAL",
    )
    assert gate.provider_selection_allowed is False
    assert gate.factor_calculation_allowed is False
    assert gate.training_label_allowed is False


def test_clean_complete_candidate_is_review_ready_but_never_promoted():
    quality = _quality()
    clean = replace(
        quality,
        malformed_row_count=0,
        invalid_ohlc_row_count=0,
        stale_terminal_file_count=0,
    )
    gate = evaluate_candidate_daily_promotion_readiness(
        clean,
        _references(),
        evaluated_at_utc="2026-07-22T17:30:00Z",
    )
    assert gate.blocker_codes == ()
    assert gate.status == "READY_FOR_OPERATOR_REVIEW_NOT_PROMOTED"
    assert gate.ready_for_operator_review is True
    assert gate.operator_review_mandatory is True
    assert gate.candidate_promotion_allowed is False
    assert gate.factor_calculation_allowed is False


def test_gate_and_references_are_deterministic():
    assert _references() == _references()
    assert _gate().gate_hash == _gate().gate_hash


def test_registered_gate_evidence_replays_exactly():
    path = Path(
        "FCF_REGISTERED_EVIDENCE_FCP_0076_A_SHARE_CANDIDATE_DAILY_PROMOTION_"
        "READINESS_GATE.json"
    )
    payload = json.loads(path.read_text(encoding="ascii"))
    gate = _gate()
    from dataclasses import asdict

    assert json.loads(json.dumps(asdict(gate), sort_keys=True)) == payload


def test_gate_hash_changes_with_registered_authority_evidence():
    assert _gate().gate_hash != _gate(_references(AUTHORITY_DOMAIN_ORDER[:1])).gate_hash


@pytest.mark.parametrize(
    "field,value",
    (("artifact_id", "unsafe value"), ("artifact_hash", "0" * 63)),
)
def test_reference_rejects_invalid_identity(field, value):
    values = {
        "artifact_id": "authority-1",
        "artifact_hash": "1" * 64,
        "domain": AUTHORITY_DOMAIN_ORDER[0],
        "observed_at_utc": "2026-07-22T16:01:00Z",
    }
    values[field] = value
    with pytest.raises(ValueError):
        CandidateDailyAuthorityReference(**values)


def test_reference_rejects_unknown_domain_and_unregistered_artifact():
    with pytest.raises(ValueError, match="domain is not registered"):
        replace(_references()[0], domain="PROVIDER")
    with pytest.raises(ValueError, match="registered artifact"):
        replace(_references()[0], registered_artifact=False)


def test_gate_rejects_untyped_quality_evidence():
    with pytest.raises(ValueError, match="exact typed FCP-0075"):
        evaluate_candidate_daily_promotion_readiness(
            object(), (), evaluated_at_utc="2026-07-22T17:30:00Z"
        )


def test_gate_rejects_untyped_authority_reference():
    with pytest.raises(ValueError, match="exact typed references"):
        _gate((object(),))


def test_gate_rejects_reordered_or_duplicate_authority_domains():
    references = _references(AUTHORITY_DOMAIN_ORDER[:2])
    with pytest.raises(ValueError, match="closed domain order"):
        _gate(tuple(reversed(references)))
    with pytest.raises(ValueError, match="closed domain order"):
        _gate((references[0], references[0]))


@pytest.mark.parametrize("field", ("artifact_id", "artifact_hash"))
def test_gate_rejects_duplicate_authority_identity(field):
    references = list(_references(AUTHORITY_DOMAIN_ORDER[:2]))
    references[1] = replace(references[1], **{field: getattr(references[0], field)})
    with pytest.raises(ValueError, match="must be unique"):
        _gate(tuple(references))


def test_gate_rejects_time_regression():
    with pytest.raises(ValueError, match="cannot postdate"):
        evaluate_candidate_daily_promotion_readiness(
            _quality(), (), evaluated_at_utc="2026-07-22T16:00:00Z"
        )
    future = replace(_references()[0], observed_at_utc="2026-07-22T18:00:00Z")
    with pytest.raises(ValueError, match="cannot postdate"):
        _gate((future,))


@pytest.mark.parametrize(
    "field,value",
    (
        ("status", "READY_FOR_OPERATOR_REVIEW"),
        ("ready_for_operator_review", True),
        ("candidate_promotion_allowed", True),
        ("factor_calculation_allowed", True),
        ("training_label_allowed", True),
        ("provider_selection_allowed", True),
        ("operator_review_mandatory", False),
    ),
)
def test_gate_rejects_authority_escalation(field, value):
    with pytest.raises(ValueError):
        replace(_gate(), **{field: value})


def test_gate_is_frozen():
    with pytest.raises(FrozenInstanceError):
        _gate().status = "changed"


def test_package_exports_are_closed():
    assert fcp_0076.__all__ == [
        "AUTHORITY_DOMAIN_ORDER",
        "CandidateDailyAuthorityReference",
        "CandidateDailyPromotionReadinessGate",
        "evaluate_candidate_daily_promotion_readiness",
    ]
