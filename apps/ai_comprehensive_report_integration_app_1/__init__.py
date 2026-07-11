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
from .d3_operator_review_adapter import (
    CONSUMER_APP_ID,
    PACKET_TYPE,
    build_operator_review_packet,
    validate_operator_review_packet,
)
from .d4_ui_visibility_projection import (
    UI_CONSUMER_APP_ID,
    UI_PACKET_TYPE,
    build_ui_visibility_packet,
    validate_ui_visibility_packet,
)
from .d5_manual_archive_projection import (
    ARCHIVE_CONSUMER_APP_ID,
    ARCHIVE_PACKET_TYPE,
    build_manual_archive_candidate_packet,
    validate_manual_archive_candidate_packet,
)
from .d6_full_chain_closeout import (
    CLOSEOUT_PACKET_TYPE,
    build_full_chain_closeout_packet,
    validate_full_chain_closeout_packet,
)

__all__ = [
    "APP_ID",
    "CONTRACT_VERSION",
    "SOURCE_APP_ID",
    "SOURCE_ARTIFACT_TYPE",
    "SOURCE_MODULE",
    "CONSUMER_APP_ID",
    "PACKET_TYPE",
    "UI_CONSUMER_APP_ID",
    "UI_PACKET_TYPE",
    "ARCHIVE_CONSUMER_APP_ID",
    "ARCHIVE_PACKET_TYPE",
    "CLOSEOUT_PACKET_TYPE",
    "build_integration_boundary_contract",
    "validate_integration_boundary_contract",
    "build_registered_source_envelope",
    "canonical_payload_sha256",
    "load_registered_source_from_file",
    "load_registered_source_from_mapping",
    "validate_registered_source_envelope",
    "build_operator_review_packet",
    "validate_operator_review_packet",
    "build_ui_visibility_packet",
    "validate_ui_visibility_packet",
    "build_manual_archive_candidate_packet",
    "validate_manual_archive_candidate_packet",
    "build_full_chain_closeout_packet",
    "validate_full_chain_closeout_packet",
]
