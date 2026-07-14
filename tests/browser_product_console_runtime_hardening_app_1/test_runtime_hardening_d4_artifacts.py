from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    RegisteredConsoleArtifact,
    RuntimeArtifactSnapshot,
    RuntimeHardeningLimits,
    load_console_artifact_index,
    normalize_registered_relative_path,
    read_runtime_artifact_snapshot,
    resolve_runtime_artifact_path,
)


def _write_json(
    path: Path,
    value: object,
) -> bytes:
    content = json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=True,
    ).encode("utf-8")

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    path.write_bytes(content)

    return content


def _write_index(
    root: Path,
    relative_path: str,
    digest: str,
) -> Path:
    index_path = root / "artifact_index.json"

    _write_json(
        index_path,
        {
            "schema_version": (
                "fcf.browser_console."
                "artifact_index.v1"
            ),
            "correlation_id": "corr-d4",
            "entries": [
                {
                    "artifact_id": "artifact-d4",
                    "artifact_type": "data_snapshot",
                    "correlation_id": "corr-d4",
                    "relative_path": relative_path,
                    "content_sha256": digest,
                }
            ],
        },
    )

    return index_path


@pytest.mark.parametrize(
    ("raw", "expected"),
    (
        ("artifact.json", "artifact.json"),
        (
            "registered/artifact.json",
            "registered/artifact.json",
        ),
        (
            r"registered\artifact.json",
            "registered/artifact.json",
        ),
    ),
)
def test_d4_relative_path_normalization(
    raw,
    expected,
):
    assert (
        normalize_registered_relative_path(raw)
        == expected
    )


@pytest.mark.parametrize(
    "raw",
    (
        "",
        " artifact.json",
        "artifact.json ",
        "../artifact.json",
        "registered/../artifact.json",
        "./artifact.json",
        "/artifact.json",
        r"C:\artifact.json",
        r"\\server\share\artifact.json",
        "artifact.json:stream",
        "registered//",
        "registered/\x00artifact.json",
    ),
)
def test_d4_relative_path_rejects_escape_syntax(
    raw,
):
    with pytest.raises(ValueError):
        normalize_registered_relative_path(raw)


def test_d4_registration_canonicalizes_path():
    registration = RegisteredConsoleArtifact(
        artifact_id="artifact-d4",
        artifact_type="data_snapshot",
        correlation_id="corr-d4",
        relative_path=r"registered\artifact.json",
        content_sha256="0" * 64,
    )

    assert registration.relative_path == (
        "registered/artifact.json"
    )


def test_d4_snapshot_contract_is_strict():
    content = b"{}"
    digest = hashlib.sha256(content).hexdigest()

    snapshot = RuntimeArtifactSnapshot(
        resolved_path="artifact.json",
        size_bytes=len(content),
        content_sha256=digest,
        content=content,
    )

    assert snapshot.size_bytes == 2
    assert snapshot.content_sha256 == digest

    with pytest.raises(ValueError):
        RuntimeArtifactSnapshot(
            resolved_path="artifact.json",
            size_bytes=1,
            content_sha256=digest,
            content=content,
        )


def test_d4_registered_artifact_loads_with_integrity(
    tmp_path,
):
    artifact_path = (
        tmp_path
        / "registered"
        / "artifact.json"
    )
    content = _write_json(
        artifact_path,
        {
            "value": "registered",
            "paper_only": True,
        },
    )
    digest = hashlib.sha256(content).hexdigest()
    index_path = _write_index(
        tmp_path,
        "registered/artifact.json",
        digest,
    )

    loaded = load_console_artifact_index(
        index_path,
        tmp_path,
    )

    assert loaded.index.correlation_id == "corr-d4"
    assert len(loaded.artifacts) == 1
    assert (
        loaded.artifacts[0].registration.content_sha256
        == digest
    )
    assert loaded.artifacts[0].payload == {
        "paper_only": True,
        "value": "registered",
    }


def test_d4_tampered_artifact_fails_closed(
    tmp_path,
):
    artifact_path = tmp_path / "artifact.json"
    original = _write_json(
        artifact_path,
        {"value": "original"},
    )
    digest = hashlib.sha256(original).hexdigest()
    index_path = _write_index(
        tmp_path,
        "artifact.json",
        digest,
    )

    _write_json(
        artifact_path,
        {"value": "tampered"},
    )

    with pytest.raises(
        ValueError,
        match="SHA-256 mismatch",
    ):
        load_console_artifact_index(
            index_path,
            tmp_path,
        )


def test_d4_oversized_artifact_fails_closed(
    tmp_path,
):
    artifact_path = tmp_path / "artifact.json"
    artifact_path.write_bytes(b"x" * 1025)

    limits = RuntimeHardeningLimits(
        artifact_max_bytes=1024,
    )

    with pytest.raises(
        ValueError,
        match="exceeds size limit",
    ):
        read_runtime_artifact_snapshot(
            artifact_path,
            tmp_path,
            limits=limits,
        )


def test_d4_oversized_index_fails_closed(
    tmp_path,
):
    index_path = tmp_path / "artifact_index.json"
    index_path.write_bytes(b"{" + b" " * 1024)

    limits = RuntimeHardeningLimits(
        artifact_max_bytes=1024,
    )

    with pytest.raises(
        ValueError,
        match="exceeds size limit",
    ):
        load_console_artifact_index(
            index_path,
            tmp_path,
            limits=limits,
        )


def test_d4_outside_index_path_is_rejected(
    tmp_path,
):
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()

    index_path = outside / "artifact_index.json"
    _write_json(
        index_path,
        {"entries": []},
    )

    with pytest.raises(
        ValueError,
        match="outside the allowed root",
    ):
        load_console_artifact_index(
            index_path,
            root,
        )


def test_d4_directory_artifact_is_rejected(
    tmp_path,
):
    directory = tmp_path / "registered"
    directory.mkdir()

    with pytest.raises(
        ValueError,
        match="must be a file",
    ):
        resolve_runtime_artifact_path(
            directory,
            tmp_path,
        )


def _make_symlink_or_skip(
    link: Path,
    target: Path,
    *,
    target_is_directory: bool,
) -> None:
    try:
        link.symlink_to(
            target,
            target_is_directory=target_is_directory,
        )
    except (OSError, NotImplementedError) as exc:
        pytest.skip(
            f"symlink creation unavailable: {exc}"
        )


def test_d4_direct_symlink_is_rejected(
    tmp_path,
):
    target = tmp_path / "target.json"
    _write_json(
        target,
        {"value": "target"},
    )

    link = tmp_path / "artifact.json"
    _make_symlink_or_skip(
        link,
        target,
        target_is_directory=False,
    )

    with pytest.raises(
        ValueError,
        match="symbolic artifact path",
    ):
        resolve_runtime_artifact_path(
            link,
            tmp_path,
        )


def test_d4_intermediate_symlink_is_rejected(
    tmp_path,
):
    target_dir = tmp_path / "target"
    target_dir.mkdir()
    _write_json(
        target_dir / "artifact.json",
        {"value": "target"},
    )

    link_dir = tmp_path / "registered"
    _make_symlink_or_skip(
        link_dir,
        target_dir,
        target_is_directory=True,
    )

    with pytest.raises(
        ValueError,
        match="symbolic artifact path",
    ):
        resolve_runtime_artifact_path(
            link_dir / "artifact.json",
            tmp_path,
        )


def test_d4_symbolic_allowed_root_is_rejected(
    tmp_path,
):
    real_root = tmp_path / "real"
    real_root.mkdir()
    artifact_path = real_root / "artifact.json"
    _write_json(
        artifact_path,
        {"value": "target"},
    )

    root_link = tmp_path / "root-link"
    _make_symlink_or_skip(
        root_link,
        real_root,
        target_is_directory=True,
    )

    with pytest.raises(
        ValueError,
        match="symbolic allowed roots",
    ):
        read_runtime_artifact_snapshot(
            root_link / "artifact.json",
            root_link,
        )


def test_d4_expected_digest_validation_is_strict(
    tmp_path,
):
    artifact_path = tmp_path / "artifact.json"
    _write_json(
        artifact_path,
        {"value": "target"},
    )

    with pytest.raises(
        ValueError,
        match="expected_sha256",
    ):
        read_runtime_artifact_snapshot(
            artifact_path,
            tmp_path,
            expected_sha256="not-a-digest",
        )
