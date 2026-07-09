"""ARCHIVE-CORRELATION-ROLLUP-APP-1.

D1 boundary package.

This sidecar builds a read-only correlation evidence index contract.
It must not mutate core, backfill missing evidence, auto-fill correlation_id,
auto-pass review, generate placeholder review packets, or create UI dashboard panels.
"""

from .contract import (
    ALLOWED_ROLLUP_STATUSES,
    ARCHIVE_CORRELATION_ROLLUP_APP_ID,
    CORRELATION_ROLLUP_REQUIRED_LINKS,
    build_correlation_rollup_contract,
)

__all__ = [
    "ALLOWED_ROLLUP_STATUSES",
    "ARCHIVE_CORRELATION_ROLLUP_APP_ID",
    "CORRELATION_ROLLUP_REQUIRED_LINKS",
    "build_correlation_rollup_contract",
]
