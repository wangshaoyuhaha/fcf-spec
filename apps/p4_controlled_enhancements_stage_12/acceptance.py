from dataclasses import dataclass

from .boundary import P4_CONTROLLED_ENHANCEMENTS_BOUNDARY
from .capabilities import P4_CAPABILITY_REGISTRY
from .services import DeterministicP4ProposalService, LocalForwardShadowValidationService, RegisteredCaseMemoryService, SpecialistTrainingGovernanceService


P4_IMPLEMENTATION_BINDINGS = {
    "CASE-MEMORY-RETRIEVAL-APP-1": RegisteredCaseMemoryService.retrieve,
    "AUTOMATIC-CHALLENGER-PROPOSAL-APP-1": DeterministicP4ProposalService.propose_challenger,
    "REALTIME-SHADOW-VALIDATION-APP-1": LocalForwardShadowValidationService.evaluate,
    "AUTOMATIC-EXPERIMENT-SCHEDULER-APP-1": DeterministicP4ProposalService.propose_schedule,
    "SPECIALIST-MODEL-TRAINING-APP-1": SpecialistTrainingGovernanceService.evaluate_registered_result,
}


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
    capabilities = set(P4_CAPABILITY_REGISTRY["P4"])
    if set(P4_IMPLEMENTATION_BINDINGS) != capabilities:
        raise ValueError("P4 implementation bindings are incomplete")
    if any(not callable(value) for value in P4_IMPLEMENTATION_BINDINGS.values()):
        raise ValueError("P4 implementation binding is not callable")
    return P4Acceptance(
        status="D1_D6_ACCEPTED",
        capability_count=sum(len(values) for values in P4_CAPABILITY_REGISTRY.values()),
        next_phase="LOCAL_AI_RUNTIME_CONFIGURATION_GOVERNANCE",
    )
