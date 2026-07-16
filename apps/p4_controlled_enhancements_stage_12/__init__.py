"""P4 controlled enhancements Stage 12 sidecar."""

from .acceptance import P4Acceptance, P4_IMPLEMENTATION_BINDINGS, build_p4_acceptance
from .boundary import P4_CONTROLLED_ENHANCEMENTS_BOUNDARY, P4ControlledEnhancementsBoundary
from .capabilities import P4_CAPABILITY_REGISTRY
from .contracts import (
    CaseMemoryQuery,
    CaseMemoryRecord,
    CaseMemoryRetrieval,
    ChallengerProposalRequest,
    ExperimentScheduleProposal,
    ForwardShadowObservation,
    RealtimeShadowValidation,
    RegisteredTrainingResult,
    SpecialistTrainingEvaluation,
    SpecialistTrainingPlan,
)
from .presentation import build_p4_console_sections
from .services import (
    DeterministicP4ProposalService,
    LocalForwardShadowValidationService,
    RegisteredCaseMemoryService,
    SpecialistTrainingGovernanceService,
)

__all__ = [
    "CaseMemoryQuery",
    "CaseMemoryRecord",
    "CaseMemoryRetrieval",
    "ChallengerProposalRequest",
    "DeterministicP4ProposalService",
    "ExperimentScheduleProposal",
    "ForwardShadowObservation",
    "LocalForwardShadowValidationService",
    "P4Acceptance",
    "P4_IMPLEMENTATION_BINDINGS",
    "P4ControlledEnhancementsBoundary",
    "P4_CAPABILITY_REGISTRY",
    "P4_CONTROLLED_ENHANCEMENTS_BOUNDARY",
    "RealtimeShadowValidation",
    "RegisteredCaseMemoryService",
    "RegisteredTrainingResult",
    "SpecialistTrainingEvaluation",
    "SpecialistTrainingGovernanceService",
    "SpecialistTrainingPlan",
    "build_p4_acceptance",
    "build_p4_console_sections",
]
