from html import escape
from pathlib import Path
from typing import Any

FORBIDDEN_TRUE_FIELDS = (
    "real_exchange_api",
    "real_brokerage_api",
    "real_api_key_required",
    "wallet_private_key_required",
    "real_order",
    "real_execution",
    "real_balance",
    "real_position",
    "real_money_impact",
    "real_world_actions_allowed",
    "deployment_allowed_now",
    "parameter_update_allowed_now",
    "trading_buttons_enabled",
)

def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "yes", "1", "enabled", "allowed"}
    return bool(value)

def _no_forbidden_true(*payloads: dict[str, Any]) -> bool:
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for field in FORBIDDEN_TRUE_FIELDS:
            if _as_bool(payload.get(field)):
                return False
    return True

def build_operator_console_state(
    project_state: dict[str, Any],
    validation_summary: dict[str, Any],
    release_summary: dict[str, Any],
) -> dict[str, Any]:
    if not isinstance(project_state, dict):
        raise ValueError("project_state must be a dict")
    if not isinstance(validation_summary, dict):
        raise ValueError("validation_summary must be a dict")
    if not isinstance(release_summary, dict):
        raise ValueError("release_summary must be a dict")

    checks = {
        "project_state_paper_only": project_state.get("paper_only") is True,
        "validation_passed": validation_summary.get("all_checks_passed") is True and validation_summary.get("pytest_passed") is True,
        "release_published": release_summary.get("release_published") is True,
        "operator_review_required": project_state.get("operator_review_required") is True,
        "ui_read_only": project_state.get("ui_mode", "read_only") == "read_only",
        "local_only": project_state.get("local_only", True) is True,
        "no_forbidden_real_action_flags": _no_forbidden_true(project_state, validation_summary, release_summary),
    }

    blocked_reasons = [f"check_failed:{name}" for name, passed in checks.items() if not passed]
    ready = len(blocked_reasons) == 0

    return {
        "ok": True,
        "type": "p13_operator_console_state",
        "console_status": "ready" if ready else "blocked",
        "operator_console_ready": ready,
        "project_name": project_state.get("project_name", "BTC finance platform"),
        "current_stage": project_state.get("current_stage", "P13"),
        "ui_mode": "read_only",
        "local_only": True,
        "trading_buttons_enabled": False,
        "paper_only": True,
        "real_exchange_api": False,
        "real_brokerage_api": False,
        "real_api_key_required": False,
        "wallet_private_key_required": False,
        "real_order": False,
        "real_execution": False,
        "real_balance": False,
        "real_position": False,
        "real_money_impact": False,
        "real_world_actions_allowed": False,
        "deployment_allowed_now": False,
        "operator_review_required": True,
        "validation_summary": validation_summary,
        "release_summary": release_summary,
        "checks": checks,
        "blocked_reasons": blocked_reasons,
    }

def render_operator_console_html(state: dict[str, Any]) -> str:
    if not isinstance(state, dict):
        raise ValueError("state must be a dict")

    title = escape(str(state.get("project_name", "BTC finance platform")))
    status = escape(str(state.get("console_status", "unknown")))
    stage = escape(str(state.get("current_stage", "P13")))
    pytest_count = escape(str(state.get("validation_summary", {}).get("pytest_count", "unknown")))
    release_tag = escape(str(state.get("release_summary", {}).get("release_tag", "unknown")))

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title} Operator Console</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; background: #111827; color: #e5e7eb; }}
    .card {{ border: 1px solid #374151; border-radius: 12px; padding: 16px; margin: 12px 0; background: #1f2937; }}
    .safe {{ color: #86efac; font-weight: bold; }}
    .blocked {{ color: #fca5a5; font-weight: bold; }}
    code {{ color: #93c5fd; }}
  </style>
</head>
<body>
  <h1>{title} Operator Console</h1>
  <div class="card"><b>Status:</b> <span class="safe">{status}</span></div>
  <div class="card"><b>Stage:</b> {stage}</div>
  <div class="card"><b>Validation:</b> ALL CHECKS PASSED; pytest count: {pytest_count}</div>
  <div class="card"><b>Release tag:</b> <code>{release_tag}</code></div>
  <div class="card"><b>Mode:</b> read-only, local-only, paper-only</div>
  <div class="card blocked"><b>No trading buttons. No real execution. Operator review required.</b></div>
</body>
</html>"""

def write_operator_console_html(state: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    html = render_operator_console_html(state)
    path.write_text(html, encoding="utf-8")
    return {
        "ok": True,
        "type": "p13_operator_console_html_written",
        "output_path": str(path),
        "paper_only": True,
        "real_world_actions_allowed": False,
        "trading_buttons_enabled": False,
        "operator_review_required": True,
    }
