"""AI evaluation drift review sidecar."""

from .classifier import (
    CLASSIFIER_VERSION,
    COMPARABLE_STATUSES,
    DRIFT_REASON_CODES,
    DRIFT_SEVERITIES,
    classify_drift_evidence,
)
from .contract import (
    ALLOWED_INPUTS,
    ALLOWED_OUTPUTS,
    APP_ID,
    CONTRACT_VERSION,
    DRIFT_STATUSES,
    FORBIDDEN_DRIFT_STATUSES,
    REQUIRED_DRIFT_DIMENSIONS,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)
from .schema import (
    OPERATOR_REVIEW_STATUSES,
    REQUIRED_EVIDENCE_FIELDS,
    SCHEMA_VERSION,
    SOURCE_COMPARISON_STATUSES,
    build_drift_evidence_record,
    validate_drift_evidence_record,
)
from .window import (
    REVIEW_DRIFT_STATUSES,
    WINDOW_STATUSES,
    WINDOW_VERSION,
    build_drift_comparison_window,
)

__all__ = [
    "ALLOWED_INPUTS",
    "ALLOWED_OUTPUTS",
    "APP_ID",
    "CLASSIFIER_VERSION",
    "COMPARABLE_STATUSES",
    "CONTRACT_VERSION",
    "DRIFT_REASON_CODES",
    "DRIFT_SEVERITIES",
    "DRIFT_STATUSES",
    "FORBIDDEN_DRIFT_STATUSES",
    "OPERATOR_REVIEW_STATUSES",
    "REQUIRED_DRIFT_DIMENSIONS",
    "REQUIRED_EVIDENCE_FIELDS",
    "REVIEW_DRIFT_STATUSES",
    "SCHEMA_VERSION",
    "SOURCE_COMPARISON_STATUSES",
    "STAGE_ID",
    "WINDOW_STATUSES",
    "WINDOW_VERSION",
    "build_boundary_contract",
    "build_drift_comparison_window",
    "build_drift_evidence_record",
    "classify_drift_evidence",
    "validate_boundary_contract",
    "validate_drift_evidence_record",
]