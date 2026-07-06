"""D3 model rule registry and scoring policy snapshot for MODEL-GOVERNANCE-APP-1.

This module records paper-only governance metadata about model rules, score
components, reason codes, and risk flags. It does not mutate rules, scores,
reason codes, risk flags, source artifacts, or core modules.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Mapping, Optional


RULE_STATUS_VALUES: List[str] = [
    "ACTIVE",
    "OBSERVED_ONLY",
    "DEPRECATED",
    "REVIEW_REQUIRED",
    "BLOCKED",
]

RULE_CATEGORY_VALUES: List[str] = [
    "DATA_QUALITY",
    "SCORING",
    "REASON_CODE",
    "RISK_FLAG",
    "SIGNAL_VALIDATION",
    "OPERATOR_REVIEW",
    "SCENARIO",
    "BACKTEST_REVIEW",
]

POLICY_STATUS_VALUES: List[str] = [
    "SNAPSHOT_READY",
    "SNAPSHOT_PARTIAL",
    "SNAPSHOT_REVIEW_REQUIRED",
    "SNAPSHOT_BLOCKED",
]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class ModelRuleRecord:
    """One paper-only model governance rule record."""

    rule_id: str
    rule_name: str
    rule_category: str
    source_layer: str
    rule_status: str = "REVIEW_REQUIRED"
    description: str = ""
    governed_fields: List[str] = field(default_factory=list)
    reason_codes: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    operator_review_required: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable rule record with closed boundaries."""

        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "rule_category": self.rule_category,
            "source_layer": self.source_layer,
            "rule_status": self.rule_status,
            "description": self.description,
            "governed_fields": list(self.governed_fields),
            "reason_codes": list(self.reason_codes),
            "risk_flags": list(self.risk_flags),
            "limitations": list(self.limitations),
            "operator_review_required": self.operator_review_required,
            "score_mutation_allowed": False,
            "reason_code_mutation_allowed": False,
            "risk_flag_deletion_allowed": False,
            "trade_action_enabled": False,
            "real_execution_allowed": False,
        }


@dataclass(frozen=True)
class ScoringPolicySnapshot:
    """Paper-only scoring policy snapshot."""

    snapshot_id: str
    source_layer: str
    score_fields: List[str]
    reason_code_fields: List[str]
    risk_flag_fields: List[str]
    confidence_fields: List[str] = field(default_factory=list)
    data_quality_fields: List[str] = field(default_factory=list)
    snapshot_status: str = "SNAPSHOT_REVIEW_REQUIRED"
    notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Return a serializable policy snapshot with closed boundaries."""

        return {
            "snapshot_id": self.snapshot_id,
            "source_layer": self.source_layer,
            "score_fields": list(self.score_fields),
            "reason_code_fields": list(self.reason_code_fields),
            "risk_flag_fields": list(self.risk_flag_fields),
            "confidence_fields": list(self.confidence_fields),
            "data_quality_fields": list(self.data_quality_fields),
            "snapshot_status": self.snapshot_status,
            "notes": list(self.notes),
            "created_at_utc": _utc_now_iso(),
            "paper_only": True,
            "local_only": True,
            "read_only": True,
            "sidecar_only": True,
            "operator_review_required": True,
            "score_mutation_allowed": False,
            "reason_code_mutation_allowed": False,
            "risk_flag_deletion_allowed": False,
            "source_content_mutation_allowed": False,
            "source_deletion_allowed": False,
            "source_overwrite_allowed": False,
            "trade_action_enabled": False,
            "real_execution_allowed": False,
            "future_return_prediction_allowed": False,
            "guaranteed_performance_claim_allowed": False,
        }


def build_model_rule_record(
    *,
    rule_id: str,
    rule_name: str,
    rule_category: str,
    source_layer: str,
    rule_status: str = "REVIEW_REQUIRED",
    description: str = "",
    governed_fields: Optional[List[str]] = None,
    reason_codes: Optional[List[str]] = None,
    risk_flags: Optional[List[str]] = None,
    limitations: Optional[List[str]] = None,
) -> ModelRuleRecord:
    """Build one validated model governance rule record."""

    if rule_category not in RULE_CATEGORY_VALUES:
        raise ValueError(f"Unsupported rule category: {rule_category}")

    if rule_status not in RULE_STATUS_VALUES:
        raise ValueError(f"Unsupported rule status: {rule_status}")

    return ModelRuleRecord(
        rule_id=rule_id,
        rule_name=rule_name,
        rule_category=rule_category,
        source_layer=source_layer,
        rule_status=rule_status,
        description=description,
        governed_fields=list(governed_fields or []),
        reason_codes=list(reason_codes or []),
        risk_flags=list(risk_flags or []),
        limitations=list(limitations or []),
        operator_review_required=True,
    )


def build_scoring_policy_snapshot(
    *,
    snapshot_id: str,
    source_layer: str,
    score_fields: List[str],
    reason_code_fields: List[str],
    risk_flag_fields: List[str],
    confidence_fields: Optional[List[str]] = None,
    data_quality_fields: Optional[List[str]] = None,
    notes: Optional[List[str]] = None,
) -> ScoringPolicySnapshot:
    """Build a paper-only scoring policy snapshot."""

    if not score_fields:
        snapshot_status = "SNAPSHOT_PARTIAL"
    elif not reason_code_fields or not risk_flag_fields:
        snapshot_status = "SNAPSHOT_REVIEW_REQUIRED"
    else:
        snapshot_status = "SNAPSHOT_READY"

    return ScoringPolicySnapshot(
        snapshot_id=snapshot_id,
        source_layer=source_layer,
        score_fields=list(score_fields),
        reason_code_fields=list(reason_code_fields),
        risk_flag_fields=list(risk_flag_fields),
        confidence_fields=list(confidence_fields or []),
        data_quality_fields=list(data_quality_fields or []),
        snapshot_status=snapshot_status,
        notes=list(notes or []),
    )


def build_model_rule_registry(
    *,
    registry_id: str,
    rules: List[ModelRuleRecord],
    snapshots: List[ScoringPolicySnapshot],
    notes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build a paper-only model rule registry packet."""

    blocked_rules = [rule.rule_id for rule in rules if rule.rule_status == "BLOCKED"]
    review_required_rules = [
        rule.rule_id
        for rule in rules
        if rule.rule_status in {"REVIEW_REQUIRED", "OBSERVED_ONLY"}
    ]
    partial_snapshots = [
        snapshot.snapshot_id
        for snapshot in snapshots
        if snapshot.snapshot_status != "SNAPSHOT_READY"
    ]

    if blocked_rules:
        registry_status = "GOVERNANCE_BLOCKED"
    elif review_required_rules or partial_snapshots:
        registry_status = "GOVERNANCE_REVIEW_REQUIRED"
    else:
        registry_status = "GOVERNANCE_READY_FOR_OPERATOR_REVIEW"

    return {
        "app_id": "MODEL-GOVERNANCE-APP-1",
        "stage_id": "MODEL-GOVERNANCE-D3",
        "registry_id": registry_id,
        "registry_status": registry_status,
        "created_at_utc": _utc_now_iso(),
        "rule_count": len(rules),
        "snapshot_count": len(snapshots),
        "blocked_rules": blocked_rules,
        "review_required_rules": review_required_rules,
        "partial_snapshots": partial_snapshots,
        "rules": [rule.to_dict() for rule in rules],
        "scoring_policy_snapshots": [snapshot.to_dict() for snapshot in snapshots],
        "notes": list(notes or []),
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "score_mutation_allowed": False,
        "reason_code_mutation_allowed": False,
        "risk_flag_deletion_allowed": False,
        "source_content_mutation_allowed": False,
        "source_deletion_allowed": False,
        "source_overwrite_allowed": False,
        "trade_action_enabled": False,
        "real_execution_allowed": False,
        "automatic_position_sizing_allowed": False,
        "automatic_portfolio_action_allowed": False,
        "future_return_prediction_allowed": False,
        "guaranteed_performance_claim_allowed": False,
    }


def validate_model_rule_registry_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate model rule registry schema and closed safety boundary."""

    required_fields = [
        "app_id",
        "stage_id",
        "registry_id",
        "registry_status",
        "rules",
        "scoring_policy_snapshots",
        "operator_review_required",
        "score_mutation_allowed",
        "real_execution_allowed",
    ]
    missing_fields = [field for field in required_fields if field not in payload]

    unsafe_true_fields = [
        field
        for field in [
            "score_mutation_allowed",
            "reason_code_mutation_allowed",
            "risk_flag_deletion_allowed",
            "source_content_mutation_allowed",
            "source_deletion_allowed",
            "source_overwrite_allowed",
            "trade_action_enabled",
            "real_execution_allowed",
            "automatic_position_sizing_allowed",
            "automatic_portfolio_action_allowed",
            "future_return_prediction_allowed",
            "guaranteed_performance_claim_allowed",
        ]
        if payload.get(field) is True
    ]

    return {
        "schema_id": "MODEL-GOVERNANCE-D3-RULE-REGISTRY",
        "is_valid": not missing_fields and not unsafe_true_fields,
        "missing_fields": missing_fields,
        "unsafe_true_fields": unsafe_true_fields,
        "operator_review_required": payload.get("operator_review_required") is True,
        "score_mutation_allowed": payload.get("score_mutation_allowed") is True,
        "real_execution_allowed": payload.get("real_execution_allowed") is True,
    }
