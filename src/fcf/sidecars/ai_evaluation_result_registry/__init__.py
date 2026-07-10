"""AI evaluation result registry sidecar."""

from .contract import (
    APP_ID,
    CONTRACT_VERSION,
    IMPORTED_RESULT_STATUSES,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)

__all__ = [
    "APP_ID",
    "CONTRACT_VERSION",
    "IMPORTED_RESULT_STATUSES",
    "STAGE_ID",
    "build_boundary_contract",
    "validate_boundary_contract",
]