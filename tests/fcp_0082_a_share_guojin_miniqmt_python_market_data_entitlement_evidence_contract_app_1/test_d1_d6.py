from __future__ import annotations

import hashlib
import json
from dataclasses import FrozenInstanceError, replace

import pytest

from apps.fcp_0082_a_share_guojin_miniqmt_python_market_data_entitlement_evidence_contract_app_1 import (
    ALLOWED_CAPABILITIES,
    ALLOWED_DECISIONS,
    ALLOWED_MARKETS,
    MiniQMTEntitlementEvidence,
    RegisteredEntitlementEvidenceArtifact,
    build_reference_packet,
    evaluate_evidence,
    load_sanitized_evidence,
)


def evidence_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "capabilities": ["MINUTE_BAR", "DAILY_BAR"],
        "captured_at_utc": "2026-07-23T08:00:00Z",
        "clock_semantics": "ASIA_SHANGHAI_EXCHANGE_TIME",
        "entitlement_declared_state": "GRANTED",
        "evidence_revision": "operator-evidence-v1",
        "expires_at_utc": "2026-08-23T08:00:00Z",
        "markets": ["SZSE", "SSE"],
        "module_file_sha256": "2" * 64,
        "probe_status": "SUCCEEDED",
        "python_module_name": "xtquant",
        "python_module_version": "1.0.0",
        "retention_state": "DOCUMENTED",
        "rights_state": "DOCUMENTED",
        "supporting_document_sha256": "3" * 64,
        "terminal_product": "GUOJIN_MINIQMT",
        "terminal_version": "2.1.19.0",
    }
    payload.update(overrides)
    return payload


def artifact_for(raw: bytes) -> RegisteredEntitlementEvidenceArtifact:
    return RegisteredEntitlementEvidenceArtifact(
        artifact_id="guojin-miniqmt-evidence-v1",
        artifact_path="local/registered/miniqmt-entitlement-evidence.json",
        artifact_sha256=hashlib.sha256(raw).hexdigest(),
        byte_length=len(raw),
    )


def encoded_payload(**overrides: object) -> bytes:
    return json.dumps(
        evidence_payload(**overrides),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def loaded_evidence(**overrides: object) -> tuple[RegisteredEntitlementEvidenceArtifact, MiniQMTEntitlementEvidence]:
    raw = encoded_payload(**overrides)
    artifact = artifact_for(raw)
    return artifact, load_sanitized_evidence(artifact, raw)


def test_closed_vocabulary_is_exact():
    assert ALLOWED_MARKETS == ("SSE", "SZSE")
    assert ALLOWED_CAPABILITIES == ("DAILY_BAR", "MINUTE_BAR", "ORDER_BOOK", "TICK")
    assert ALLOWED_DECISIONS == ("INSUFFICIENT_EVIDENCE", "OPERATOR_REVIEW_ELIGIBLE")


def test_registered_artifact_is_immutable_and_non_authorizing():
    artifact = artifact_for(encoded_payload())
    assert artifact.network_used_by_sidecar is False
    assert artifact.credentials_committed is False
    with pytest.raises(FrozenInstanceError):
        artifact.byte_length = 1  # type: ignore[misc]


@pytest.mark.parametrize(
    "field,value",
    (
        ("credentials_committed", True),
        ("account_identifiers_committed", True),
        ("raw_market_values_committed", True),
        ("executable_request_committed", True),
        ("network_used_by_sidecar", True),
        ("operator_review_required", False),
    ),
)
def test_registered_artifact_boundary_cannot_be_weakened(field: str, value: object):
    artifact = artifact_for(encoded_payload())
    with pytest.raises(ValueError, match="cannot be weakened"):
        replace(artifact, **{field: value})


def test_loader_verifies_and_normalizes_exact_sanitized_evidence():
    artifact, evidence = loaded_evidence()
    assert artifact.artifact_id == "guojin-miniqmt-evidence-v1"
    assert evidence.markets == ("SSE", "SZSE")
    assert evidence.capabilities == ("DAILY_BAR", "MINUTE_BAR")
    assert evidence.probe_invoked_by_sidecar is False
    assert evidence.provider_selected is False


def test_loader_rejects_length_mismatch():
    raw = encoded_payload()
    with pytest.raises(ValueError, match="length mismatch"):
        load_sanitized_evidence(replace(artifact_for(raw), byte_length=len(raw) + 1), raw)


def test_loader_rejects_digest_mismatch():
    raw = encoded_payload()
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_sanitized_evidence(replace(artifact_for(raw), artifact_sha256="0" * 64), raw)


def test_loader_rejects_non_ascii():
    raw = '{"note":"unsafe-chinese-\u8bc1\u636e"}'.encode("utf-8")
    with pytest.raises(ValueError, match="ASCII"):
        load_sanitized_evidence(artifact_for(raw), raw)


def test_loader_rejects_duplicate_json_key():
    raw = b'{"terminal_product":"GUOJIN_MINIQMT","terminal_product":"GUOJIN_MINIQMT"}'
    with pytest.raises(ValueError, match="duplicate JSON key"):
        load_sanitized_evidence(artifact_for(raw), raw)


@pytest.mark.parametrize("forbidden_key", ("account_id", "password", "token", "authorization_code"))
def test_loader_rejects_secret_or_account_keys(forbidden_key: str):
    payload = evidence_payload()
    payload[forbidden_key] = "redacted"
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("ascii")
    with pytest.raises(ValueError, match="forbidden"):
        load_sanitized_evidence(artifact_for(raw), raw)


def test_loader_rejects_unregistered_field():
    raw = encoded_payload(note="unexpected")
    with pytest.raises(ValueError, match="closed schema"):
        load_sanitized_evidence(artifact_for(raw), raw)


@pytest.mark.parametrize(
    "overrides,match",
    (
        ({"terminal_product": "OTHER"}, "terminal_product"),
        ({"python_module_name": "requests"}, "python_module_name"),
        ({"markets": ["BSE"]}, "markets"),
        ({"capabilities": ["ORDER"]}, "capabilities"),
        ({"captured_at_utc": "2026-07-23T08:00:00+08:00"}, "captured_at_utc"),
    ),
)
def test_evidence_rejects_unregistered_semantics(overrides: dict[str, object], match: str):
    raw = encoded_payload(**overrides)
    with pytest.raises(ValueError, match=match):
        load_sanitized_evidence(artifact_for(raw), raw)


def test_complete_evidence_is_review_eligible_but_never_authorizing():
    artifact, evidence = loaded_evidence()
    packet = evaluate_evidence(artifact, evidence, as_of_utc="2026-07-23T09:00:00Z")
    assert packet.decision_state == "OPERATOR_REVIEW_ELIGIBLE"
    assert packet.blockers == ()
    assert packet.entitlement_authorized is False
    assert packet.registered_evidence_authority is False
    assert packet.realtime_activation_authorized is False
    assert packet.provider_selected is False
    assert packet.data_promotion_authorized is False
    assert packet.closes_gap is False
    assert packet.operator_review_required is True


@pytest.mark.parametrize(
    "overrides,blocker",
    (
        ({"entitlement_declared_state": "UNKNOWN"}, "ENTITLEMENT_NOT_DECLARED_GRANTED"),
        ({"probe_status": "NOT_RUN"}, "READ_ONLY_PROBE_NOT_SUCCEEDED"),
        ({"rights_state": "UNRESOLVED"}, "RIGHTS_NOT_DOCUMENTED"),
        ({"retention_state": "UNRESOLVED"}, "RETENTION_NOT_DOCUMENTED"),
        ({"markets": ["SSE"]}, "MISSING_MARKET_SZSE"),
        ({"capabilities": ["DAILY_BAR"]}, "MISSING_CAPABILITY_MINUTE_BAR"),
        ({"expires_at_utc": None}, "EXPIRY_NOT_DECLARED"),
        ({"expires_at_utc": "2026-07-23T08:30:00Z"}, "EVIDENCE_EXPIRED"),
    ),
)
def test_incomplete_evidence_fails_closed(overrides: dict[str, object], blocker: str):
    artifact, evidence = loaded_evidence(**overrides)
    packet = evaluate_evidence(artifact, evidence, as_of_utc="2026-07-23T09:00:00Z")
    assert packet.decision_state == "INSUFFICIENT_EVIDENCE"
    assert blocker in packet.blockers
    assert packet.entitlement_authorized is False


def test_packet_payload_is_immutable():
    packet = build_reference_packet()
    with pytest.raises(TypeError):
        packet.as_payload()["decision_state"] = "INSUFFICIENT_EVIDENCE"  # type: ignore[index]


def test_reference_packet_is_deterministic_and_non_authorizing():
    first = build_reference_packet()
    second = build_reference_packet()
    assert first.packet_hash == second.packet_hash
    assert first.decision_state == "OPERATOR_REVIEW_ELIGIBLE"
    assert first.entitlement_authorized is False
    assert first.realtime_activation_authorized is False


def test_invalid_as_of_clock_is_rejected():
    artifact, evidence = loaded_evidence()
    with pytest.raises(ValueError, match="as_of_utc"):
        evaluate_evidence(artifact, evidence, as_of_utc="2026-07-23T17:00:00+08:00")
