"""Operator review sidecar package.

This package is paper-only, local-only, read-only, and sidecar-only.
It must not import or mutate P1-P47 core modules.
"""

from .paper_review_contract import (
    OPERATOR_REVIEW_APP_ID,
    OPERATOR_REVIEW_STAGE_ID,
    PaperReviewContract,
    build_paper_review_contract,
    validate_paper_review_contract,
)

__all__ = [
    "OPERATOR_REVIEW_APP_ID",
    "OPERATOR_REVIEW_STAGE_ID",
    "PaperReviewContract",
    "build_paper_review_contract",
    "validate_paper_review_contract",
]
