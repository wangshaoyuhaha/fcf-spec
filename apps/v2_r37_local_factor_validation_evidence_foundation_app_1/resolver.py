from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc

from .contracts import FactorValidationPacket, VALIDATION_CHECK_TYPES, ValidationCheckEvidence
from .registry import LocalFactorValidationEvidenceRegistry


@dataclass(frozen=True)
class FactorValidationSnapshot:
    candidate_id: str
    evaluated_at_utc: str
    state: str
    checks: tuple[ValidationCheckEvidence, ...]
    packet: FactorValidationPacket | None
    missing_check_types: tuple[str, ...]
    failed_check_types: tuple[str, ...]
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str


def resolve_factor_validation(registry: LocalFactorValidationEvidenceRegistry, *, candidate_id: str, as_of_utc: str) -> FactorValidationSnapshot:
    candidate = identifier(candidate_id, "candidate_id")
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    checks = tuple(sorted((item for item in registry.checks if item.candidate_id == candidate and instant(item.evaluated_at_utc) <= as_of), key=lambda item: item.check_type))
    present = {item.check_type for item in checks}
    missing = tuple(item for item in VALIDATION_CHECK_TYPES if item not in present)
    failed = tuple(item.check_type for item in checks if item.outcome == "FAILED")
    packet = next((item for item in registry.packets if item.candidate.candidate_id == candidate and instant(item.available_at_utc) <= as_of), None)
    if not checks:
        state, reasons = "MISSING", ("NO_REGISTERED_VALIDATION_EVIDENCE",)
    elif missing:
        state, reasons = "INCOMPLETE", ("SEVEN_CLASS_VALIDATION_COVERAGE_INCOMPLETE",)
    elif failed:
        state, reasons = "FAILED", ("REGISTERED_VALIDATION_FAILURE_PRESERVED",)
    elif packet is None:
        state, reasons = "INCOMPLETE", ("REGISTERED_VALIDATION_PACKET_MISSING",)
    else:
        state, reasons = "PASSED_REVIEW_REQUIRED", ("SEVEN_CLASS_VALIDATION_EVIDENCE_PASSED", "NO_AUTOMATIC_PROMOTION", "NO_FACTOR_ACTIVATION")
    payload = {"candidate_id": candidate, "checks": [item.check_hash for item in checks], "evaluated_at_utc": evaluated, "failed": list(failed), "missing": list(missing), "packet": None if packet is None else packet.packet_hash, "reasons": list(reasons), "state": state}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return FactorValidationSnapshot(candidate, evaluated, state, checks, packet, missing, failed, tuple(reasons), True, digest)
