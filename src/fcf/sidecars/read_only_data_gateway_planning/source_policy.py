"""Deterministic D3 source-policy decision."""

import re
from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from .normalized_envelope import validate_normalized_data_envelope


_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class SourcePolicyDecisionViolation(ValueError):
    """Raised when a source-policy decision cannot be built."""


def _canonical_reasons(value: object) -> list[str]:
    if not isinstance(value, list):
        return []

    return sorted(
        {
            item
            for item in value
            if isinstance(item, str) and item
        }
    )


def build_source_policy_decision(
    *,
    decision_id: str,
    normalized_envelope: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a deterministic planning-only source-policy decision."""
    if (
        not isinstance(decision_id, str)
        or _IDENTIFIER_PATTERN.fullmatch(decision_id) is None
    ):
        raise SourcePolicyDecisionViolation(
            "decision_id_invalid"
        )

    if not isinstance(normalized_envelope, Mapping):
        raise SourcePolicyDecisionViolation(
            "normalized_envelope_must_be_mapping"
        )

    envelope = deepcopy(dict(normalized_envelope))

    envelope_errors = validate_normalized_data_envelope(
        envelope
    )

    if envelope_errors:
        raise SourcePolicyDecisionViolation(
            ";".join(envelope_errors)
        )

    blocking_reasons = _canonical_reasons(
        envelope["blocking_reasons"]
    )
    degradation_reasons = _canonical_reasons(
        envelope["degradation_reasons"]
    )

    if envelope["credential_scan_status"] != "CLEAR":
        blocking_reasons.append(
            "credential_scan_not_clear"
        )

    if envelope["allowed_use"] == "PROHIBITED":
        blocking_reasons.append(
            "source_use_prohibited"
        )

    if envelope["gateway_status"] == "BLOCKED":
        blocking_reasons.append(
            "source_envelope_blocked"
        )

    blocking_reasons = sorted(set(blocking_reasons))

    if blocking_reasons:
        status = "BLOCKED"
        cloud_eligible = False
        local_processing_required = True
    else:
        if envelope["allowed_use"] == "RESTRICTED":
            degradation_reasons.append(
                "source_use_restricted"
            )

        if envelope["gateway_status"] == "DEGRADED":
            degradation_reasons.append(
                "source_envelope_degraded"
            )

        degradation_reasons = sorted(
            set(degradation_reasons)
        )

        if degradation_reasons:
            status = "DEGRADED"
            cloud_eligible = False
            local_processing_required = True
        elif envelope["cloud_processing_allowed"] is True:
            status = "CLOUD_ELIGIBLE"
            cloud_eligible = True
            local_processing_required = False
        else:
            status = "LOCAL_ONLY"
            cloud_eligible = False
            local_processing_required = True

    return {
        "decision_id": decision_id,
        "source_envelope_id": envelope["envelope_id"],
        "source_evidence_id": envelope["evidence_id"],
        "source_policy_status": status,
        "cloud_eligible": cloud_eligible,
        "local_processing_required": (
            local_processing_required
        ),
        "runtime_activation_allowed": False,
        "blocking_reasons": list(blocking_reasons),
        "degradation_reasons": list(
            degradation_reasons
        ),
        "operator_review_status": "REVIEW_REQUIRED",
    }

def validate_source_policy_decision(
    decision: object,
    normalized_envelope: object,
) -> list[str]:
    """Return deterministic D3 source-policy validation errors."""
    if not isinstance(decision, Mapping):
        return ["decision_must_be_mapping"]

    if not isinstance(normalized_envelope, Mapping):
        return ["normalized_envelope_must_be_mapping"]

    envelope = deepcopy(dict(normalized_envelope))

    envelope_errors = validate_normalized_data_envelope(
        envelope
    )

    if envelope_errors:
        return [
            f"source_envelope_{error}"
            for error in envelope_errors
        ]

    errors: list[str] = []

    required_fields = {
        "decision_id",
        "source_envelope_id",
        "source_evidence_id",
        "source_policy_status",
        "cloud_eligible",
        "local_processing_required",
        "runtime_activation_allowed",
        "blocking_reasons",
        "degradation_reasons",
        "operator_review_status",
    }

    if set(decision.keys()) != required_fields:
        errors.append(
            "decision_fields_must_match_schema"
        )

    decision_id = decision.get("decision_id")

    if not isinstance(decision_id, str) or not decision_id:
        errors.append("decision_id_invalid")
        decision_id = "validation.decision"

    expected = build_source_policy_decision(
        decision_id=decision_id,
        normalized_envelope=envelope,
    )

    for field in (
        "source_envelope_id",
        "source_evidence_id",
        "operator_review_status",
    ):
        if decision.get(field) != expected[field]:
            errors.append(f"{field}_invalid")

    if (
        decision.get("source_policy_status")
        != expected["source_policy_status"]
    ):
        errors.append(
            "source_policy_status_mismatch"
        )

    if (
        decision.get("cloud_eligible")
        is not expected["cloud_eligible"]
    ):
        errors.append(
            "cloud_eligibility_mismatch"
        )

    if (
        decision.get("local_processing_required")
        is not expected["local_processing_required"]
    ):
        errors.append(
            "local_processing_requirement_mismatch"
        )

    if decision.get("runtime_activation_allowed") is not False:
        errors.append(
            "runtime_activation_allowed_must_be_false"
        )

    if (
        decision.get("blocking_reasons")
        != expected["blocking_reasons"]
    ):
        errors.append(
            "blocking_reasons_mismatch"
        )

    if (
        decision.get("degradation_reasons")
        != expected["degradation_reasons"]
    ):
        errors.append(
            "degradation_reasons_mismatch"
        )

    if (
        decision.get("source_policy_status")
        in ("CLOUD_ELIGIBLE", "LOCAL_ONLY")
        and (
            decision.get("blocking_reasons")
            or decision.get("degradation_reasons")
        )
    ):
        errors.append(
            "ready_decision_must_not_include_reasons"
        )

    return errors