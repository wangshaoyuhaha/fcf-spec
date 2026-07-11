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
from .d2_operator_review_binding import (
    BINDING_PACKET_TYPE,
    CONSUMER_APP_ID,
    build_operator_review_consumer_binding,
    validate_operator_review_consumer_binding,
)
from .d3_ui_binding import (
    REQUIRED_VISIBLE_SECTION_IDS,
    UI_BINDING_PACKET_TYPE,
    UI_CONSUMER_APP_ID,
    build_ui_consumer_binding,
    validate_ui_consumer_binding,
)
from .d4_report_archive_binding import (
    ARCHIVE_BINDING_PACKET_TYPE,
    ARCHIVE_CONSUMER_APP_ID,
    REQUIRED_ARCHIVE_FIELDS,
    build_report_archive_consumer_binding,
    validate_report_archive_consumer_binding,
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
    "BINDING_PACKET_TYPE",
    "CONSUMER_APP_ID",
    "REQUIRED_VISIBLE_SECTION_IDS",
    "UI_BINDING_PACKET_TYPE",
    "UI_CONSUMER_APP_ID",
    "ARCHIVE_BINDING_PACKET_TYPE",
    "ARCHIVE_CONSUMER_APP_ID",
    "REQUIRED_ARCHIVE_FIELDS",
    "build_consumer_binding_contract",
    "validate_consumer_binding_contract",
    "build_operator_review_consumer_binding",
    "validate_operator_review_consumer_binding",
    "build_ui_consumer_binding",
    "validate_ui_consumer_binding",
    "build_report_archive_consumer_binding",
    "validate_report_archive_consumer_binding",
]
