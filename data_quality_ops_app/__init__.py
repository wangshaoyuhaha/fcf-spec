"""Data quality operations sidecar package.

This package is paper-only, local-only, read-only, and sidecar-only.
It inspects local data quality signals and produces paper-only operations records.
It must not import or mutate P1-P47 core modules.
"""

from .ops_contract import (
    DATA_QUALITY_OPS_APP_ID,
    DATA_QUALITY_OPS_STAGE_ID,
    DataQualityOpsContract,
    build_data_quality_ops_contract,
    validate_data_quality_ops_contract,
)

__all__ = [
    "DATA_QUALITY_OPS_APP_ID",
    "DATA_QUALITY_OPS_STAGE_ID",
    "DataQualityOpsContract",
    "build_data_quality_ops_contract",
    "validate_data_quality_ops_contract",
]
