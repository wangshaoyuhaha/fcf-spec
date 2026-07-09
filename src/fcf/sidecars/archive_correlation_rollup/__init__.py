"""ARCHIVE-CORRELATION-ROLLUP-APP-1.

Read-only correlation evidence index sidecar.
"""

from .contract import (
    ALLOWED_ROLLUP_STATUSES,
    ARCHIVE_CORRELATION_ROLLUP_APP_ID,
    CORRELATION_ROLLUP_REQUIRED_LINKS,
    build_correlation_rollup_contract,
)
from .source_references import (
    ARTIFACT_REFERENCE_STATUS,
    build_artifact_reference,
    build_reference_index,
    validate_artifact_reference,
)

__all__ = [
    "ALLOWED_ROLLUP_STATUSES",
    "ARCHIVE_CORRELATION_ROLLUP_APP_ID",
    "ARTIFACT_REFERENCE_STATUS",
    "CORRELATION_ROLLUP_REQUIRED_LINKS",
    "build_artifact_reference",
    "build_correlation_rollup_contract",
    "build_reference_index",
    "validate_artifact_reference",
]
