from dataclasses import replace

import pytest

from apps.read_only_data_gateway_app_1 import (
    ArtifactFormat, RegisteredArtifactRegistry, RegisteredArtifactSource,
    build_gateway_operator_review_packet, build_gateway_presentation_model,
    build_gateway_runtime_acceptance,
)


def _source(source_id, **updates):
    values=dict(source_id=source_id,evidence_id=f"evidence-{source_id}",
        relative_path=f"registered/{source_id}.json",artifact_format=ArtifactFormat.JSON,
        expected_sha256="a"*64,source_class="A",trust_level="HIGH",
        license_type="PUBLIC",allowed_use="ALLOWED",freshness_status="FRESH",
        published_at_utc="2026-07-16T00:00:00Z")
    values.update(updates)
    return RegisteredArtifactSource(**values)


def test_d6_acceptance_reconciles_all_policy_states():
    registry=RegisteredArtifactRegistry((
        _source("ready"),_source("degraded",freshness_status="STALE"),
        _source("blocked",allowed_use="PROHIBITED")))
    model=build_gateway_presentation_model(registry)
    packet=build_gateway_operator_review_packet("packet-final",model)
    acceptance=build_gateway_runtime_acceptance(model,packet)
    assert acceptance.status == "READY_FOR_OPERATOR_ACCEPTANCE"
    assert acceptance.registered_source_count == 3
    assert (acceptance.ready_count,acceptance.degraded_count,acceptance.blocked_count)==(1,1,1)


def test_d6_acceptance_preserves_permanent_authority_boundary():
    model=build_gateway_presentation_model(RegisteredArtifactRegistry((_source("ready"),)))
    acceptance=build_gateway_runtime_acceptance(
        model,build_gateway_operator_review_packet("packet-final",model))
    assert acceptance.paper_only and acceptance.local_only and acceptance.loopback_only
    assert acceptance.registered_artifact_only and acceptance.operator_review_required
    assert acceptance.deterministic_authority_preserved
    assert acceptance.registered_evidence_authority_preserved
    assert acceptance.automatic_activation_allowed is False
    assert acceptance.trading_or_execution_path_allowed is False
    with pytest.raises(ValueError,match="boundary"):
        replace(acceptance,trading_or_execution_path_allowed=True)


def test_d6_acceptance_rejects_packet_from_other_registry():
    first=build_gateway_presentation_model(RegisteredArtifactRegistry((_source("first"),)))
    second=build_gateway_presentation_model(RegisteredArtifactRegistry((_source("second"),)))
    with pytest.raises(ValueError,match="registry mismatch"):
        build_gateway_runtime_acceptance(
            first,build_gateway_operator_review_packet("packet-final",second))
