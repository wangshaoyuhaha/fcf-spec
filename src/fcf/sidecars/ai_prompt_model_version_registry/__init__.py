"""AI prompt and model version registry sidecar."""

from .contract import (
    APP_ID,
    CONTRACT_VERSION,
    build_contract,
    validate_contract,
)

__all__ = [
    "APP_ID",
    "CONTRACT_VERSION",
    "build_contract",
    "validate_contract",
]
