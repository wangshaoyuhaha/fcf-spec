"""MODEL-GOVERNANCE-APP-1 package.

This sidecar package is paper-only, local-only, read-only, and review-only.
It records model rule governance metadata for completed local sidecar outputs.
It must not mutate P1-P47 core modules or source artifacts.
"""

from .contract import (
    MODEL_GOVERNANCE_APP_ID,
    MODEL_GOVERNANCE_STAGE_ID,
    build_model_governance_contract,
)

__all__ = [
    "MODEL_GOVERNANCE_APP_ID",
    "MODEL_GOVERNANCE_STAGE_ID",
    "build_model_governance_contract",
]
