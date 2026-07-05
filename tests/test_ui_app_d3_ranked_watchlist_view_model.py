from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "sidecars" / "ui_app_1" / "ranked_watchlist_view_model.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "ui_app_ranked_watchlist_view_model",
        MODULE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_payload():
    return {
        "ranked_watchlist": [
            {
                "symbol": "000001.SZ",
                "display_name": "Ping An Bank",
                "rank": 1,
                "score": 0.82,
                "score_breakdown": {
                    "volume_price": 0.30,
                    "theme_linkage": 0.22,
                    "fund_flow_proxy": 0.30,
                },
                "reason_codes": [
                    "VOLUME_PRICE_ANOMALY",
                    "THEME_LINKAGE_CONFIRMED",
                ],
                "risk_flags": [
                    "OPERATOR_REVIEW_REQUIRED",
                ],
                "data_quality_state": "PASS_STRICT",
                "confidence_level": "MEDIUM",
            },
            {
                "symbol": "600000.SH",
                "rank": 2,
                "score_breakdown": {
                    "volume_price": 0.10,
                    "theme_linkage": 0.20,
                },
                "reason_codes": ["WATCHLIST_ONLY"],
                "risk_flags": ["LOW_CONFIDENCE"],
                "data_quality_state": "PASS_LIMITED",
                "confidence_level": "LOW",
            },
        ]
    }


def test_ui_app_d3_view_model_file_exists():
    assert MODULE_PATH.exists()


def test_ui_app_d3_builds_ranked_watchlist_rows():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model(sample_payload())

    assert view_model["view_model_id"] == "ui_app_1_ranked_watchlist_view_model"
    assert view_model["stage_id"] == "UI-APP-D3"
    assert view_model["row_count"] == 2
    assert view_model["rows"][0]["symbol"] == "000001.SZ"
    assert view_model["rows"][1]["symbol"] == "600000.SH"


def test_ui_app_d3_view_model_is_read_only_sidecar():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model(sample_payload())

    assert view_model["paper_only"] is True
    assert view_model["local_only"] is True
    assert view_model["read_only"] is True
    assert view_model["sidecar_only"] is True


def test_ui_app_d3_view_model_blocks_action_buttons():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model(sample_payload())

    assert view_model["trade_action_enabled"] is False
    assert view_model["buy_button_enabled"] is False
    assert view_model["sell_button_enabled"] is False
    assert view_model["order_button_enabled"] is False

    for row in view_model["rows"]:
        assert row["trade_action_enabled"] is False
        assert row["buy_button_enabled"] is False
        assert row["sell_button_enabled"] is False
        assert row["order_button_enabled"] is False


def test_ui_app_d3_operator_review_required_for_all_rows():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model(sample_payload())

    assert view_model["operator_review_required"] is True
    for row in view_model["rows"]:
        assert row["operator_review_required"] is True


def test_ui_app_d3_preserves_reason_codes_and_risk_flags():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model(sample_payload())

    first = view_model["rows"][0]
    assert "VOLUME_PRICE_ANOMALY" in first["reason_codes"]
    assert "THEME_LINKAGE_CONFIRMED" in first["reason_codes"]
    assert "OPERATOR_REVIEW_REQUIRED" in first["risk_flags"]


def test_ui_app_d3_calculates_score_from_breakdown_when_missing():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model(sample_payload())

    second = view_model["rows"][1]
    assert second["score"] == 0.3


def test_ui_app_d3_handles_empty_ranked_watchlist():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model({"ranked_watchlist": []})

    assert view_model["row_count"] == 0
    assert view_model["rows"] == []
    assert view_model["empty_state"] == "NO_RANKED_WATCHLIST_CANDIDATES"


def test_ui_app_d3_validates_good_view_model():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model(sample_payload())
    result = module.validate_ranked_watchlist_view_model(view_model)

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["row_count"] == 2
    assert result["stage_id"] == "UI-APP-D3"


def test_ui_app_d3_validation_rejects_enabled_buy_button():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model(sample_payload())
    view_model["rows"][0]["buy_button_enabled"] = True

    result = module.validate_ranked_watchlist_view_model(view_model)

    assert result["ok"] is False
    assert "row_buy_button_enabled:1" in result["errors"]


def test_ui_app_d3_summarizes_view_model_counts():
    module = load_module()
    view_model = module.build_ranked_watchlist_view_model(sample_payload())
    summary = module.summarize_ranked_watchlist_view_model(view_model)

    assert summary["ok"] is True
    assert summary["row_count"] == 2
    assert summary["risk_flag_count"] == 2
    assert summary["reason_code_count"] == 3
    assert summary["operator_review_required"] is True
    assert summary["trade_action_enabled"] is False
