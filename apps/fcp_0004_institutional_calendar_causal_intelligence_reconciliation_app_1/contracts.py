from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field


SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
STAGE_ID = re.compile(r"^V2-R(?:2[3-9]|3[0-7])$")
GAP_ID = re.compile(r"^V2-FR-GAP-(?:07[1-9]|08[0-6])$")
RECONCILIATION_STATES = ("READY_FOR_OPERATOR_REVIEW", "BLOCKED")
FINDING_SEVERITIES = ("INFO", "BLOCKING")


def safe_id(value: str, name: str) -> str:
    normalized = str(value).strip()
    if not SAFE_ID.fullmatch(normalized):
        raise ValueError(f"{name} is not a safe identifier")
    return normalized


def sorted_unique(values: tuple[str, ...], name: str) -> tuple[str, ...]:
    normalized = tuple(sorted(safe_id(value, name) for value in values))
    if len(normalized) != len(set(normalized)):
        raise ValueError(f"{name} values must be unique")
    return normalized


def digest(payload: object) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class FoundationDeliveryReceipt:
    stage_id: str
    app_id: str
    final_state_path: str
    guard_path: str
    test_path: str
    gap_ids: tuple[str, ...]
    registered_local_only: bool = True
    operator_review_required: bool = True
    production_gap_closed: bool = False
    factor_activation_claimed: bool = False
    receipt_hash: str = field(init=False)

    def __post_init__(self) -> None:
        stage_id = safe_id(self.stage_id, "stage_id")
        if not STAGE_ID.fullmatch(stage_id):
            raise ValueError("stage_id is outside V2-R23 through V2-R37")
        app_id = safe_id(self.app_id, "app_id")
        paths = {}
        for name in ("final_state_path", "guard_path", "test_path"):
            value = safe_id(getattr(self, name), name)
            if value.startswith("/") or ".." in value.split("/"):
                raise ValueError(f"{name} must remain repository relative")
            paths[name] = value
        gaps = sorted_unique(tuple(self.gap_ids), "gap_id")
        if not gaps or any(not GAP_ID.fullmatch(value) for value in gaps):
            raise ValueError("delivery receipt requires registered FCP-0004 gaps")
        if not self.registered_local_only or not self.operator_review_required:
            raise ValueError("delivery receipt must remain registered-local and reviewed")
        object.__setattr__(self, "stage_id", stage_id)
        object.__setattr__(self, "app_id", app_id)
        object.__setattr__(self, "gap_ids", gaps)
        for name, value in paths.items():
            object.__setattr__(self, name, value)
        object.__setattr__(
            self,
            "receipt_hash",
            digest(
                {
                    "app_id": app_id,
                    "factor_activation_claimed": self.factor_activation_claimed,
                    "final_state_path": paths["final_state_path"],
                    "gap_ids": gaps,
                    "guard_path": paths["guard_path"],
                    "operator_review_required": self.operator_review_required,
                    "production_gap_closed": self.production_gap_closed,
                    "registered_local_only": self.registered_local_only,
                    "stage_id": stage_id,
                    "test_path": paths["test_path"],
                }
            ),
        )


@dataclass(frozen=True)
class InstitutionalArchitectureRegistry:
    receipts: tuple[FoundationDeliveryReceipt, ...]
    candidate_ids: tuple[str, ...]
    proposal_id: str = "FCF-FCP-0004"
    proposal_status: str = "ACCEPTED_ARCHITECTURE"
    operator_decision: str = "ACCEPTED_ARCHITECTURE"
    phase_id: str = "NONE"
    registry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        receipts = tuple(sorted(self.receipts, key=lambda item: item.stage_id))
        stages = tuple(item.stage_id for item in receipts)
        if len(stages) != len(set(stages)):
            raise ValueError("delivery stage ids must be unique")
        candidates = sorted_unique(tuple(self.candidate_ids), "candidate_id")
        if self.proposal_id != "FCF-FCP-0004":
            raise ValueError("registry proposal id is not FCF-FCP-0004")
        if self.proposal_status != "ACCEPTED_ARCHITECTURE":
            raise ValueError("proposal status must remain ACCEPTED_ARCHITECTURE")
        if self.operator_decision != "ACCEPTED_ARCHITECTURE":
            raise ValueError("Operator decision must remain ACCEPTED_ARCHITECTURE")
        if self.phase_id != "NONE":
            raise ValueError("architecture reconciliation cannot authorize a phase")
        object.__setattr__(self, "receipts", receipts)
        object.__setattr__(self, "candidate_ids", candidates)
        object.__setattr__(
            self,
            "registry_hash",
            digest(
                {
                    "candidate_ids": candidates,
                    "operator_decision": self.operator_decision,
                    "phase_id": self.phase_id,
                    "proposal_id": self.proposal_id,
                    "proposal_status": self.proposal_status,
                    "receipt_hashes": tuple(item.receipt_hash for item in receipts),
                }
            ),
        )


@dataclass(frozen=True)
class ReconciliationFinding:
    code: str
    severity: str
    subject_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        safe_id(self.code, "finding_code")
        if self.severity not in FINDING_SEVERITIES:
            raise ValueError("finding severity is not registered")
        sorted_unique(tuple(self.subject_ids), "finding_subject_id")


@dataclass(frozen=True)
class InstitutionalArchitectureReconciliation:
    state: str
    registry_hash: str
    findings: tuple[ReconciliationFinding, ...]
    missing_stage_ids: tuple[str, ...]
    unexpected_stage_ids: tuple[str, ...]
    missing_gap_ids: tuple[str, ...]
    mapping_mismatch_stage_ids: tuple[str, ...]
    missing_candidate_ids: tuple[str, ...]
    unexpected_candidate_ids: tuple[str, ...]
    overclaim_stage_ids: tuple[str, ...]
    gap_coverage: tuple[tuple[str, tuple[str, ...]], ...]
    expected_overlap_gap_ids: tuple[str, ...]
    operator_review_required: bool
    production_gap_closure_claimed: bool
    factor_activation_claimed: bool
    reconciliation_hash: str

    def __post_init__(self) -> None:
        if self.state not in RECONCILIATION_STATES:
            raise ValueError("reconciliation state is not registered")
        if not self.operator_review_required:
            raise ValueError("architecture reconciliation requires Operator review")
        if self.production_gap_closure_claimed or self.factor_activation_claimed:
            raise ValueError("architecture reconciliation cannot claim production authority")
