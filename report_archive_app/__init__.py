"""Report archive sidecar package.

This package is paper-only, local-only, read-only, and sidecar-only.
It archives local report and handoff artifacts from completed sidecar layers.
It must not import or mutate P1-P47 core modules.
"""

from .archive_contract import (
    REPORT_ARCHIVE_APP_ID,
    REPORT_ARCHIVE_STAGE_ID,
    ReportArchiveContract,
    build_report_archive_contract,
    validate_report_archive_contract,
)

__all__ = [
    "REPORT_ARCHIVE_APP_ID",
    "REPORT_ARCHIVE_STAGE_ID",
    "ReportArchiveContract",
    "build_report_archive_contract",
    "validate_report_archive_contract",
]
