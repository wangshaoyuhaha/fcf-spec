"""AI evaluation comparison sidecar."""

from .contract import (
    ALLOWED_INPUTS,
    ALLOWED_OUTPUTS,
    APP_ID,
    COMPARISON_MODES,
    COMPARISON_STATUSES,
    CONTRACT_VERSION,
    FORBIDDEN_COMPARISON_STATUSES,
    REQUIRED_COMPARISON_DIMENSIONS,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)
from .engine import (
    ENGINE_VERSION,
    FIELD_STATUSES,
    VALID_COMPARISON_STATUSES,
    compare_expected_observed,
)
from .schema import (
    OPERATOR_REVIEW_STATUSES,
    REQUIRED_RECORD_FIELDS,
    RESULT_STATUSES,
    SCHEMA_VERSION,
    build_comparison_record,
    validate_comparison_record,
)

__all__ = [
    "ALLOWED_INPUTS",
    "ALLOWED_OUTPUTS",
    "APP_ID",
    "COMPARISON_MODES",
    "COMPARISON_STATUSES",
    "CONTRACT_VERSION",
    "ENGINE_VERSION",
    "FIELD_STATUSES",
    "FORBIDDEN_COMPARISON_STATUSES",
    "OPERATOR_REVIEW_STATUSES",
    "REQUIRED_COMPARISON_DIMENSIONS",
    "REQUIRED_RECORD_FIELDS",
    "RESULT_STATUSES",
    "SCHEMA_VERSION",
    "STAGE_ID",
    "VALID_COMPARISON_STATUSES",
    "build_boundary_contract",
    "build_comparison_record",
    "compare_expected_observed",
    "validate_boundary_contract",
    "validate_comparison_record",
]