"""Read-only registered-artifact gateway runtime."""

from .boundary import (
    READ_ONLY_DATA_GATEWAY_BOUNDARY,
    ReadOnlyDataGatewayBoundary,
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
    "GatewayReadReceipt",
    "GatewayReadRequest",
    "GatewayReadStatus",
    "READ_ONLY_DATA_GATEWAY_BOUNDARY",
    "ReadOnlyDataGatewayBoundary",
    "RegisteredArtifactRegistry",
    "RegisteredArtifactSource",
    "normalize_registered_relative_path",
]
