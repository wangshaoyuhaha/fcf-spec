"""ARCHIVE-CORRELATION-ROLLUP-APP-1.

Read-only correlation evidence index sidecar.
"""

from .chain_coverage import (
    build_chain_coverage_matrix,
    summarize_chain_coverage,
)
from .contract import (
    ALLOWED_ROLLUP_STATUSES,
    ARCHIVE_CORRELATION_ROLLUP_APP_ID,
    CORRELATION_ROLLUP_REQUIRED_LINKS,
    build_correlation_rollup_contract,
)
from .rollup_packet import (
    build_rollup_packet,
    classify_rollup_packet,
)
from .source_references import (
    ARTIFACT_REFERENCE_STATUS,
    build_artifact_reference,
    build_reference_index,
    validate_artifact_reference,
)
from .trace_summary import (
    build_trace_summary,
    classify_trace_summary,
)

__all__ = [
    "ALLOWED_ROLLUP_STATUSES",
    "ARCHIVE_CORRELATION_ROLLUP_APP_ID",
    "ARTIFACT_REFERENCE_STATUS",
    "CORRELATION_ROLLUP_REQUIRED_LINKS",
    "build_artifact_reference",
    "build_chain_coverage_matrix",
    "build_correlation_rollup_contract",
    "build_reference_index",
    "build_rollup_packet",
    "build_trace_summary",
    "classify_rollup_packet",
    "classify_trace_summary",
    "summarize_chain_coverage",
    "validate_artifact_reference",
]
