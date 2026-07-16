import hashlib
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.read_only_data_gateway_app_1 import (
    ArtifactFormat, GatewayReadRequest, LocalRegisteredArtifactReader,
    ReadOnlyDataGatewayService, RegisteredArtifactRegistry,
    RegisteredArtifactSource, build_gateway_operator_review_packet,
    build_gateway_presentation_model,
)


def _source(content: bytes, source_id="source-a", **updates):
    values=dict(source_id=source_id,evidence_id=f"evidence-{source_id}",
        relative_path=f"registered/{source_id}.json",artifact_format=ArtifactFormat.JSON,
        expected_sha256=hashlib.sha256(content).hexdigest(),source_class="A",
        trust_level="HIGH",license_type="PUBLIC",allowed_use="ALLOWED",
        freshness_status="FRESH",published_at_utc="2026-07-16T00:00:00Z")
    values.update(updates)
    return RegisteredArtifactSource(**values)


def test_d5_catalog_model_is_read_only_without_artifact_access():
    registry=RegisteredArtifactRegistry((_source(b"x"),))
    model=build_gateway_presentation_model(registry)
    assert model.sources[0].record_count is None
    assert model.read_only is True
    assert isinstance(model.status_counts, MappingProxyType)
    assert isinstance(model.sources[0].as_payload(), MappingProxyType)


def test_d5_model_presents_verified_evidence_summary(tmp_path: Path):
    content=b'[{"symbol":"BTC"}]'
    source=_source(content)
    path=tmp_path/source.relative_path
    path.parent.mkdir(parents=True)
    path.write_bytes(content)
    registry=RegisteredArtifactRegistry((source,))
    outcome=ReadOnlyDataGatewayService(
        registry,LocalRegisteredArtifactReader(tmp_path)
    ).query(GatewayReadRequest("r-1","c-1","source-a","2026-07-16T01:00:00Z"))
    model=build_gateway_presentation_model(registry,(outcome,))
    item=model.sources[0]
    assert item.record_count == 1
    assert item.evidence_id == source.evidence_id
    assert len(item.normalized_records_sha256) == 64


def test_d5_model_counts_ready_degraded_and_blocked():
    content=b"x"
    registry=RegisteredArtifactRegistry((
        _source(content,"ready"),
        _source(content,"degraded",freshness_status="STALE"),
        _source(content,"blocked",allowed_use="PROHIBITED"),
    ))
    model=build_gateway_presentation_model(registry)
    assert sorted(model.status_counts.values()) == [1,1,1]


def test_d5_review_packet_keeps_operator_authority():
    model=build_gateway_presentation_model(RegisteredArtifactRegistry((_source(b"x"),)))
    packet=build_gateway_operator_review_packet("packet-1",model)
    assert packet.operator_decision_status == "PENDING"
    assert packet.automatic_activation_allowed is False
    assert packet.write_operation_allowed is False
    assert "REQUEST_SOURCE_REPAIR" in packet.allowed_operator_actions
    assert all("ACTIVATE" not in action for action in packet.allowed_operator_actions)


def test_d5_rejects_duplicate_or_unregistered_outcomes(tmp_path):
    content=b'[{"x":1}]'
    source=_source(content)
    path=tmp_path/source.relative_path
    path.parent.mkdir(parents=True)
    path.write_bytes(content)
    registry=RegisteredArtifactRegistry((source,))
    outcome=ReadOnlyDataGatewayService(registry,LocalRegisteredArtifactReader(tmp_path)).query(
        GatewayReadRequest("r-1","c-1","source-a","2026-07-16T01:00:00Z"))
    with pytest.raises(ValueError,match="duplicate"):
        build_gateway_presentation_model(registry,(outcome,outcome))
