from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc
from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import sha256_text
from apps.v2_r36_local_institutional_factor_lifecycle_foundation_app_1 import InstitutionalFactorCandidate


VALIDATION_CHECK_TYPES = (
    "ABLATION",
    "CAPACITY",
    "LEAKAGE",
    "MULTIPLE_TESTING",
    "OUT_OF_SAMPLE",
    "SENSITIVITY",
    "SURVIVORSHIP",
)
VALIDATION_OUTCOMES = ("FAILED", "PASSED")


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


@dataclass(frozen=True)
class ValidationCheckEvidence:
    check_id: str
    candidate_id: str
    check_type: str
    protocol_id: str
    dataset_id: str
    evaluation_window_id: str
    evaluated_at_utc: str
    evidence_sha256: str
    outcome: str
    reason_codes: tuple[str, ...]
    deterministic_evidence: bool = True
    operator_registered: bool = True
    automatic_pass: bool = False
    check_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("check_id", "candidate_id", "protocol_id", "dataset_id", "evaluation_window_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        check_type = str(self.check_type).strip().upper()
        outcome = str(self.outcome).strip().upper()
        if check_type not in VALIDATION_CHECK_TYPES:
            raise ValueError("validation check type is not registered")
        if outcome not in VALIDATION_OUTCOMES:
            raise ValueError("validation outcome is not registered")
        object.__setattr__(self, "check_type", check_type)
        object.__setattr__(self, "outcome", outcome)
        object.__setattr__(self, "evaluated_at_utc", utc(self.evaluated_at_utc, "evaluated_at_utc"))
        object.__setattr__(self, "evidence_sha256", sha256_text(self.evidence_sha256, "evidence_sha256"))
        reasons = tuple(sorted(identifier(item, "reason_code") for item in self.reason_codes))
        if not reasons or len(set(reasons)) != len(reasons):
            raise ValueError("validation check requires unique reason codes")
        object.__setattr__(self, "reason_codes", reasons)
        if self.deterministic_evidence is not True or self.operator_registered is not True:
            raise ValueError("validation check requires deterministic registered evidence")
        if self.automatic_pass:
            raise ValueError("automatic validation pass is prohibited")
        object.__setattr__(
            self,
            "check_hash",
            _digest(
                {
                    "candidate_id": self.candidate_id,
                    "check_id": self.check_id,
                    "check_type": check_type,
                    "dataset_id": self.dataset_id,
                    "evaluated_at_utc": self.evaluated_at_utc,
                    "evaluation_window_id": self.evaluation_window_id,
                    "evidence_sha256": self.evidence_sha256,
                    "outcome": outcome,
                    "protocol_id": self.protocol_id,
                    "reason_codes": list(reasons),
                }
            ),
        )


@dataclass(frozen=True)
class FactorValidationPacket:
    packet_id: str
    candidate: InstitutionalFactorCandidate
    checks: tuple[ValidationCheckEvidence, ...]
    available_at_utc: str
    operator_registered: bool = True
    automatic_promotion: bool = False
    factor_activation_allowed: bool = False
    all_checks_passed: bool = field(init=False)
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "packet_id", identifier(self.packet_id, "packet_id"))
        if not isinstance(self.candidate, InstitutionalFactorCandidate):
            raise ValueError("validation packet requires an R36 candidate")
        checks = tuple(sorted(self.checks, key=lambda item: item.check_type))
        if any(not isinstance(item, ValidationCheckEvidence) for item in checks):
            raise ValueError("validation packet accepts validation checks only")
        if tuple(item.check_type for item in checks) != VALIDATION_CHECK_TYPES:
            raise ValueError("validation packet requires exact seven-class coverage")
        if any(item.candidate_id != self.candidate.candidate_id for item in checks):
            raise ValueError("validation check candidate mismatch")
        object.__setattr__(self, "checks", checks)
        object.__setattr__(self, "available_at_utc", utc(self.available_at_utc, "available_at_utc"))
        if any(instant(item.evaluated_at_utc) > instant(self.available_at_utc) for item in checks):
            raise ValueError("packet availability cannot precede validation checks")
        if self.operator_registered is not True:
            raise ValueError("validation packet requires Operator registration")
        if self.automatic_promotion or self.factor_activation_allowed:
            raise ValueError("validation packet cannot promote or activate a factor")
        passed = all(item.outcome == "PASSED" for item in checks)
        object.__setattr__(self, "all_checks_passed", passed)
        object.__setattr__(
            self,
            "packet_hash",
            _digest(
                {
                    "available_at_utc": self.available_at_utc,
                    "candidate_hash": self.candidate.candidate_hash,
                    "check_hashes": [item.check_hash for item in checks],
                    "packet_id": self.packet_id,
                }
            ),
        )
