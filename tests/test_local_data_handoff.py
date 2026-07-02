import json
import os
import sys
from pathlib import Path

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.local_data_handoff import build_local_analysis_handoff_package
from btc_finance_platform.local_data_handoff import build_local_data_quality_gate
from btc_finance_platform.local_data_handoff import write_local_analysis_handoff_package


JSON_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.json"
CSV_FIXTURE = Path(ROOT) / "fixtures" / "sample_paper_batch.csv"
SOURCES = [JSON_FIXTURE, CSV_FIXTURE]


def test_build_local_data_quality_gate_passes_for_fixtures():
    result = build_local_data_quality_gate(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "local_data_quality_gate"
    assert result["gate"] == "pass"
    assert result["count"] == 6
    assert all(result["checks"].values())


def test_quality_gate_preserves_paper_only_boundary():
    result = build_local_data_quality_gate(SOURCES)

    assert result["paper_only"] is True
    assert result["real_exchange_api"] is False
    assert result["real_api_key_required"] is False
    assert result["wallet_private_key_required"] is False
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_balance"] is False
    assert result["real_position"] is False
    assert result["real_money_impact"] is False
    assert result["operator_review_required"] is True


def test_build_local_analysis_handoff_package_contains_inputs_audit_and_gate():
    result = build_local_analysis_handoff_package(SOURCES)

    assert result["ok"] is True
    assert result["type"] == "local_analysis_handoff_package"
    assert result["gate"] == "pass"
    assert result["count"] == 6
    assert "analysis_inputs" in result
    assert "audit_report" in result
    assert "quality_gate" in result


def test_handoff_package_next_step_requires_operator_review():
    result = build_local_analysis_handoff_package(SOURCES)

    assert result["next_step"] == "paper_analysis_only_after_operator_review"
    assert result["operator_review_required"] is True
    assert result["real_order"] is False
    assert result["real_execution"] is False
    assert result["real_money_impact"] is False


def test_write_local_analysis_handoff_package(tmp_path):
    output = tmp_path / "handoff" / "local_analysis_handoff_package.json"
    result = write_local_analysis_handoff_package(SOURCES, output)

    assert result["ok"] is True
    assert result["type"] == "local_analysis_handoff_package_written"
    assert output.exists()

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["type"] == "local_analysis_handoff_package"
    assert saved["gate"] == "pass"


def test_quality_gate_rejects_bad_fixture_file(tmp_path):
    bad_file = tmp_path / "bad.csv"
    bad_file.write_text(
        "symbol,price,reference_price\nBTCUSDT,0,64000\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="price must be positive"):
        build_local_data_quality_gate([bad_file])


def test_handoff_rejects_empty_source_list():
    with pytest.raises(ValueError, match="file_paths must not be empty"):
        build_local_analysis_handoff_package([])
