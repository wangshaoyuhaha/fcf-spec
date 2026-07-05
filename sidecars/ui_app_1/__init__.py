"""UI-APP-1 sidecar package."""

from .read_only_contract import (
    UI_APP_READ_ONLY_CONTRACT,
    get_read_only_ui_contract,
    validate_read_only_ui_contract,
)

__all__ = [
    "UI_APP_READ_ONLY_CONTRACT",
    "get_read_only_ui_contract",
    "validate_read_only_ui_contract",
]
