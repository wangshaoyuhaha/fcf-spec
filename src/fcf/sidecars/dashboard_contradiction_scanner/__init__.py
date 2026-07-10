"""Dashboard contradiction scanner sidecar."""

from .contract import build_contract, validate_contract
from .finding_schema import (
    CONTRADICTION_SEVERITIES,
    FINDING_STATUSES,
    build_contradiction_finding,
    validate_contradiction_finding,
)
from .source_loader import (
    build_source_manifest,
    load_source_record,
)

__all__ = [
    "build_contract",
    "validate_contract",
    "build_source_manifest",
    "load_source_record",
    "CONTRADICTION_SEVERITIES",
    "FINDING_STATUSES",
    "build_contradiction_finding",
    "validate_contradiction_finding",
]
