"""AI evaluation result registry sidecar."""

from .contract import (
    APP_ID,
    CONTRACT_VERSION,
    IMPORTED_RESULT_STATUSES,
    STAGE_ID,
    build_boundary_contract,
    validate_boundary_contract,
)
from .linkage_checks import (
    LINKAGE_SCHEMA_VERSION,
    LINKAGE_STAGE_ID,
    LINKAGE_STATUSES,
    build_sample_result_linkage_report,
    validate_sample_result_linkage_report,
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
    "LINKAGE_SCHEMA_VERSION",
    "LINKAGE_STAGE_ID",
    "LINKAGE_STATUSES",
    "build_sample_result_linkage_report",
    "validate_sample_result_linkage_report",
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