"""SIGNAL-VALIDATION-APP-1 package.

This sidecar package is paper-only, local-only, read-only, and review-only.
It must not mutate P1-P47 core modules or source artifacts.
"""

from .contract import (
    SIGNAL_VALIDATION_APP_ID,
    SIGNAL_VALIDATION_STAGE_ID,
    build_signal_validation_contract,
)

__all__ = [
    "SIGNAL_VALIDATION_APP_ID",
    "SIGNAL_VALIDATION_STAGE_ID",
    "build_signal_validation_contract",
]
