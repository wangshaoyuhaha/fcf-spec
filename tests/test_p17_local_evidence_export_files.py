import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_export import build_local_evidence_export_files
from btc_finance_platform.operator_evidence_export import build_local_evidence_export_manifest
from btc_finance_platform.operator_evidence_export import render_operator_evidence_markdown_report
from btc_finance_platform.operator_evidence_export import write_local_evidence_export_files


def test_p17_d1_local_evidence_export_manifest_is_static_and_read_only():
    manifest = build_local_evidence_export_manifest()
    assert manifest["ok"] is True
    assert manifest["export_mode"] == "LOCAL_STATIC_READ_ONLY"
    assert manifest["file_count"] == 3
    assert manifest["deploy_enabled"] is False
    assert manifest["real_trading_enabled"] is False


def test_p17_d2_markdown_report_preserves_release_and_safety_boundary():
    report = render_operator_evidence_markdown_report()
    assert "Operator Evidence Console Export Report" in report
    assert "v14-learning-engine-paper" in report
    assert "no deploy" in report
    assert "no real trading" in report


def test_p17_d3_local_evidence_export_files_can_write_to_temp_dir(tmp_path):
    result = write_local_evidence_export_files(tmp_path / "evidence")
    assert result["ok"] is True
    assert result["written_count"] == 3
    assert result["deploy_enabled"] is False
    assert result["real_trading_enabled"] is False
    for path in result["written_files"]:
        assert os.path.exists(path)
    bundle = build_local_evidence_export_files("runtime/operator_evidence_console")
    assert bundle["file_count"] == 3
    assert bundle["read_only"] is True
