"""Read-only registered-artifact gateway runtime."""

from .boundary import (
    READ_ONLY_DATA_GATEWAY_BOUNDARY,
    ReadOnlyDataGatewayBoundary,
)
from .artifact_reader import (
    DEFAULT_MAX_ARTIFACT_BYTES,
    LocalRegisteredArtifactReader,
    RegisteredArtifactReadError,
    VerifiedArtifactRead,
    resolve_registered_artifact_path,
)
from .contracts import (
    ArtifactFormat,
    GatewayReadReceipt,
    GatewayReadRequest,
    GatewayReadStatus,
    RegisteredArtifactSource,
    normalize_registered_relative_path,
)
from .registry import RegisteredArtifactRegistry

__all__ = [
    "ArtifactFormat",
    "DEFAULT_MAX_ARTIFACT_BYTES",
    "GatewayReadReceipt",
    "GatewayReadRequest",
    "GatewayReadStatus",
    "READ_ONLY_DATA_GATEWAY_BOUNDARY",
    "LocalRegisteredArtifactReader",
    "RegisteredArtifactReadError",
    "ReadOnlyDataGatewayBoundary",
    "RegisteredArtifactRegistry",
    "RegisteredArtifactSource",
    "VerifiedArtifactRead",
    "normalize_registered_relative_path",
    "resolve_registered_artifact_path",
]
