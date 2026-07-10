"""AI contrarian challenge sidecar."""

from .contract import (
    ALLOWED_INPUTS,
    ALLOWED_OUTPUTS,
    APP_ID,
    CHALLENGE_CATEGORIES,
    CHALLENGE_STATUSES,
    CONTRACT_VERSION,
    FORBIDDEN_OUTCOMES,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)

__all__ = [
    "ALLOWED_INPUTS",
    "ALLOWED_OUTPUTS",
    "APP_ID",
    "CHALLENGE_CATEGORIES",
    "CHALLENGE_STATUSES",
    "CONTRACT_VERSION",
    "FORBIDDEN_OUTCOMES",
    "STAGE_ID",
    "build_boundary_contract",
    "validate_boundary_contract",
]