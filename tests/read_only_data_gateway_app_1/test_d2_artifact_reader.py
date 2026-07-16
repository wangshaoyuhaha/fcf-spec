import hashlib
from dataclasses import replace
from pathlib import Path

import pytest

from apps.read_only_data_gateway_app_1 import (
    ArtifactFormat,
    GatewayReadRequest,
    LocalRegisteredArtifactReader,
    RegisteredArtifactReadError,
    RegisteredArtifactRegistry,
    RegisteredArtifactSource,
    VerifiedArtifactRead,
    resolve_registered_artifact_path,
)


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _source(content: bytes, **updates) -> RegisteredArtifactSource:
    values = {
        "source_id": "registered-source-a",
        "evidence_id": "registered-evidence-a",
        "relative_path": "registered/source-a.json",
        "artifact_format": ArtifactFormat.JSON,
        "expected_sha256": _digest(content),
        "source_class": "A",
        "trust_level": "HIGH",
        "license_type": "PUBLIC",
        "allowed_use": "ALLOWED",
        "freshness_status": "FRESH",
        "published_at_utc": "2026-07-16T00:00:00Z",
    }
    values.update(updates)
    return RegisteredArtifactSource(**values)


def _request(source_id: str = "registered-source-a") -> GatewayReadRequest:
    return GatewayReadRequest(
        request_id="request-001",
        correlation_id="correlation-001",
        source_id=source_id,
        requested_at_utc="2026-07-16T01:00:00Z",
    )


def _fixture(tmp_path: Path, content: bytes = b'{"symbol":"BTCUSDT"}'):
    path = tmp_path / "registered" / "source-a.json"
    path.parent.mkdir()
    path.write_bytes(content)
    source = _source(content)
    return path, source, RegisteredArtifactRegistry((source,))


def test_d2_reads_only_registered_checksum_verified_bytes(tmp_path):
    _, source, registry = _fixture(tmp_path)
    result = LocalRegisteredArtifactReader(tmp_path).read(_request(), registry)
    assert isinstance(result, VerifiedArtifactRead)
    assert result.content == b'{"symbol":"BTCUSDT"}'
    assert result.source == source
    assert result.receipt.actual_sha256 == source.expected_sha256
    assert result.receipt.byte_length == len(result.content)
    assert str(tmp_path) not in repr(result.receipt)


def test_d2_supports_registered_csv_bytes(tmp_path):
    content = b"symbol,close\nBTCUSDT,65000\n"
    path = tmp_path / "registered" / "source-a.csv"
    path.parent.mkdir()
    path.write_bytes(content)
    source = _source(
        content,
        relative_path="registered/source-a.csv",
        artifact_format=ArtifactFormat.CSV,
    )
    result = LocalRegisteredArtifactReader(tmp_path).read(
        _request(), RegisteredArtifactRegistry((source,))
    )
    assert result.content == content
    assert result.receipt.artifact_format is ArtifactFormat.CSV


def test_d2_rejects_unknown_source_before_file_resolution(tmp_path):
    _, _, registry = _fixture(tmp_path)
    with pytest.raises(RegisteredArtifactReadError) as error:
        LocalRegisteredArtifactReader(tmp_path).read(
            _request("missing-source"), registry
        )
    assert error.value.reason_code == "source-not-registered"


def test_d2_rejects_checksum_mismatch(tmp_path):
    _, source, _ = _fixture(tmp_path)
    tampered = replace(source, expected_sha256="f" * 64)
    with pytest.raises(RegisteredArtifactReadError) as error:
        LocalRegisteredArtifactReader(tmp_path).read(
            _request(), RegisteredArtifactRegistry((tampered,))
        )
    assert error.value.reason_code == "registered-artifact-checksum-mismatch"


def test_d2_rejects_missing_and_directory_artifacts(tmp_path):
    source = _source(b"missing")
    registry = RegisteredArtifactRegistry((source,))
    with pytest.raises(RegisteredArtifactReadError) as missing:
        LocalRegisteredArtifactReader(tmp_path).read(_request(), registry)
    assert missing.value.reason_code == "registered-artifact-unavailable"

    directory = tmp_path / "registered" / "source-a.json"
    directory.mkdir(parents=True)
    with pytest.raises(RegisteredArtifactReadError) as not_file:
        LocalRegisteredArtifactReader(tmp_path).read(_request(), registry)
    assert not_file.value.reason_code == "registered-artifact-not-file"


def test_d2_rejects_oversized_artifact_without_returning_content(tmp_path):
    content = b"12345"
    _, _, registry = _fixture(tmp_path, content)
    with pytest.raises(RegisteredArtifactReadError) as error:
        LocalRegisteredArtifactReader(tmp_path, max_artifact_bytes=4).read(
            _request(), registry
        )
    assert error.value.reason_code == "registered-artifact-size-limit-exceeded"


@pytest.mark.parametrize("limit", (0, -1, True, 1.5))
def test_d2_rejects_invalid_size_limit(tmp_path, limit):
    with pytest.raises(ValueError, match="positive integer"):
        LocalRegisteredArtifactReader(tmp_path, max_artifact_bytes=limit)


def test_d2_resolver_returns_file_inside_allowed_root(tmp_path):
    path, source, _ = _fixture(tmp_path)
    assert resolve_registered_artifact_path(tmp_path, source) == path.resolve()


def test_d2_rejects_symbolic_artifact_path(tmp_path):
    target = tmp_path / "actual.json"
    target.write_bytes(b"{}")
    link = tmp_path / "registered" / "source-a.json"
    link.parent.mkdir()
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip("symbolic links are unavailable")
    source = _source(b"{}")
    with pytest.raises(RegisteredArtifactReadError) as error:
        resolve_registered_artifact_path(tmp_path, source)
    assert error.value.reason_code == "symbolic-artifact-path-prohibited"


def test_d2_rejects_symbolic_allowed_root(tmp_path):
    actual = tmp_path / "actual-root"
    actual.mkdir()
    link = tmp_path / "linked-root"
    try:
        link.symlink_to(actual, target_is_directory=True)
    except OSError:
        pytest.skip("symbolic links are unavailable")
    with pytest.raises(RegisteredArtifactReadError) as error:
        LocalRegisteredArtifactReader(link)
    assert error.value.reason_code == "symbolic-allowed-root-prohibited"


def test_d2_verified_read_rejects_mutable_or_mismatched_content(tmp_path):
    _, _, registry = _fixture(tmp_path)
    result = LocalRegisteredArtifactReader(tmp_path).read(_request(), registry)
    with pytest.raises(TypeError, match="immutable bytes"):
        replace(result, content=bytearray(result.content))
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        replace(result, content=b"tampered")
