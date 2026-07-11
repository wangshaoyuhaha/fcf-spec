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
from .d3_ui_activation import (
    UI_CONSUMER_ID,
    UI_DISPLAY_STATE,
    UI_RENDER_MODE,
    UiActivationPacket,
    build_ui_activation_packet,
    validate_ui_activation_packet,
)
from .d4_report_archive_activation import (
    REPORT_ARCHIVE_CONSUMER_ID,
    REPORT_ARCHIVE_STATUS,
    ReportArchiveActivationPacket,
    build_report_archive_activation_packet,
    validate_report_archive_activation_packet,
)
from .d5_cross_surface_activation_validation import (
    CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE,
    CROSS_SURFACE_VALIDATION_STATUS,
    RegisteredCrossSurfaceActivationArtifact,
    build_registered_cross_surface_activation_artifact,
    validate_registered_cross_surface_activation_artifact,
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
    "UI_CONSUMER_ID",
    "UI_DISPLAY_STATE",
    "UI_RENDER_MODE",
    "UiActivationPacket",
    "build_ui_activation_packet",
    "validate_ui_activation_packet",
    "REPORT_ARCHIVE_CONSUMER_ID",
    "REPORT_ARCHIVE_STATUS",
    "ReportArchiveActivationPacket",
    "build_report_archive_activation_packet",
    "validate_report_archive_activation_packet",
    "CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE",
    "CROSS_SURFACE_VALIDATION_STATUS",
    "RegisteredCrossSurfaceActivationArtifact",
    "build_registered_cross_surface_activation_artifact",
    "validate_registered_cross_surface_activation_artifact",
]
