from .contracts import (
    REQUIRED_CACHE_FAMILIES,
    REQUIRED_DIRECTORY_CLASSES,
    RuntimeFootprintEvidence,
    RuntimeFootprintRegistration,
    RuntimeFootprintSnapshot,
    build_reference_evidence,
    build_runtime_footprint_evidence,
    canonical_sha256,
)


def render_evidence_json(evidence):
    from .runner import render_evidence_json as implementation

    return implementation(evidence)


def scan_runtime_footprint(*args, **kwargs):
    from .runner import scan_runtime_footprint as implementation

    return implementation(*args, **kwargs)

__all__ = [
    "REQUIRED_CACHE_FAMILIES",
    "REQUIRED_DIRECTORY_CLASSES",
    "RuntimeFootprintEvidence",
    "RuntimeFootprintRegistration",
    "RuntimeFootprintSnapshot",
    "build_reference_evidence",
    "build_runtime_footprint_evidence",
    "canonical_sha256",
    "render_evidence_json",
    "scan_runtime_footprint",
]
