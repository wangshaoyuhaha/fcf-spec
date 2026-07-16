import hashlib
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.read_only_data_gateway_app_1 import (
    ArtifactFormat,
    ArtifactNormalizationError,
    GatewayReadRequest,
    LocalRegisteredArtifactReader,
    RegisteredArtifactRegistry,
    RegisteredArtifactSource,
    normalize_verified_artifact,
)


def _read(tmp_path: Path, content: bytes, artifact_format=ArtifactFormat.JSON):
    suffix = artifact_format.value.lower()
    path = tmp_path / "registered" / f"source-a.{suffix}"
    path.parent.mkdir(exist_ok=True)
    path.write_bytes(content)
    source = RegisteredArtifactSource(
        source_id="registered-source-a",
        evidence_id="registered-evidence-a",
        relative_path=f"registered/source-a.{suffix}",
        artifact_format=artifact_format,
        expected_sha256=hashlib.sha256(content).hexdigest(),
        source_class="A",
        trust_level="HIGH",
        license_type="PUBLIC",
        allowed_use="ALLOWED",
        freshness_status="FRESH",
        published_at_utc="2026-07-16T00:00:00Z",
    )
    request = GatewayReadRequest(
        request_id="request-001",
        correlation_id="correlation-001",
        source_id=source.source_id,
        requested_at_utc="2026-07-16T01:00:00Z",
    )
    return LocalRegisteredArtifactReader(tmp_path).read(
        request, RegisteredArtifactRegistry((source,))
    )


def test_d3_normalizes_json_records_with_evidence_linkage(tmp_path):
    artifact = _read(tmp_path, b'[{"symbol":"BTCUSDT","close":65000}]')
    envelope = normalize_verified_artifact(artifact)
    assert envelope.source_id == "registered-source-a"
    assert envelope.evidence_id == "registered-evidence-a"
    assert envelope.artifact_sha256 == artifact.receipt.actual_sha256
    assert envelope.record_count == 1
    assert len(envelope.normalized_records_sha256) == 64
    assert envelope.credential_scan_status == "CLEAR"


def test_d3_normalizes_json_wrappers_and_single_object(tmp_path):
    wrapped = normalize_verified_artifact(
        _read(tmp_path, b'{"rows":[{"symbol":"BTCUSDT"}]}')
    )
    assert wrapped.record_count == 1
    single_root = tmp_path / "single"
    single_root.mkdir()
    single = normalize_verified_artifact(
        _read(single_root, b'{"symbol":"ETHUSDT"}')
    )
    assert single.record_count == 1


def test_d3_normalizes_csv_deterministically(tmp_path):
    content = b"symbol,close\nBTCUSDT,65000\nETHUSDT,3500\n"
    envelope = normalize_verified_artifact(
        _read(tmp_path, content, ArtifactFormat.CSV)
    )
    assert envelope.record_count == 2
    assert envelope.records[0]["close"] == "65000"
    assert envelope.normalized_records_sha256 == normalize_verified_artifact(
        _read(tmp_path, content, ArtifactFormat.CSV)
    ).normalized_records_sha256


def test_d3_records_are_deeply_immutable(tmp_path):
    envelope = normalize_verified_artifact(
        _read(tmp_path, b'[{"nested":{"values":[1,2]}}]')
    )
    assert isinstance(envelope.records[0], MappingProxyType)
    assert isinstance(envelope.records[0]["nested"], MappingProxyType)
    assert envelope.records[0]["nested"]["values"] == (1, 2)
    with pytest.raises(TypeError):
        envelope.records[0]["nested"] = {}


@pytest.mark.parametrize(
    "content,reason",
    (
        (b"\xff", "artifact-encoding-not-utf8"),
        (b"{bad", "json-parse-failed"),
        (b"[]", "artifact-records-empty"),
        (b"[1]", "normalized-record-must-be-object"),
        (b'{"x":1,"x":2}', "json-duplicate-object-key"),
        (b'[{"x":NaN}]', "json-non-finite-number"),
        (b'[{"api_key":"secret-value"}]', "credential-material-detected"),
        (
            b'[{"note":"-----BEGIN PRIVATE KEY-----"}]',
            "credential-material-detected",
        ),
    ),
)
def test_d3_json_fail_closed(tmp_path, content, reason):
    with pytest.raises(ArtifactNormalizationError) as error:
        normalize_verified_artifact(_read(tmp_path, content))
    assert error.value.reason_code == reason


def test_d3_rejects_csv_duplicate_headers_and_width_mismatch(tmp_path):
    duplicate = _read(tmp_path, b"symbol,symbol\nBTC,ETH\n", ArtifactFormat.CSV)
    with pytest.raises(ArtifactNormalizationError) as error:
        normalize_verified_artifact(duplicate)
    assert error.value.reason_code == "csv-duplicate-header"
    other = tmp_path / "other"
    other.mkdir()
    wide = _read(other, b"symbol,close\nBTC,1,extra\n", ArtifactFormat.CSV)
    with pytest.raises(ArtifactNormalizationError) as error:
        normalize_verified_artifact(wide)
    assert error.value.reason_code == "csv-row-width-mismatch"


def test_d3_rejects_record_limit_and_invalid_limit(tmp_path):
    artifact = _read(tmp_path, b'[{"x":1},{"x":2}]')
    with pytest.raises(ArtifactNormalizationError) as error:
        normalize_verified_artifact(artifact, max_records=1)
    assert error.value.reason_code == "artifact-record-limit-exceeded"
    with pytest.raises(ValueError, match="positive integer"):
        normalize_verified_artifact(artifact, max_records=0)


def test_d3_payload_is_read_only_product_data(tmp_path):
    envelope = normalize_verified_artifact(_read(tmp_path, b'[{"symbol":"BTC"}]'))
    payload = envelope.as_payload()
    assert isinstance(payload, MappingProxyType)
    assert payload["operator_review_required"] is True
    assert payload["records"] == ({"symbol": "BTC"},)
    with pytest.raises(TypeError):
        payload["record_count"] = 0
