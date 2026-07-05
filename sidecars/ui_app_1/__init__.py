"""UI-APP-1 sidecar package."""

from .ai_context_handoff_loader import (
    AI_CONTEXT_HANDOFF_REQUIRED_FIELDS,
    UIAppHandoffLoadError,
    load_ai_context_handoff_payload,
    summarize_ai_context_handoff_payload,
    validate_ai_context_handoff_payload,
)
from .local_report_artifact import (
    build_local_report_artifact,
    render_read_only_html_report,
    render_read_only_text_report,
    validate_local_report_artifact,
    write_local_report_artifact,
)
from .ranked_watchlist_view_model import (
    build_ranked_watchlist_view_model,
    summarize_ranked_watchlist_view_model,
    validate_ranked_watchlist_view_model,
)
from .read_only_contract import (
    UI_APP_READ_ONLY_CONTRACT,
    get_read_only_ui_contract,
    validate_read_only_ui_contract,
)
from .risk_reason_review_panels import (
    build_operator_review_panel,
    build_reason_codes_panel,
    build_risk_flags_panel,
    build_risk_reason_review_panels,
    validate_risk_reason_review_panels,
)

__all__ = [
    "AI_CONTEXT_HANDOFF_REQUIRED_FIELDS",
    "UIAppHandoffLoadError",
    "UI_APP_READ_ONLY_CONTRACT",
    "build_local_report_artifact",
    "build_operator_review_panel",
    "build_ranked_watchlist_view_model",
    "build_reason_codes_panel",
    "build_risk_flags_panel",
    "build_risk_reason_review_panels",
    "get_read_only_ui_contract",
    "load_ai_context_handoff_payload",
    "render_read_only_html_report",
    "render_read_only_text_report",
    "summarize_ai_context_handoff_payload",
    "summarize_ranked_watchlist_view_model",
    "validate_ai_context_handoff_payload",
    "validate_local_report_artifact",
    "validate_ranked_watchlist_view_model",
    "validate_read_only_ui_contract",
    "validate_risk_reason_review_panels",
    "write_local_report_artifact",
]

from .final_handoff import (
    UI_APP_D6_FINAL_HANDOFF,
    get_ui_app_d6_final_handoff,
    validate_ui_app_d6_final_handoff,
)

__all__.extend(
    [
        "UI_APP_D6_FINAL_HANDOFF",
        "get_ui_app_d6_final_handoff",
        "validate_ui_app_d6_final_handoff",
    ]
)
