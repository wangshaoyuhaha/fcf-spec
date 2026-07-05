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

__all__ = [
    "AI_CONTEXT_HANDOFF_REQUIRED_FIELDS",
    "UIAppHandoffLoadError",
    "UI_APP_READ_ONLY_CONTRACT",
    "build_ranked_watchlist_view_model",
    "get_read_only_ui_contract",
    "load_ai_context_handoff_payload",
    "summarize_ai_context_handoff_payload",
    "summarize_ranked_watchlist_view_model",
    "validate_ai_context_handoff_payload",
    "validate_ranked_watchlist_view_model",
    "validate_read_only_ui_contract",
]
