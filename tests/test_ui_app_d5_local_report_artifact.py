from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "sidecars" / "ui_app_1" / "local_report_artifact.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "ui_app_local_report_artifact",
        MODULE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_payload():
    return {
        "app_id": "AI-CONTEXT-1",
        "operator_review_summary": {
            "status": "PENDING_OPERATOR_REVIEW",
        },
    }


def sample_view_model():
    return {
        "rows": [
            {
                "rank": 1,
                "symbol": "000001.SZ",
                "display_name": "Ping An Bank",
                "score": 0.82,
                "data_quality_state": "PASS_STRICT",
                "confidence_level": "MEDIUM",
                "reason_codes": ["VOLUME_PRICE_ANOMALY"],
                "risk_flags": ["OPERATOR_REVIEW_REQUIRED"],
            }
        ]
    }


def sample_panels():
    return {
        "panel_group_id": "ui_app_1_risk_reason_review_panels",
        "panels": {},
    }


def test_ui_app_d5_artifact_file_exists():
    assert MODULE_PATH.exists()


def test_ui_app_d5_renders_text_report():
    module = load_module()
    text = module.render_read_only_text_report(
        sample_payload(),
        sample_view_model(),
        sample_panels(),
    )

    assert "UI-APP-1 LOCAL READ-ONLY REPORT" in text
    assert "paper_only: true" in text
    assert "trade_action_enabled: false" in text
    assert "symbol=000001.SZ" in text


def test_ui_app_d5_renders_html_report():
    module = load_module()
    html = module.render_read_only_html_report(
        sample_payload(),
        sample_view_model(),
        sample_panels(),
    )

    assert "<html" in html
    assert "UI-APP-1 Local Read-Only Report" in html
    assert "buy_button_enabled: false" in html
    assert "000001.SZ" in html


def test_ui_app_d5_builds_artifact_bundle():
    module = load_module()
    artifact = module.build_local_report_artifact(
        sample_payload(),
        sample_view_model(),
        sample_panels(),
    )

    assert artifact["artifact_id"] == "ui_app_1_local_read_only_report"
    assert artifact["stage_id"] == "UI-APP-D5"
    assert artifact["paper_only"] is True
    assert artifact["local_only"] is True
    assert artifact["read_only"] is True
    assert artifact["sidecar_only"] is True
    assert artifact["operator_review_required"] is True


def test_ui_app_d5_artifact_blocks_trade_actions():
    module = load_module()
    artifact = module.build_local_report_artifact(
        sample_payload(),
        sample_view_model(),
        sample_panels(),
    )

    assert artifact["trade_action_enabled"] is False
    assert artifact["buy_button_enabled"] is False
    assert artifact["sell_button_enabled"] is False
    assert artifact["order_button_enabled"] is False
    assert artifact["real_execution_enabled"] is False
    assert artifact["core_mutation_enabled"] is False


def test_ui_app_d5_validates_good_artifact():
    module = load_module()
    artifact = module.build_local_report_artifact(
        sample_payload(),
        sample_view_model(),
        sample_panels(),
    )
    result = module.validate_local_report_artifact(artifact)

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["artifact_id"] == "ui_app_1_local_read_only_report"
    assert result["stage_id"] == "UI-APP-D5"


def test_ui_app_d5_validation_rejects_buy_button_enabled():
    module = load_module()
    artifact = module.build_local_report_artifact(
        sample_payload(),
        sample_view_model(),
        sample_panels(),
    )
    artifact["buy_button_enabled"] = True

    result = module.validate_local_report_artifact(artifact)

    assert result["ok"] is False
    assert "artifact_field_mismatch:buy_button_enabled" in result["errors"]
    assert "forbidden_enabled:buy_button_enabled" in result["errors"]


def test_ui_app_d5_writes_local_files(tmp_path):
    module = load_module()
    artifact = module.build_local_report_artifact(
        sample_payload(),
        sample_view_model(),
        sample_panels(),
    )

    result = module.write_local_report_artifact(artifact, tmp_path)

    assert result["ok"] is True
    assert result["paper_only"] is True
    assert result["local_only"] is True
    assert result["read_only"] is True
    assert Path(result["html_path"]).exists()
    assert Path(result["text_path"]).exists()
    assert Path(result["manifest_path"]).exists()


def test_ui_app_d5_empty_candidates_render_empty_state():
    module = load_module()
    html = module.render_read_only_html_report(
        sample_payload(),
        {"rows": []},
        sample_panels(),
    )

    assert "NO_RANKED_WATCHLIST_CANDIDATES" in html


def test_ui_app_d5_rejects_invalid_artifact_before_write(tmp_path):
    module = load_module()
    artifact = module.build_local_report_artifact(
        sample_payload(),
        sample_view_model(),
        sample_panels(),
    )
    artifact["real_execution_enabled"] = True

    try:
        module.write_local_report_artifact(artifact, tmp_path)
    except ValueError as exc:
        assert "invalid_local_report_artifact" in str(exc)
    else:
        raise AssertionError("expected ValueError")
