from apps.browser_product_console_runtime_app_1.artifact_index import (
    LoadedConsoleArtifactIndex,
)
from apps.browser_product_console_runtime_app_1.operator_launch import (
    STARTER_DATA_CLASSIFICATION,
)
from apps.browser_product_console_runtime_app_1.read_model import (
    build_console_read_model,
)
from apps.browser_product_console_runtime_app_1.research_workspace_views import (
    build_governance_workspace_model,
)

from .contracts import BrowserGovernanceStarterPackageAcceptance


def build_starter_governance_acceptance(
    loaded: LoadedConsoleArtifactIndex,
) -> BrowserGovernanceStarterPackageAcceptance:
    if not isinstance(loaded, LoadedConsoleArtifactIndex):
        raise ValueError("loaded registered starter package is required")
    if any(
        artifact.payload.get("data_classification")
        != STARTER_DATA_CLASSIFICATION
        for artifact in loaded.artifacts
    ):
        raise ValueError("starter governance artifacts must be demonstrative")
    workspace = build_governance_workspace_model(build_console_read_model(loaded))
    presentations = workspace.projection_presentations
    return BrowserGovernanceStarterPackageAcceptance(
        status="READY_FOR_READ_ONLY_GOVERNANCE_DEMONSTRATION",
        artifact_count=len(loaded.artifacts),
        governance_state=workspace.state,
        projection_count=len(presentations),
        observed_field_count=sum(
            field.origin == "OBSERVED"
            for presentation in presentations
            for field in presentation.fields
        ),
        inferred_field_count=sum(
            field.origin == "INFERRED"
            for presentation in presentations
            for field in presentation.fields
        ),
    )
