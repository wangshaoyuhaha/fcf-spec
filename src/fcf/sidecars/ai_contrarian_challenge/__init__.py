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
    "OPERATOR_REVIEW_STATUSES",
    "REASON_CODES",
    "REQUIRED_EVIDENCE_FIELDS",
    "RULE_ENGINE_VERSION",
    "RULE_IDS",
    "SCHEMA_VERSION",
    "SOURCE_ARTIFACT_TYPES",
    "STAGE_ID",
    "apply_challenge_rules",
    "build_boundary_contract",
    "build_challenge_evidence_record",
    "validate_boundary_contract",
    "validate_challenge_evidence_record",
]