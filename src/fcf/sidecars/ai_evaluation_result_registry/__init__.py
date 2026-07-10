"""AI evaluation result registry sidecar."""

from .contract import (
    APP_ID,
    CONTRACT_VERSION,
    IMPORTED_RESULT_STATUSES,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)
from .registry_index import (
    REGISTRY_SCHEMA_VERSION,
    REGISTRY_STAGE_ID,
    build_evaluation_result_registry,
    validate_evaluation_result_registry,
    validate_registry_source_records,
)
from .result_schema import (
    OBSERVED_OUTCOMES,
    RESULT_SCHEMA_VERSION,
    RESULT_STAGE_ID,
    build_evaluation_result_record,
    validate_evaluation_result_record,
)

__all__ = [
    "APP_ID",
    "CONTRACT_VERSION",
    "IMPORTED_RESULT_STATUSES",
    "STAGE_ID",
    "build_boundary_contract",
    "validate_boundary_contract",
    "REGISTRY_SCHEMA_VERSION",
    "REGISTRY_STAGE_ID",
    "build_evaluation_result_registry",
    "validate_evaluation_result_registry",
    "validate_registry_source_records",
    "OBSERVED_OUTCOMES",
    "RESULT_SCHEMA_VERSION",
    "RESULT_STAGE_ID",
    "build_evaluation_result_record",
    "validate_evaluation_result_record",
]