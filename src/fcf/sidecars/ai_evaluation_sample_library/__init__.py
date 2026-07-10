"""AI evaluation sample library sidecar."""

from .contract import (
    APP_ID,
    CONTRACT_VERSION,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)
from .coverage_checks import (
    COVERAGE_SCHEMA_VERSION,
    COVERAGE_STAGE_ID,
    COVERAGE_STATUSES,
    build_evaluation_sample_coverage_report,
    validate_evaluation_sample_coverage_report,
)
from .registry_index import (
    REGISTRY_SCHEMA_VERSION,
    REGISTRY_STAGE_ID,
    build_evaluation_sample_registry,
    validate_evaluation_sample_registry,
    validate_registry_source_records,
)
from .sample_schema import (
    EVALUATION_DIMENSIONS,
    EXPECTED_OUTCOMES,
    REVIEW_STATUSES,
    SAMPLE_SCHEMA_VERSION,
    SAMPLE_STAGE_ID,
    build_evaluation_sample_record,
    validate_evaluation_sample_record,
)

__all__ = [
    "APP_ID",
    "CONTRACT_VERSION",
    "STAGE_ID",
    "build_boundary_contract",
    "validate_boundary_contract",
    "COVERAGE_SCHEMA_VERSION",
    "COVERAGE_STAGE_ID",
    "COVERAGE_STATUSES",
    "build_evaluation_sample_coverage_report",
    "validate_evaluation_sample_coverage_report",
    "REGISTRY_SCHEMA_VERSION",
    "REGISTRY_STAGE_ID",
    "build_evaluation_sample_registry",
    "validate_evaluation_sample_registry",
    "validate_registry_source_records",
    "EVALUATION_DIMENSIONS",
    "EXPECTED_OUTCOMES",
    "REVIEW_STATUSES",
    "SAMPLE_SCHEMA_VERSION",
    "SAMPLE_STAGE_ID",
    "build_evaluation_sample_record",
    "validate_evaluation_sample_record",
]