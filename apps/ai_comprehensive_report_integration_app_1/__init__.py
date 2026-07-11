"""Read-only comprehensive report integration sidecar."""

from .d1_boundary_contract import (
    APP_ID,
    CONTRACT_VERSION,
    build_integration_boundary_contract,
    validate_integration_boundary_contract,
)

__all__ = [
    "APP_ID",
    "CONTRACT_VERSION",
    "build_integration_boundary_contract",
    "validate_integration_boundary_contract",
]
