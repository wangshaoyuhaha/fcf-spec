from .builder import (
    REFERENCE_OBSERVED_AT_UTC,
    build_reference_artifact_bytes,
    build_reference_runtime_snapshot,
    render_runtime_snapshot_json,
)
from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    RegisteredLabelDefinition,
    RegisteredTargetLabelArtifact,
    RegisteredTargetLabelRuntimeSnapshot,
)
from .runtime import load_registered_target_label_registry


PHASE_ID = "FCF-FCP-0097-REGISTERED-TARGET-LABEL-REGISTRY-RUNTIME-APP-1"


__all__ = [
    "PHASE_ID",
    "REFERENCE_OBSERVED_AT_UTC",
    "RUNTIME_SCHEMA_VERSION",
    "RegisteredLabelDefinition",
    "RegisteredTargetLabelArtifact",
    "RegisteredTargetLabelRuntimeSnapshot",
    "build_reference_artifact_bytes",
    "build_reference_runtime_snapshot",
    "load_registered_target_label_registry",
    "render_runtime_snapshot_json",
]
