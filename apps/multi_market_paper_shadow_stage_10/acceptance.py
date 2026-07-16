from dataclasses import dataclass

from apps.multi_market_adapters_stage_6 import MarketAdapterId

from .boundary import MULTI_MARKET_PAPER_SHADOW_BOUNDARY


@dataclass(frozen=True)
class Stage10Acceptance:
    status: str
    market_ids: tuple[str, ...]
    next_phase: str

    def __post_init__(self) -> None:
        if self.status != "D1_D6_ACCEPTED":
            raise ValueError("Stage 10 acceptance is incomplete")
        if len(self.market_ids) != 6:
            raise ValueError("Stage 10 requires six markets")
        if self.next_phase != "CONTROLLED_LEARNING_BACKTESTING_P0_P3":
            raise ValueError("Stage 10 next phase mismatch")


def build_stage10_acceptance() -> Stage10Acceptance:
    MULTI_MARKET_PAPER_SHADOW_BOUNDARY.__post_init__()
    return Stage10Acceptance(
        status="D1_D6_ACCEPTED",
        market_ids=tuple(sorted(item.value for item in MarketAdapterId)),
        next_phase="CONTROLLED_LEARNING_BACKTESTING_P0_P3",
    )
