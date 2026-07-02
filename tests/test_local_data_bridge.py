import json
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.local_data_bridge import build_local_data_audit_report
from btc_finance_platform.local_data_bridge import build_local_paper_analysis_inputs
from btc_finance_platform.local_data_bridge import build_local_paper_dataset
from btc_finance_platform.local_data_bridge import write_local_data_audit_report


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_build_local_paper_dataset_combines_json_and_csv():
    result = build_local_paper_dataset(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "local_paper_dataset"
    assert result["source_count"] == 2
    assert result["total_records"] == 6
    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["operator_review_required"] is True


def test_build_local_paper_analysis_inputs_contains_only_analysis_fields():
    result = build_local_paper_analysis_inputs(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "local_paper_analysis_inputs"
    assert result["count"] == 6
    assert set(result["items"][0].keys()) == {"symbol", "price", "reference_price"}


def test_build_local_paper_analysis_inputs_keeps_operator_review_required():
    result = build_local_paper_analysis_inputs(SOURCES)

    assert result["paper_only"] is True
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_build_local_data_audit_report_has_required_safety_checks():
    result = build_local_data_audit_report(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "local_data_audit_report"
    assert all(result["checks"].values())
    assert result["checks"]["paper_only_preserved"] is True
    assert result["checks"]["no_real_exchange_api"] is True
    assert result["checks"]["no_real_order"] is True
    assert result["checks"]["operator_review_required"] is True


def test_write_local_data_audit_report_to_tmp_path(tmp_path):
    output = tmp_path / "local_data_audit_report.json"
    result = write_local_data_audit_report(SOURCES, output)

    assert result["ok"] is True
    assert result["type"] == "local_data_audit_report_written"
    assert output.exists()

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["type"] == "local_data_audit_report"
    assert saved["ok"] is True


def test_bridge_rejects_empty_file_list():
    with pytest.raises(ValueError, match="file_paths must not be empty"):
        build_local_paper_dataset([])


def test_audit_report_record_count_matches_manifest():
    result = build_local_data_audit_report(SOURCES)

    assert result["total_records"] == 6
    assert result["manifest"]["total_records"] == 6
    assert result["checks"]["record_count_matches_manifest"] is True
    assert result["checks"]["source_files_have_sha256"] is True
