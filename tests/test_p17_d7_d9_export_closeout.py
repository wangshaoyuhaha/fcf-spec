import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_export import build_local_evidence_export_closeout_checkpoint
from btc_finance_platform.operator_evidence_export import build_local_evidence_export_handoff_packet
from btc_finance_platform.operator_evidence_export import render_local_evidence_export_index_markdown
from btc_finance_platform.operator_evidence_export import write_local_evidence_export_readable_index


def test_p17_d7_readable_index_writer_writes_json_and_markdown(tmp_path):
    result = write_local_evidence_export_readable_index(tmp_path / "export")
    assert result["ok"] is True
    assert result["written_count"] == 2
    assert result["deploy_enabled"] is False
    assert result["real_trading_enabled"] is False
    for path in result["written_files"]:
        assert os.path.exists(path)


def test_p17_d8_export_closeout_checkpoint_passes_safe_bundle():
    checkpoint = build_local_evidence_export_closeout_checkpoint()
    assert checkpoint["ok"] is True
    assert checkpoint["validation_status"] == "PASSED"
    assert checkpoint["paper_only"] is True
    assert checkpoint["deploy_enabled"] is False
    assert checkpoint["real_trading_enabled"] is False


def test_p17_d9_export_handoff_packet_is_ready_for_operator_review():
    packet = build_local_evidence_export_handoff_packet()
    markdown = render_local_evidence_export_index_markdown()
    assert packet["ok"] is True
    assert packet["handoff_status"] == "READY_FOR_OPERATOR_REVIEW"
    assert packet["next_phase_candidate"] == "P18 Local Evidence Console Navigation"
    assert "no real trading" in markdown
    assert packet["operator_review_required"] is True
