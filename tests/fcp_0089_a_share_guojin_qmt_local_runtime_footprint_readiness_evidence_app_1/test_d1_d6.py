from __future__ import annotations

import json
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.fcp_0089_a_share_guojin_qmt_local_runtime_footprint_readiness_evidence_app_1 import (
    RuntimeFootprintRegistration,
    RuntimeFootprintSnapshot,
    build_runtime_footprint_evidence,
    render_evidence_json,
    scan_runtime_footprint,
)
from apps.fcp_0089_a_share_guojin_qmt_local_runtime_footprint_readiness_evidence_app_1.runner import (
    main,
)


REQUIRED_DIRS = ("datadir", "datas", "dumps", "log", "quoter", "users")
REQUIRED_FILES = (
    "miniqmtShmStockListCacheSH",
    "miniqmtShmStockListCacheSZ",
    "miniqmtShmTradeDateListCache",
)


def build_footprint(root: Path) -> Path:
    root.mkdir()
    for name in REQUIRED_DIRS:
        (root / name).mkdir()
    for index, name in enumerate(REQUIRED_FILES, start=1):
        (root / name).write_bytes(b"x" * index)
    return root


def test_registration_is_closed_and_immutable():
    registration = RuntimeFootprintRegistration(artifact_id="qmt-runtime-footprint-v1")
    assert registration.metadata_only is True
    assert registration.file_content_read is False
    assert registration.recursive_scan is False
    with pytest.raises(Exception):
        registration.artifact_id = "changed"


def test_ready_scan_is_path_free_and_does_not_read_file_contents(tmp_path, monkeypatch):
    root = build_footprint(tmp_path / "userdata_mini")
    (root / "account-secret-12345").write_bytes(b"sensitive-fixture")
    monkeypatch.setattr(
        Path,
        "read_bytes",
        lambda self: (_ for _ in ()).throw(AssertionError("content read")),
    )

    evidence = scan_runtime_footprint(
        root,
        artifact_id="qmt-runtime-footprint-v1",
    )
    rendered = render_evidence_json(evidence)

    assert evidence.readiness_state == "READY_FOR_OPERATOR_PROBE"
    assert evidence.directory_count == 6
    assert evidence.regular_file_count == 4
    assert evidence.file_content_read is False
    assert evidence.entitlement_proven is False
    assert evidence.terminal_liveness_proven is False
    assert str(root) not in rendered
    assert "account-secret-12345" not in rendered
    assert "sensitive-fixture" not in rendered
    assert isinstance(evidence.as_payload(), MappingProxyType)


def test_missing_footprint_fails_closed(tmp_path):
    root = tmp_path / "userdata_mini"
    root.mkdir()
    (root / "datadir").mkdir()

    evidence = scan_runtime_footprint(root, artifact_id="qmt-runtime-missing-v1")

    assert evidence.readiness_state == "INCOMPLETE_FOOTPRINT"
    assert "MISSING_DIRECTORY_USERS" in evidence.blockers
    assert "MISSING_CACHE_STOCK_LIST_SH" in evidence.blockers
    assert "MINIQMT_ENTITLEMENT_UNPROVEN" in evidence.blockers
    assert evidence.closes_gap is False


def test_top_level_limit_is_enforced(tmp_path):
    root = tmp_path / "userdata_mini"
    root.mkdir()
    for index in range(3):
        (root / f"item-{index}").write_bytes(b"x")
    with pytest.raises(ValueError, match="top-level entry limit"):
        scan_runtime_footprint(
            root,
            artifact_id="qmt-runtime-limit-v1",
            max_top_level_entries=2,
        )


def test_symlink_entry_is_rejected(tmp_path):
    root = build_footprint(tmp_path / "userdata_mini")
    target = tmp_path / "target"
    target.mkdir()
    (root / "linked").symlink_to(target, target_is_directory=True)
    with pytest.raises(ValueError, match="links or reparse points"):
        scan_runtime_footprint(root, artifact_id="qmt-runtime-link-v1")


def test_snapshot_requires_exact_closed_partitions():
    with pytest.raises(ValueError, match="partitions are not exact"):
        RuntimeFootprintSnapshot(
            top_level_entry_count=0,
            directory_count=0,
            regular_file_count=0,
            aggregate_regular_file_bytes=0,
            latest_metadata_time_utc="2026-07-23T00:00:00.000000Z",
            required_directories_present=(),
            required_directories_missing=(),
            required_cache_families_present=(),
            required_cache_families_missing=(
                "STOCK_LIST_SH",
                "STOCK_LIST_SZ",
                "TRADE_DATE_LIST",
            ),
            manifest_sha256="0" * 64,
        )


def test_builder_preserves_non_authorizing_boundary():
    registration = RuntimeFootprintRegistration(artifact_id="qmt-runtime-reference-v1")
    snapshot = RuntimeFootprintSnapshot(
        top_level_entry_count=9,
        directory_count=6,
        regular_file_count=3,
        aggregate_regular_file_bytes=6,
        latest_metadata_time_utc="2026-07-23T00:00:00.000000Z",
        required_directories_present=(
            "DATADIR",
            "DATAS",
            "DUMPS",
            "LOG",
            "QUOTER",
            "USERS",
        ),
        required_directories_missing=(),
        required_cache_families_present=(
            "STOCK_LIST_SH",
            "STOCK_LIST_SZ",
            "TRADE_DATE_LIST",
        ),
        required_cache_families_missing=(),
        manifest_sha256="1" * 64,
    )
    evidence = build_runtime_footprint_evidence(registration, snapshot)
    payload = evidence.as_payload()

    assert evidence.readiness_state == "READY_FOR_OPERATOR_PROBE"
    assert payload["sdk_invoked"] is False
    assert payload["network_used"] is False
    assert payload["account_accessed"] is False
    assert payload["registered_evidence_authority"] is False
    assert payload["realtime_activation_authorized"] is False


def test_cli_emits_canonical_path_free_json(tmp_path, capsys):
    root = build_footprint(tmp_path / "userdata_mini")
    result = main(
        [
            "--directory",
            str(root),
            "--artifact-id",
            "qmt-runtime-cli-v1",
        ]
    )
    captured = capsys.readouterr()
    payload = json.loads(captured.out)

    assert result == 0
    assert payload["readiness_state"] == "READY_FOR_OPERATOR_PROBE"
    assert str(root) not in captured.out
    assert captured.err == ""


def test_cli_fails_closed_without_directory(capsys, tmp_path):
    result = main(
        [
            "--directory",
            str(tmp_path / "missing"),
            "--artifact-id",
            "qmt-runtime-missing-cli-v1",
        ]
    )
    captured = capsys.readouterr()
    assert result == 2
    assert captured.out == ""
    assert json.loads(captured.err) == {
        "error": "LOCAL_RUNTIME_FOOTPRINT_SCAN_FAILED"
    }
