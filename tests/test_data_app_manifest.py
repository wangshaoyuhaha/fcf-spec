import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from data_app.manifest import build_data_app_manifest_for_file
from data_app.manifest import build_data_app_manifest_for_files
from data_app.manifest import file_sha256
from data_app.manifest import validate_data_app_manifest


CSV_FIXTURE = Path(ROOT) / "data_app" / "fixtures" / "a_share_sample.csv"
JSON_FIXTURE = Path(ROOT) / "data_app" / "fixtures" / "a_share_sample.json"


def test_file_sha256_returns_stable_hash():
    first = file_sha256(CSV_FIXTURE)
    second = file_sha256(CSV_FIXTURE)

    assert first == second
    assert len(first) == 64


def test_build_data_app_manifest_for_file_contains_counts_and_checksum():
    result = build_data_app_manifest_for_file(CSV_FIXTURE)

    assert result["app"] == "DATA-APP"
    assert result["market"] == "A_SHARE"
    assert result["source_type"] == "csv"
    assert result["row_count"] == 2
    assert result["accepted_count"] == 2
    assert result["rejected_count"] == 0
    assert len(result["checksum_sha256"]) == 64
    assert result["manifest_id"].startswith("DATAAPP-A-SHARE-")


def test_data_app_manifest_preserves_safety_boundary():
    result = build_data_app_manifest_for_file(JSON_FIXTURE)

    assert result["paper_only"] is True
    assert result["local_only"] is True
    assert result["read_only"] is True
    assert result["operator_review_required"] is True
    assert result["real_exchange_api"] is False
    assert result["real_brokerage_api"] is False
    assert result["api_key_required"] is False
    assert result["real_order_allowed"] is False
    assert result["real_execution_allowed"] is False
    assert result["real_money_impact_allowed"] is False


def test_build_data_app_manifest_for_files_aggregates_sources():
    result = build_data_app_manifest_for_files([CSV_FIXTURE, JSON_FIXTURE])

    assert result["source_count"] == 2
    assert result["row_count"] == 4
    assert result["accepted_count"] == 4
    assert result["rejected_count"] == 0
    assert result["all_sources_ok"] is True
    assert len(result["sources"]) == 2
    assert result["manifest_id"].startswith("DATAAPP-A-SHARE-BATCH-")


def test_validate_data_app_manifest_passes_for_file_manifest():
    manifest = build_data_app_manifest_for_file(CSV_FIXTURE)
    result = validate_data_app_manifest(manifest)

    assert result["ok"] is True
    assert result["app"] == "DATA-APP"
    assert result["manifest_id"] == manifest["manifest_id"]
    assert all(result["checks"].values())


def test_manifest_rejects_empty_file_list():
    with pytest.raises(ValueError, match="file_paths must not be empty"):
        build_data_app_manifest_for_files([])
