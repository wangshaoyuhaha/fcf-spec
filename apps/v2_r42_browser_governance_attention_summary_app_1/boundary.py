from dataclasses import dataclass


@dataclass(frozen=True)
class V2R42BrowserGovernanceAttentionSummaryBoundary:
    local_only: bool = True
    loopback_only: bool = True
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    network_fetch_allowed: bool = False
    write_controls_allowed: bool = False
    approval_allowed: bool = False
    factor_activation_allowed: bool = False
    order_or_execution_allowed: bool = False

    def __post_init__(self) -> None:
        if not all(
            (
                self.local_only,
                self.loopback_only,
                self.registered_artifact_only,
                self.read_only,
                self.operator_review_required,
            )
        ):
            raise ValueError("R42 attention boundary must remain closed")
        if any(
            (
                self.network_fetch_allowed,
                self.write_controls_allowed,
                self.approval_allowed,
                self.factor_activation_allowed,
                self.order_or_execution_allowed,
            )
        ):
            raise ValueError("R42 prohibited capability cannot be enabled")


V2_R42_BROWSER_GOVERNANCE_ATTENTION_SUMMARY_BOUNDARY = (
    V2R42BrowserGovernanceAttentionSummaryBoundary()
)
