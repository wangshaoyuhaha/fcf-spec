import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from btc_finance_platform.operator_evidence_export import build_local_evidence_export_integrity_index
from btc_finance_platform.operator_evidence_export import build_local_evidence_export_readable_index
from btc_finance_platform.operator_evidence_export import validate_local_evidence_export_bundle


def test_p17_d4_local_evidence_export_integrity_index_has_hashes():
    index = build_local_evidence_export_integrity_index()
    assert index["ok"] is True
    assert index["file_count"] == 3
    assert all(len(item["sha256"]) == 64 for item in index["items"])
    assert index["deploy_enabled"] is False
    assert index["real_trading_enabled"] is False


def test_p17_d5_local_evidence_export_bundle_validator_passes_safe_bundle():
    result = validate_local_evidence_export_bundle()
    assert result["ok"] is True
    assert result["status"] == "PASSED"
    assert result["all_read_only"] is True
    assert result["safety_ok"] is True
    assert result["deploy_enabled"] is False


def test_p17_d6_local_evidence_export_readable_index_is_operator_safe():
    index = build_local_evidence_export_readable_index()
    assert index["ok"] is True
    assert index["title"] == "P17 Local Evidence Console Export Index"
    assert index["validation_status"] == "PASSED"
    assert index["file_count"] == 3
    assert index["operator_review_required"] is True
