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
from .d2_operator_review_activation import (
    OPERATOR_REVIEW_CONSUMER_ID,
    OPERATOR_REVIEW_STATUS,
    OperatorReviewActivationPacket,
    build_operator_review_activation_packet,
    validate_operator_review_activation_packet,
)

__all__ = [
    "ACTIVATION_SURFACES",
    "PHASE_ID",
    "SOURCE_BINDING_PACKAGE",
    "ActivationContract",
    "ActivationEntryPointCandidate",
    "build_activation_contract",
    "discover_production_entry_point_candidates",
    "OPERATOR_REVIEW_CONSUMER_ID",
    "OPERATOR_REVIEW_STATUS",
    "OperatorReviewActivationPacket",
    "build_operator_review_activation_packet",
    "validate_operator_review_activation_packet",
]
