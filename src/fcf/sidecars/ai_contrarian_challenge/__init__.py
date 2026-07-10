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
from .handoff import (
    HANDOFF_STATUSES,
    HANDOFF_VERSION,
    build_challenge_operator_handoff,
)
from .report import (
    REPORT_STATUSES,
    REPORT_VERSION,
    REVIEW_CATEGORIES,
    build_contradiction_evidence_gap_report,
)
from .review import (
    PROHIBITED_REVIEW_ACTIONS,
    REVIEW_PACKET_VERSION,
    REVIEW_PRIORITIES,
    build_challenge_review_packet,
)
from .rules import (
    REASON_CODES,
    RULE_ENGINE_VERSION,
    RULE_IDS,
    apply_challenge_rules,
)
from .schema import (
    CHALLENGE_SEVERITIES,
    OPERATOR_REVIEW_STATUSES,
    REQUIRED_EVIDENCE_FIELDS,
    SCHEMA_VERSION,
    SOURCE_ARTIFACT_TYPES,
    build_challenge_evidence_record,
    validate_challenge_evidence_record,
)

__all__ = [
    "ALLOWED_INPUTS",
    "ALLOWED_OUTPUTS",
    "APP_ID",
    "CHALLENGE_CATEGORIES",
    "CHALLENGE_SEVERITIES",
    "CHALLENGE_STATUSES",
    "CONTRACT_VERSION",
    "FORBIDDEN_OUTCOMES",
    "HANDOFF_STATUSES",
    "HANDOFF_VERSION",
    "OPERATOR_REVIEW_STATUSES",
    "PROHIBITED_REVIEW_ACTIONS",
    "REASON_CODES",
    "REPORT_STATUSES",
    "REPORT_VERSION",
    "REQUIRED_EVIDENCE_FIELDS",
    "REVIEW_CATEGORIES",
    "REVIEW_PACKET_VERSION",
    "REVIEW_PRIORITIES",
    "RULE_ENGINE_VERSION",
    "RULE_IDS",
    "SCHEMA_VERSION",
    "SOURCE_ARTIFACT_TYPES",
    "STAGE_ID",
    "apply_challenge_rules",
    "build_boundary_contract",
    "build_challenge_evidence_record",
    "build_challenge_operator_handoff",
    "build_challenge_review_packet",
    "build_contradiction_evidence_gap_report",
    "validate_boundary_contract",
    "validate_challenge_evidence_record",
]