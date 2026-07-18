from dataclasses import dataclass


@dataclass(frozen=True)
class V2R41BrowserGovernanceStarterPackageBoundary:
    demonstration_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    network_fetch_allowed: bool = False
    write_controls_allowed: bool = False
    factor_activation_allowed: bool = False
    order_or_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if not all(
            (
                self.demonstration_only,
                self.local_only,
                self.loopback_only,
                self.registered_artifact_only,
                self.read_only,
                self.operator_review_required,
            )
        ):
            raise ValueError("R41 starter boundary must remain closed")
        if any(
            (
                self.network_fetch_allowed,
                self.write_controls_allowed,
                self.factor_activation_allowed,
                self.order_or_execution_allowed,
            )
        ):
            raise ValueError("R41 prohibited capability cannot be enabled")


V2_R41_BROWSER_GOVERNANCE_STARTER_PACKAGE_BOUNDARY = (
    V2R41BrowserGovernanceStarterPackageBoundary()
)
