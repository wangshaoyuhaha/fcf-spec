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
from .normalization import (
    DEFAULT_MAX_NORMALIZED_RECORDS,
    ArtifactNormalizationError,
    NormalizedArtifactEnvelope,
    normalize_verified_artifact,
)
from .service import (
    GatewayQueryOutcome,
    ReadOnlyDataGatewayService,
    SourcePolicyDecision,
    SourcePolicyStatus,
    evaluate_source_policy,
)

__all__ = [
    "ArtifactFormat",
    "ArtifactNormalizationError",
    "DEFAULT_MAX_ARTIFACT_BYTES",
    "DEFAULT_MAX_NORMALIZED_RECORDS",
    "GatewayReadReceipt",
    "GatewayReadRequest",
    "GatewayReadStatus",
    "GatewayQueryOutcome",
    "READ_ONLY_DATA_GATEWAY_BOUNDARY",
    "LocalRegisteredArtifactReader",
    "NormalizedArtifactEnvelope",
    "RegisteredArtifactReadError",
    "ReadOnlyDataGatewayBoundary",
    "ReadOnlyDataGatewayService",
    "RegisteredArtifactRegistry",
    "RegisteredArtifactSource",
    "SourcePolicyDecision",
    "SourcePolicyStatus",
    "VerifiedArtifactRead",
    "normalize_registered_relative_path",
    "normalize_verified_artifact",
    "evaluate_source_policy",
    "resolve_registered_artifact_path",
]
