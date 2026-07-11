"""Deterministic comprehensive report consumer binding sidecar."""

from .d1_binding_contract import (
    APP_ID,
    CONTRACT_VERSION,
    FORBIDDEN_BEHAVIORS,
    REQUIRED_CONSUMERS,
    REQUIRED_CONTENT_FIELDS,
    REQUIRED_IDENTITY_FIELDS,
    SOURCE_APP_ID,
    SOURCE_PACKAGE,
    SOURCE_PACKET_TYPE,
    build_consumer_binding_contract,
    validate_consumer_binding_contract,
)

__all__ = [
    "APP_ID",
    "CONTRACT_VERSION",
    "FORBIDDEN_BEHAVIORS",
    "REQUIRED_CONSUMERS",
    "REQUIRED_CONTENT_FIELDS",
    "REQUIRED_IDENTITY_FIELDS",
    "SOURCE_APP_ID",
    "SOURCE_PACKAGE",
    "SOURCE_PACKET_TYPE",
    "build_consumer_binding_contract",
    "validate_consumer_binding_contract",
]
