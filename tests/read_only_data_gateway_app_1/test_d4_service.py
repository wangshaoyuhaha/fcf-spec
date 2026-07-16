import hashlib
from pathlib import Path

import pytest

from apps.read_only_data_gateway_app_1 import (
    ArtifactFormat,
    GatewayReadRequest,
    LocalRegisteredArtifactReader,
    ReadOnlyDataGatewayService,
    RegisteredArtifactRegistry,
    RegisteredArtifactSource,
    SourcePolicyStatus,
    evaluate_source_policy,
)


def _source(content: bytes, **updates):
    values = dict(
        source_id="source-a", evidence_id="evidence-a",
        relative_path="registered/source-a.json", artifact_format=ArtifactFormat.JSON,
        expected_sha256=hashlib.sha256(content).hexdigest(), source_class="A",
        trust_level="HIGH", license_type="PUBLIC", allowed_use="ALLOWED",
        freshness_status="FRESH", published_at_utc="2026-07-16T00:00:00Z",
    )
    values.update(updates)
    return RegisteredArtifactSource(**values)


def _request():
    return GatewayReadRequest("request-1", "correlation-1", "source-a", "2026-07-16T01:00:00Z")


def _service(tmp_path: Path, source, content=b'[{"symbol":"BTC"}]'):
    path = tmp_path / source.relative_path
    path.parent.mkdir(parents=True)
    path.write_bytes(content)
    registry = RegisteredArtifactRegistry((source,))
    return ReadOnlyDataGatewayService(registry, LocalRegisteredArtifactReader(tmp_path))


def test_d4_ready_source_returns_verified_normalized_outcome(tmp_path):
    content = b'[{"symbol":"BTC"}]'
    outcome = _service(tmp_path, _source(content), content).query(_request())
    assert outcome.policy_decision.status is SourcePolicyStatus.READY_FOR_OPERATOR_REVIEW
    assert outcome.receipt is not None
    assert outcome.envelope is not None
    assert outcome.envelope.evidence_id == "evidence-a"


@pytest.mark.parametrize(
    "updates,reason",
    (({"allowed_use":"PROHIBITED"}, "source-use-prohibited"),
     ({"license_type":"RESTRICTED"}, "source-license-restricted")),
)
def test_d4_blocked_source_is_not_read(tmp_path, updates, reason):
    source = _source(b"not-present", **updates)
    service = ReadOnlyDataGatewayService(
        RegisteredArtifactRegistry((source,)), LocalRegisteredArtifactReader(tmp_path)
    )
    outcome = service.query(_request())
    assert outcome.policy_decision.status is SourcePolicyStatus.BLOCKED
    assert reason in outcome.policy_decision.blocking_reasons
    assert outcome.receipt is None and outcome.envelope is None


@pytest.mark.parametrize(
    "updates,reason",
    (({"allowed_use":"RESTRICTED"}, "source-use-restricted"),
     ({"license_type":"UNKNOWN"}, "source-license-unknown"),
     ({"freshness_status":"STALE"}, "source-freshness-stale"),
     ({"trust_level":"LOW"}, "source-trust-low"),
     ({"source_class":"UNKNOWN"}, "source-class-unknown")),
)
def test_d4_degraded_sources_remain_operator_reviewable(tmp_path, updates, reason):
    content = b'[{"symbol":"BTC"}]'
    outcome = _service(tmp_path, _source(content, **updates), content).query(_request())
    assert outcome.policy_decision.status is SourcePolicyStatus.DEGRADED
    assert reason in outcome.policy_decision.degradation_reasons
    assert outcome.envelope is not None
    assert outcome.policy_decision.automatic_activation_allowed is False


def test_d4_unknown_source_fails_closed(tmp_path):
    source = _source(b"[]")
    service = ReadOnlyDataGatewayService(
        RegisteredArtifactRegistry((source,)), LocalRegisteredArtifactReader(tmp_path)
    )
    with pytest.raises(KeyError, match="unregistered source_id"):
        service.query(GatewayReadRequest("r-1", "c-1", "missing", "2026-07-16T01:00:00Z"))


def test_d4_policy_requires_registered_source_type():
    with pytest.raises(TypeError, match="RegisteredArtifactSource"):
        evaluate_source_policy({})
