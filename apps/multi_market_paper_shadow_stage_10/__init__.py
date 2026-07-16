"""Stage 10 multi-market Paper and Shadow validation sidecar."""

from .acceptance import Stage10Acceptance, build_stage10_acceptance
from .boundary import (
    MULTI_MARKET_PAPER_SHADOW_BOUNDARY,
    MultiMarketPaperShadowBoundary,
)
from .contracts import (
    MarketValidationFinding,
    MultiMarketValidationOutcome,
    MultiMarketValidationRequest,
    PaperMarketValidation,
    ShadowMarketObservation,
    ShadowMaturity,
    ValidationStatus,
)
from .service import (
    MultiMarketPaperShadowValidationService,
    build_console_sections,
)

__all__ = [
    "MULTI_MARKET_PAPER_SHADOW_BOUNDARY",
    "MarketValidationFinding",
    "MultiMarketPaperShadowBoundary",
    "MultiMarketPaperShadowValidationService",
    "MultiMarketValidationOutcome",
    "MultiMarketValidationRequest",
    "PaperMarketValidation",
    "ShadowMarketObservation",
    "ShadowMaturity",
    "Stage10Acceptance",
    "ValidationStatus",
    "build_console_sections",
    "build_stage10_acceptance",
]
