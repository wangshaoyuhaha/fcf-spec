"""AI evaluation comparison sidecar."""

from .contract import (
    ALLOWED_INPUTS,
    ALLOWED_OUTPUTS,
    APP_ID,
    COMPARISON_MODES,
    COMPARISON_STATUSES,
    CONTRACT_VERSION,
    FORBIDDEN_COMPARISON_STATUSES,
    REQUIRED_COMPARISON_DIMENSIONS,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)

__all__ = [
    "ALLOWED_INPUTS",
    "ALLOWED_OUTPUTS",
    "APP_ID",
    "COMPARISON_MODES",
    "COMPARISON_STATUSES",
    "CONTRACT_VERSION",
    "FORBIDDEN_COMPARISON_STATUSES",
    "REQUIRED_COMPARISON_DIMENSIONS",
    "STAGE_ID",
    "build_boundary_contract",
    "validate_boundary_contract",
]