from dataclasses import dataclass

from .contracts import RegisteredBrowserGovernanceProjection


@dataclass(frozen=True)
class V2R39IntegrationAcceptance:
    projection_hash: str
    status: str = "PASSED_READ_ONLY_INTEGRATION"
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    write_controls: bool = False
    factor_activated: bool = False
    action_created: bool = False


def build_integration_acceptance(
    artifact: RegisteredBrowserGovernanceProjection,
) -> V2R39IntegrationAcceptance:
    return V2R39IntegrationAcceptance(artifact.projection.projection_hash)
