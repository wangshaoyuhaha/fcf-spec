"""Deterministic comprehensive-report consumer activation package."""

from .d1_activation_contract import (
    ACTIVATION_SURFACES,
    PHASE_ID,
    SOURCE_BINDING_PACKAGE,
    ActivationContract,
    ActivationEntryPointCandidate,
    build_activation_contract,
    discover_production_entry_point_candidates,
)

__all__ = [
    "ACTIVATION_SURFACES",
    "PHASE_ID",
    "SOURCE_BINDING_PACKAGE",
    "ActivationContract",
    "ActivationEntryPointCandidate",
    "build_activation_contract",
    "discover_production_entry_point_candidates",
]
