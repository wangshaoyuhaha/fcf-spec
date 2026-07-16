from dataclasses import dataclass

from .boundary import CONTROLLED_LEARNING_BACKTESTING_BOUNDARY
from .capabilities import P0_P3_CAPABILITY_REGISTRY


@dataclass(frozen=True)
class P0P3Acceptance:
    status: str
    capability_count: int
    phase_counts: tuple[tuple[str, int], ...]
    next_phase: str

    def __post_init__(self) -> None:
        if self.status != "D1_D6_ACCEPTED" or self.capability_count != 22:
            raise ValueError("P0-P3 capability acceptance is incomplete")
        if self.next_phase != "P4_GOVERNANCE_DECISION":
            raise ValueError("P0-P3 next phase mismatch")


def build_p0_p3_acceptance() -> P0P3Acceptance:
    CONTROLLED_LEARNING_BACKTESTING_BOUNDARY.__post_init__()
    return P0P3Acceptance(
        status="D1_D6_ACCEPTED",
        capability_count=sum(
            len(values) for values in P0_P3_CAPABILITY_REGISTRY.values()
        ),
        phase_counts=tuple(
            (phase, len(values))
            for phase, values in P0_P3_CAPABILITY_REGISTRY.items()
        ),
        next_phase="P4_GOVERNANCE_DECISION",
    )
