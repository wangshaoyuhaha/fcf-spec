"""Dashboard contradiction scanner sidecar."""

from .contract import build_contract, validate_contract
from .source_loader import (
    build_source_manifest,
    load_source_record,
)

__all__ = [
    "build_contract",
    "validate_contract",
    "build_source_manifest",
    "load_source_record",
]
