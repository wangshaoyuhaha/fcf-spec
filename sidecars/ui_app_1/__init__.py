"""UI-APP-1 sidecar package."""

from .ai_context_handoff_loader import (
    AI_CONTEXT_HANDOFF_REQUIRED_FIELDS,
    UIAppHandoffLoadError,
    load_ai_context_handoff_payload,
    summarize_ai_context_handoff_payload,
    validate_ai_context_handoff_payload,
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
    "build_operator_review_panel",
    "build_ranked_watchlist_view_model",
    "build_reason_codes_panel",
    "build_risk_flags_panel",
    "build_risk_reason_review_panels",
    "get_read_only_ui_contract",
    "load_ai_context_handoff_payload",
    "summarize_ai_context_handoff_payload",
    "summarize_ranked_watchlist_view_model",
    "validate_ai_context_handoff_payload",
    "validate_ranked_watchlist_view_model",
    "validate_read_only_ui_contract",
    "validate_risk_reason_review_panels",
]
