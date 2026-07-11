"""Read-only comprehensive report integration sidecar."""

from .d1_boundary_contract import (
    APP_ID,
    CONTRACT_VERSION,
    build_integration_boundary_contract,
    validate_integration_boundary_contract,
)
from .d2_registered_source_loader import (
    SOURCE_APP_ID,
    SOURCE_ARTIFACT_TYPE,
    SOURCE_MODULE,
    build_registered_source_envelope,
    canonical_payload_sha256,
    load_registered_source_from_file,
    load_registered_source_from_mapping,
    validate_registered_source_envelope,
)

__all__ = [
    "APP_ID",
    "CONTRACT_VERSION",
    "SOURCE_APP_ID",
    "SOURCE_ARTIFACT_TYPE",
    "SOURCE_MODULE",
    "build_integration_boundary_contract",
    "validate_integration_boundary_contract",
    "build_registered_source_envelope",
    "canonical_payload_sha256",
    "load_registered_source_from_file",
    "load_registered_source_from_mapping",
    "validate_registered_source_envelope",
]
