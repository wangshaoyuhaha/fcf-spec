from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.read_only_data_gateway_app_1 import (
    ArtifactFormat,
    GatewayReadReceipt,
    GatewayReadRequest,
    GatewayReadStatus,
    READ_ONLY_DATA_GATEWAY_BOUNDARY,
    RegisteredArtifactRegistry,
    RegisteredArtifactSource,
)


def _source(**updates) -> RegisteredArtifactSource:
    values = {
        "source_id": "registered-source-a",
        "evidence_id": "registered-evidence-a",
        "relative_path": "registered/source-a.json",
        "artifact_format": ArtifactFormat.JSON,
        "expected_sha256": "a" * 64,
        "source_class": "A",
        "trust_level": "HIGH",
        "license_type": "PUBLIC",
        "allowed_use": "ALLOWED",
        "freshness_status": "FRESH",
        "published_at_utc": "2026-07-16T00:00:00Z",
    }
    values.update(updates)
    return RegisteredArtifactSource(**values)


def test_d1_boundary_preserves_authority_and_sidecar_limits():
    boundary = READ_ONLY_DATA_GATEWAY_BOUNDARY
    assert boundary.paper_only is True
    assert boundary.local_only is True
    assert boundary.loopback_only is True
    assert boundary.sidecar_only is True
    assert boundary.registered_artifact_only is True
    assert boundary.read_only is True
    assert boundary.operator_review_required is True
    assert boundary.deterministic_authority_preserved is True
    assert boundary.registered_evidence_authority_preserved is True
    assert boundary.ai_advisory_only is True


def test_d1_boundary_rejects_network_or_execution_authority():
    with pytest.raises(ValueError, match="prohibited read-only gateway"):
        replace(READ_ONLY_DATA_GATEWAY_BOUNDARY, network_retrieval_allowed=True)
    with pytest.raises(ValueError, match="prohibited read-only gateway"):
        replace(READ_ONLY_DATA_GATEWAY_BOUNDARY, order_path_allowed=True)


def test_d1_boundary_rejects_disabled_operator_review():
    with pytest.raises(ValueError, match="authority flags"):
        replace(READ_ONLY_DATA_GATEWAY_BOUNDARY, operator_review_required=False)


def test_d1_source_payload_is_immutable_and_normalized():
    source = _source(expected_sha256="A" * 64, trust_level="high")
    payload = source.as_payload()
    assert isinstance(payload, MappingProxyType)
    assert payload["expected_sha256"] == "a" * 64
    assert payload["trust_level"] == "HIGH"
    with pytest.raises(TypeError):
        payload["source_id"] = "tampered"


@pytest.mark.parametrize(
    "relative_path",
    (
        "../source.json",
        "/registered/source.json",
        "C:/registered/source.json",
        "registered\\source.json",
        "registered/./source.json",
    ),
)
def test_d1_source_rejects_unsafe_relative_paths(relative_path):
    with pytest.raises(ValueError, match="relative_path"):
        _source(relative_path=relative_path)


def test_d1_source_rejects_suffix_mismatch_and_bad_digest():
    with pytest.raises(ValueError, match="suffix"):
        _source(relative_path="registered/source.csv")
    with pytest.raises(ValueError, match="SHA-256"):
        _source(expected_sha256="bad")


def test_d1_source_rejects_credentials_and_missing_review():
    with pytest.raises(ValueError, match="credential material"):
        _source(credential_material_expected=True)
    with pytest.raises(ValueError, match="operator_review_required"):
        _source(operator_review_required=False)


def test_d1_request_requires_exact_loopback_and_utc():
    request = GatewayReadRequest(
        request_id="request-001",
        correlation_id="correlation-001",
        source_id="registered-source-a",
        requested_at_utc="2026-07-16T01:00:00+00:00",
    )
    assert request.peer_host == "127.0.0.1"
    with pytest.raises(ValueError, match="exactly 127.0.0.1"):
        replace(request, peer_host="localhost")
    with pytest.raises(ValueError, match="must be UTC"):
        replace(request, requested_at_utc="2026-07-16T09:00:00+08:00")


def test_d1_verified_receipt_requires_digest_and_no_blocking_reasons():
    receipt = GatewayReadReceipt(
        request_id="request-001",
        correlation_id="correlation-001",
        source_id="registered-source-a",
        evidence_id="registered-evidence-a",
        status=GatewayReadStatus.VERIFIED,
        artifact_format=ArtifactFormat.JSON,
        actual_sha256="b" * 64,
        byte_length=42,
    )
    assert receipt.byte_length == 42
    with pytest.raises(ValueError, match="must not contain blocking"):
        replace(receipt, blocking_reasons=("checksum-mismatch",))


def test_d1_blocked_receipt_is_fail_closed():
    receipt = GatewayReadReceipt(
        request_id="request-001",
        correlation_id="correlation-001",
        source_id="registered-source-a",
        evidence_id="registered-evidence-a",
        status=GatewayReadStatus.BLOCKED,
        artifact_format=ArtifactFormat.JSON,
        actual_sha256=None,
        byte_length=None,
        blocking_reasons=("source-not-found", "source-not-found"),
    )
    assert receipt.blocking_reasons == ("source-not-found",)
    with pytest.raises(ValueError, match="must contain a blocking reason"):
        replace(receipt, blocking_reasons=())


def test_d1_registry_is_sorted_immutable_and_reproducible():
    source_b = _source(
        source_id="registered-source-b",
        evidence_id="registered-evidence-b",
        relative_path="registered/source-b.csv",
        artifact_format=ArtifactFormat.CSV,
        expected_sha256="b" * 64,
    )
    registry = RegisteredArtifactRegistry((source_b, _source()))
    assert registry.source_ids == (
        "registered-source-a",
        "registered-source-b",
    )
    assert registry.require("registered-source-a") == _source()
    assert len(registry.registry_sha256) == 64
    assert registry.registry_sha256 == RegisteredArtifactRegistry(
        (_source(), source_b)
    ).registry_sha256
    assert isinstance(registry.as_payload(), MappingProxyType)


@pytest.mark.parametrize(
    "updates,field_name",
    (
        ({"source_id": "registered-source-a"}, "source_id"),
        ({"evidence_id": "registered-evidence-a"}, "evidence_id"),
        ({"relative_path": "registered/source-a.json"}, "relative_path"),
    ),
)
def test_d1_registry_rejects_duplicate_authority_keys(updates, field_name):
    values = {
        "source_id": "registered-source-b",
        "evidence_id": "registered-evidence-b",
        "relative_path": "registered/source-b.json",
        "expected_sha256": "b" * 64,
    }
    values.update(updates)
    duplicate = _source(**values)
    with pytest.raises(ValueError, match=field_name):
        RegisteredArtifactRegistry((_source(), duplicate))


def test_d1_registry_rejects_empty_and_unknown_sources():
    with pytest.raises(ValueError, match="must not be empty"):
        RegisteredArtifactRegistry(())
    registry = RegisteredArtifactRegistry((_source(),))
    with pytest.raises(KeyError, match="unregistered source_id"):
        registry.require("missing-source")


def test_d1_registry_rejects_non_source_entries():
    with pytest.raises(TypeError, match="RegisteredArtifactSource"):
        RegisteredArtifactRegistry(("not-a-source",))
