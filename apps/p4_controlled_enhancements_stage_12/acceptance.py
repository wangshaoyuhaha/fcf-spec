from dataclasses import dataclass

from .boundary import P4_CONTROLLED_ENHANCEMENTS_BOUNDARY
from .capabilities import P4_CAPABILITY_REGISTRY


@dataclass(frozen=True)
class P4Acceptance:
    status: str
    capability_count: int
    next_phase: str

    def __post_init__(self) -> None:
        if self.status != "D1_D6_ACCEPTED" or self.capability_count != 5:
            raise ValueError("P4 capability acceptance is incomplete")
        if self.next_phase != "LOCAL_AI_RUNTIME_CONFIGURATION_GOVERNANCE":
            raise ValueError("P4 next phase mismatch")


def build_p4_acceptance() -> P4Acceptance:
    P4_CONTROLLED_ENHANCEMENTS_BOUNDARY.__post_init__()
    return P4Acceptance(
        status="D1_D6_ACCEPTED",
        capability_count=sum(len(values) for values in P4_CAPABILITY_REGISTRY.values()),
        next_phase="LOCAL_AI_RUNTIME_CONFIGURATION_GOVERNANCE",
    )
