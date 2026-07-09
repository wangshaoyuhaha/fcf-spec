"""Sidecar-only UI risk flag visibility guard."""

from .review_packet import build_operator_review_visibility_packet
from .visibility_validator import validate_visibility_preservation

__all__ = [
    'build_operator_review_visibility_packet',
    'validate_visibility_preservation',
]
