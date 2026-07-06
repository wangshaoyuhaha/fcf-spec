from copy import deepcopy

from apps.watchlist_lifecycle_app_1.contract import UPSTREAM_READ_SOURCES
from apps.watchlist_lifecycle_app_1.source_loader import (
    STAGE_ID,
    build_watchlist_lifecycle_source_manifest,
    inspect_source_candidate,
    validate_watchlist_lifecycle_source_manifest,
)


def test_d2_source_manifest_represents_all_upstream_sources(tmp_path):
    manifest = build_watchlist_lifecycle_source_manifest(root_path=str(tmp_path))

    assert manifest["stage_id"] == STAGE_ID
    assert manifest["read_only"] is True
    assert manifest["content_loaded"] is False
    assert manifest["operator_review_required"] is True
    assert set(UPSTREAM_READ_SOURCES).issubset(set(manifest["represented_upstream_sources"]))
    assert manifest["source_record_count"] == len(UPSTREAM_READ_SOURCES)

    validation = validate_watchlist_lifecycle_source_manifest(manifest)

    assert validation["valid"] is True
    assert validation["issues"] == []


def test_d2_source_loader_records_file_metadata_without_loading_content(tmp_path):
    source_file = tmp_path / "docs" / "data_app_1" / "packet.json"
    source_file.parent.mkdir(parents=True)
    source_file.write_text('{"sample": true}', encoding="utf-8")

    record = inspect_source_candidate(
        root_path=str(tmp_path),
        app_id="DATA-APP-1",
        source_kind="fixture",
        relative_path="docs/data_app_1/packet.json",
    )

    assert record["status"] == "PRESENT"
    assert record["path_type"] == "file"
    assert record["exists"] is True
    assert record["size_bytes"] > 0
    assert record["file_count"] == 1
    assert record["sha256"]
    assert record["content_loaded"] is False
    assert record["read_only"] is True
    assert record["source_content_mutation_allowed"] is False
    assert "sample" not in record


def test_d2_source_manifest_allows_missing_paths_as_metadata_not_failure(tmp_path):
    manifest = build_watchlist_lifecycle_source_manifest(root_path=str(tmp_path))

    assert manifest["missing_source_count"] == len(UPSTREAM_READ_SOURCES)
    assert manifest["present_source_count"] == 0

    for record in manifest["source_records"]:
        assert record["status"] == "MISSING"
        assert record["exists"] is False
        assert record["content_loaded"] is False
        assert record["read_only"] is True


def test_d2_source_manifest_validator_rejects_mutation_or_content_loading(tmp_path):
    manifest = build_watchlist_lifecycle_source_manifest(root_path=str(tmp_path))
    mutated = deepcopy(manifest)

    mutated["content_loaded"] = True
    mutated["source_content_mutation_allowed"] = True
    mutated["source_records"][0]["content_loaded"] = True
    mutated["source_records"][0]["source_overwrite_allowed"] = True

    validation = validate_watchlist_lifecycle_source_manifest(mutated)

    assert validation["valid"] is False
    assert "content_loaded must be false" in validation["issues"]
    assert "source_content_mutation_allowed must be false" in validation["issues"]
    assert any("content_loaded must be false" in issue for issue in validation["issues"])
    assert any("source_overwrite_allowed must be false" in issue for issue in validation["issues"])
