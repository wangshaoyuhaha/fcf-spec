"""Paper review contract for OPERATOR-REVIEW-D1.

The contract defines the safety boundary for a local human review record layer.
It is intentionally non-executable and cannot represent a trading instruction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


OPERATOR_REVIEW_APP_ID = "OPERATOR-REVIEW-APP-1"
OPERATOR_REVIEW_STAGE_ID = "OPERATOR-REVIEW-D1"

_ALLOWED_SOURCE_TYPES = (
    "ui_app_local_report_artifact",
    "ui_app_workflow_handoff",
)

_FORBIDDEN_TRUE_FLAGS = (
    "real_execution_allowed",
    "trade_action_enabled",
    "buy_button_enabled",
    "sell_button_enabled",
    "order_button_enabled",
    "broker_connection_allowed",
    "exchange_connection_allowed",
    "credential_storage_allowed",
    "wallet_private_key_access_allowed",
    "real_account_access_allowed",
    "real_position_access_allowed",
    "core_mutation_allowed",
    "p48_core_expansion_allowed",
    "operator_review_bypass_allowed",
)


@dataclass(frozen=True)
class PaperReviewContract:
    """Static safety contract for the operator review sidecar."""

    app_id: str = OPERATOR_REVIEW_APP_ID
    stage_id: str = OPERATOR_REVIEW_STAGE_ID
    contract_version: str = "1.0.0"

    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True

    source_types: tuple[str, ...] = _ALLOWED_SOURCE_TYPES
    output_record_types: tuple[str, ...] = (
        "paper_review_record",
        "reviewer_note_record",
        "risk_acknowledgement_record",
        "no_execution_receipt",
        "operator_review_handoff_packet",
    )

    review_status_is_trade_action: bool = False
    paper_decision_label_is_trade_action: bool = False
    operator_review_required: bool = True
    operator_review_bypass_allowed: bool = False

    real_execution_allowed: bool = False
    trade_action_enabled: bool = False
    buy_button_enabled: bool = False
    sell_button_enabled: bool = False
    order_button_enabled: bool = False
    broker_connection_allowed: bool = False
    exchange_connection_allowed: bool = False
    credential_storage_allowed: bool = False
    wallet_private_key_access_allowed: bool = False
    real_account_access_allowed: bool = False
    real_position_access_allowed: bool = False
    core_mutation_allowed: bool = False
    p48_core_expansion_allowed: bool = False

    notes: tuple[str, ...] = field(
        default_factory=lambda: (
            "Read UI-APP-1 local read-only report artifacts only.",
            "Create paper-only local review records only.",
            "Never convert review fields into trade instructions.",
            "Never mutate P1-P47 core modules.",
        )
    )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe contract dictionary."""
        data = asdict(self)
        data["source_types"] = list(self.source_types)
        data["output_record_types"] = list(self.output_record_types)
        data["notes"] = list(self.notes)
        return data


def build_paper_review_contract() -> PaperReviewContract:
    """Build the static OPERATOR-REVIEW-D1 contract."""
    return PaperReviewContract()


def validate_paper_review_contract(contract: PaperReviewContract) -> list[str]:
    """Validate the D1 safety contract and return human-readable errors."""
    errors: list[str] = []

    if contract.app_id != OPERATOR_REVIEW_APP_ID:
        errors.append("app_id mismatch")
    if contract.stage_id != OPERATOR_REVIEW_STAGE_ID:
        errors.append("stage_id mismatch")

    required_true_flags = (
        "paper_only",
        "local_only",
        "read_only",
        "sidecar_only",
        "operator_review_required",
    )
    for flag_name in required_true_flags:
        if getattr(contract, flag_name) is not True:
            errors.append(f"{flag_name} must be true")

    for flag_name in _FORBIDDEN_TRUE_FLAGS:
        if getattr(contract, flag_name) is not False:
            errors.append(f"{flag_name} must be false")

    if contract.review_status_is_trade_action is not False:
        errors.append("review_status_is_trade_action must be false")
    if contract.paper_decision_label_is_trade_action is not False:
        errors.append("paper_decision_label_is_trade_action must be false")

    if tuple(contract.source_types) != _ALLOWED_SOURCE_TYPES:
        errors.append("source_types must remain limited to UI-APP-1 read-only sources")

    return errors
