"""Tests for Read-Only Data Gateway planning D2."""

from copy import deepcopy

import pytest

from fcf.sidecars.read_only_data_gateway_planning import (
    NormalizedDataEnvelopeViolation,
    build_normalized_data_envelope,
    build_read_only_data_gateway_boundary_contract,
    validate_normalized_data_envelope,
)


def _build(**overrides):
    values = {
        "envelope_id": "envelope.public.report.v1",
        "boundary_contract": (
            build_read_only_data_gateway_boundary_contract()
        ),
        "source_id": "source.public.report.v1",
        "source_class": "A",
        "trust_level": "HIGH",
        "published_at": "2026-07-12T00:00:00+00:00",
        "retrieved_at": "2026-07-12T01:00:00+00:00",
        "evidence_id": "evidence.public.report.v1",
        "checksum": "sha256:" + ("a" * 64),
        "freshness_status": "FRESH",
        "license_type": "PUBLIC",
        "allowed_use": "ALLOWED",
        "cloud_processing_allowed": False,
        "retention_period": "policy.retention.v1",
        "redistribution_allowed": False,
        "training_allowed": False,
        "data_format": "json",
        "payload_reference": "payload.normalized.v1",
        "normalization_status": "VALIDATED",
        "credential_scan_status": "CLEAR",
    }
    values.update(overrides)
    return build_normalized_data_envelope(**values)


def test_valid_envelope_passes_validation():
    envelope = _build()
    assert validate_normalized_data_envelope(envelope) == []


def test_valid_envelope_ready_for_d3():
    assert _build()["gateway_status"] == (
        "READY_FOR_D3_SOURCE_POLICY"
    )


def test_unknown_metadata_degrades():
    envelope = _build(
        source_class="UNKNOWN",
        trust_level="UNKNOWN",
        freshness_status="UNKNOWN",
        license_type="UNKNOWN",
    )
    assert envelope["gateway_status"] == "DEGRADED"
    assert envelope["blocking_reasons"] == []
    assert envelope["degradation_reasons"] == [
        "freshness_unknown",
        "license_unknown",
        "source_class_unknown",
        "source_trust_unknown",
    ]


def test_stale_data_degrades():
    envelope = _build(freshness_status="STALE")
    assert envelope["gateway_status"] == "DEGRADED"
    assert envelope["degradation_reasons"] == [
        "freshness_stale"
    ]


def test_restricted_use_degrades():
    envelope = _build(allowed_use="RESTRICTED")
    assert envelope["gateway_status"] == "DEGRADED"


def test_prohibited_use_blocks():
    envelope = _build(allowed_use="PROHIBITED")
    assert envelope["gateway_status"] == "BLOCKED"
    assert "source_use_prohibited" in (
        envelope["blocking_reasons"]
    )


def test_detected_credentials_block():
    envelope = _build(credential_scan_status="DETECTED")
    assert envelope["gateway_status"] == "BLOCKED"
    assert "credential_detected" in (
        envelope["blocking_reasons"]
    )


def test_missing_credential_scan_blocks():
    envelope = _build(credential_scan_status="NOT_RUN")
    assert envelope["gateway_status"] == "BLOCKED"
    assert "credential_scan_not_run" in (
        envelope["blocking_reasons"]
    )


def test_normalization_blocked_blocks():
    envelope = _build(normalization_status="BLOCKED")
    assert envelope["gateway_status"] == "BLOCKED"


def test_invalid_checksum_rejected():
    with pytest.raises(NormalizedDataEnvelopeViolation):
        _build(checksum="bad")


def test_naive_timestamp_rejected():
    with pytest.raises(NormalizedDataEnvelopeViolation):
        _build(published_at="2026-07-12T00:00:00")


def test_retrieval_before_publication_rejected():
    with pytest.raises(NormalizedDataEnvelopeViolation):
        _build(
            published_at="2026-07-12T02:00:00+00:00",
            retrieved_at="2026-07-12T01:00:00+00:00",
        )


def test_invalid_boundary_contract_rejected():
    contract = build_read_only_data_gateway_boundary_contract()
    contract["gateway_status"] = "INVALID"
    with pytest.raises(NormalizedDataEnvelopeViolation):
        _build(boundary_contract=contract)


def test_validation_detects_status_tampering():
    envelope = _build(allowed_use="PROHIBITED")
    envelope["gateway_status"] = "READY_FOR_D3_SOURCE_POLICY"
    assert "gateway_status_mismatch" in (
        validate_normalized_data_envelope(envelope)
    )


def test_builder_returns_fresh_nested_values():
    first = _build()
    second = _build()
    mutated = deepcopy(first)
    mutated["safety_flags"]["database_write_allowed"] = True
    assert second == _build()
    assert mutated != second


def test_non_mapping_envelope_rejected():
    assert validate_normalized_data_envelope([]) == [
        "envelope_must_be_mapping"
    ]
