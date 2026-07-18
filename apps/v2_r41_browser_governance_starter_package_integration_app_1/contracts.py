from dataclasses import dataclass


@dataclass(frozen=True)
class BrowserGovernanceStarterPackageAcceptance:
    status: str
    artifact_count: int
    governance_state: str
    projection_count: int
    observed_field_count: int
    inferred_field_count: int
    demonstration_only: bool = True
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    factor_activated: bool = False
    action_created: bool = False

    def __post_init__(self) -> None:
        if self.status != "READY_FOR_READ_ONLY_GOVERNANCE_DEMONSTRATION":
            raise ValueError("starter governance acceptance status mismatch")
        if self.artifact_count < 1 or self.projection_count < 1:
            raise ValueError("starter governance artifacts are required")
        if self.governance_state != "AVAILABLE":
            raise ValueError("starter Governance workspace must be available")
        if self.observed_field_count < 1 or self.inferred_field_count < 1:
            raise ValueError("starter field origins must be explicit")
        if not all(
            (
                self.demonstration_only,
                self.registered_artifact_only,
                self.read_only,
                self.operator_review_required,
            )
        ):
            raise ValueError("starter governance boundary is required")
        if self.factor_activated or self.action_created:
            raise ValueError("starter package cannot activate or create actions")
