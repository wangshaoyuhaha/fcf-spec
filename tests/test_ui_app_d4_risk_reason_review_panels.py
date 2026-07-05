from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "sidecars" / "ui_app_1" / "risk_reason_review_panels.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "ui_app_risk_reason_review_panels",
        MODULE_PATH,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sample_handoff_payload():
    return {
        "operator_review_summary": {
            "status": "PENDING_OPERATOR_REVIEW",
            "required": True,
        }
    }


def sample_view_model():
    return {
        "rows": [
            {
                "symbol": "000001.SZ",
                "reason_codes": [
                    "VOLUME_PRICE_ANOMALY",
                    "THEME_LINKAGE_CONFIRMED",
                ],
                "risk_flags": [
                    "OPERATOR_REVIEW_REQUIRED",
                    "LOW_CONFIDENCE",
                ],
                "operator_review_required": True,
            },
            {
                "symbol": "600000.SH",
                "reason_codes": [
                    "WATCHLIST_ONLY",
                ],
                "risk_flags": [
                    "DATA_QUALITY_LIMITED",
                ],
                "operator_review_required": True,
            },
        ]
    }


def test_ui_app_d4_panel_file_exists():
    assert MODULE_PATH.exists()


def test_ui_app_d4_builds_reason_codes_panel():
    module = load_module()
    panel = module.build_reason_codes_panel(sample_view_model())

    assert panel["panel_id"] == "reason_codes_panel"
    assert panel["stage_id"] == "UI-APP-D4"
    assert panel["total_reason_code_count"] == 3
    assert panel["unique_reason_code_count"] == 3
    assert panel["candidate_reason_codes"]["000001.SZ"] == [
        "VOLUME_PRICE_ANOMALY",
        "THEME_LINKAGE_CONFIRMED",
    ]


def test_ui_app_d4_builds_risk_flags_panel():
    module = load_module()
    panel = module.build_risk_flags_panel(sample_view_model())

    assert panel["panel_id"] == "risk_flags_panel"
    assert panel["total_risk_flag_count"] == 3
    assert panel["unique_risk_flag_count"] == 3
    assert "LOW_CONFIDENCE" in panel["high_attention_flags"]
    assert "DATA_QUALITY_LIMITED" in panel["high_attention_flags"]


def test_ui_app_d4_builds_operator_review_panel():
    module = load_module()
    panel = module.build_operator_review_panel(
        sample_handoff_payload(),
        sample_view_model(),
    )

    assert panel["panel_id"] == "operator_review_summary_panel"
    assert panel["review_status"] == "PENDING_OPERATOR_REVIEW"
    assert panel["review_required"] is True
    assert panel["review_bypass_allowed"] is False
    assert panel["candidate_count"] == 2
    assert panel["pending_review_count"] == 2


def test_ui_app_d4_panels_are_read_only():
    module = load_module()
    group = module.build_risk_reason_review_panels(
        sample_handoff_payload(),
        sample_view_model(),
    )

    assert group["paper_only"] is True
    assert group["local_only"] is True
    assert group["read_only"] is True
    assert group["sidecar_only"] is True
    assert group["trade_action_enabled"] is False
    assert group["buy_button_enabled"] is False
    assert group["sell_button_enabled"] is False
    assert group["order_button_enabled"] is False


def test_ui_app_d4_panel_group_contains_expected_panels():
    module = load_module()
    group = module.build_risk_reason_review_panels(
        sample_handoff_payload(),
        sample_view_model(),
    )

    assert group["panel_group_id"] == "ui_app_1_risk_reason_review_panels"
    assert group["stage_id"] == "UI-APP-D4"
    assert group["panel_count"] == 3
    assert set(group["panels"]) == {
        "reason_codes_panel",
        "risk_flags_panel",
        "operator_review_summary_panel",
    }


def test_ui_app_d4_operator_actions_are_safe():
    module = load_module()
    panel = module.build_operator_review_panel(
        sample_handoff_payload(),
        sample_view_model(),
    )

    assert "read_report" in panel["allowed_operator_actions"]
    assert "inspect_reason_codes" in panel["allowed_operator_actions"]
    assert "inspect_risk_flags" in panel["allowed_operator_actions"]
    assert "record_paper_review_status" in panel["allowed_operator_actions"]

    assert "buy" in panel["forbidden_operator_actions"]
    assert "sell" in panel["forbidden_operator_actions"]
    assert "place_order" in panel["forbidden_operator_actions"]
    assert "bypass_review" in panel["forbidden_operator_actions"]


def test_ui_app_d4_validates_good_panel_group():
    module = load_module()
    group = module.build_risk_reason_review_panels(
        sample_handoff_payload(),
        sample_view_model(),
    )
    result = module.validate_risk_reason_review_panels(group)

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["panel_count"] == 3
    assert result["stage_id"] == "UI-APP-D4"


def test_ui_app_d4_validation_rejects_buy_button_enabled():
    module = load_module()
    group = module.build_risk_reason_review_panels(
        sample_handoff_payload(),
        sample_view_model(),
    )
    group["buy_button_enabled"] = True

    result = module.validate_risk_reason_review_panels(group)

    assert result["ok"] is False
    assert "expected_false:buy_button_enabled" in result["errors"]


def test_ui_app_d4_validation_rejects_panel_order_button_enabled():
    module = load_module()
    group = module.build_risk_reason_review_panels(
        sample_handoff_payload(),
        sample_view_model(),
    )
    group["panels"]["risk_flags_panel"]["order_button_enabled"] = True

    result = module.validate_risk_reason_review_panels(group)

    assert result["ok"] is False
    assert (
        "panel_expected_false:risk_flags_panel:order_button_enabled"
        in result["errors"]
    )


def test_ui_app_d4_empty_view_model_panels_have_empty_state():
    module = load_module()
    empty = {"rows": []}

    reason_panel = module.build_reason_codes_panel(empty)
    risk_panel = module.build_risk_flags_panel(empty)

    assert reason_panel["empty_state"] == "NO_REASON_CODES"
    assert risk_panel["empty_state"] == "NO_RISK_FLAGS"
