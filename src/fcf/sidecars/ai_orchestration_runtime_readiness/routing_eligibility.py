"""Readiness-only routing eligibility contracts."""

import re
from typing import Any, Mapping, Sequence

from .contract import (
    APP_ID,
    READINESS_MODE,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_POLICY_IDENTIFIERS,
    REQUIRED_TRUE_FLAGS,
)
from .role_contracts import (
    TERMINAL_OPERATOR_ROLE_ID,
    validate_machine_readable_role_contract_manifest,
)


STAGE_ID = "AI-ORCHESTRATION-RUNTIME-READINESS-D3"
ROUTING_CONTRACT_VERSION = "1.0.0"

ROUTING_ELIGIBILITY_STATUSES = (
    "ELIGIBLE_FOR_OPERATOR_REVIEW",
    "BLOCKED",
    "DEGRADED",
)

ROUTING_CONTRACT_STATUSES = (
    "READY_FOR_RUNTIME_LIMIT_CONTRACTS",
    "BLOCKED",
    "DEGRADED",
)

HEALTH_STATUSES = (
    "HEALTHY",
    "DEGRADED",
    "UNAVAILABLE",
)

POLICY_CHECK_STATUSES = (
    "ALLOWED",
    "BLOCKED",
)

REGISTRATION_STATUSES = (
    "VERIFIED",
    "MISSING",
)

COST_LIMIT_STATUSES = (
    "WITHIN_LIMIT",
    "EXCEEDED",
    "UNKNOWN",
)

ROUTING_POLICY_IDENTIFIERS = (
    "FCF.POLICY.RUNTIME.ROUTING.COST_LIMIT_REQUIRED",
    "FCF.POLICY.RUNTIME.ROUTING.HEALTH_EVIDENCE_REQUIRED",
    "FCF.POLICY.RUNTIME.ROUTING.NO_AUTOMATIC_SELECTION",
    "FCF.POLICY.RUNTIME.ROUTING.OPERATOR_REVIEW_REQUIRED",
    "FCF.POLICY.RUNTIME.ROUTING.POLICY_CONFIG_MATCH_REQUIRED",
    "FCF.POLICY.RUNTIME.ROUTING.REGISTERED_ARTIFACTS_REQUIRED",
    "FCF.POLICY.RUNTIME.ROUTING.ROLE_CONTRACT_REQUIRED",
)

REQUIRED_CANDIDATE_FIELDS = (
    "candidate_id",
    "role_id",
    "provider_id",
    "model_version_id",
    "prompt_version_id",
    "policy_identifier",
    "policy_version",
    "policy_digest",
    "config_snapshot_id",
    "registered_artifacts_status",
    "privacy_policy_status",
    "licensing_policy_status",
    "health_status",
    "cost_limit_status",
    "operator_review_required",
    "automatic_routing_allowed",
    "model_invocation_status",
    "prompt_execution_status",
    "route_execution_status",
    "eligibility_status",
    "blocking_reasons",
    "degradation_reasons",
)

REQUIRED_ROUTING_CONTRACT_FIELDS = (
    "routing_contract_id",
    "app_id",
    "stage_id",
    "routing_contract_version",
    "readiness_mode",
    "source_role_manifest_id",
    "policy_identifiers",
    "config_snapshot_linkage_status",
    "candidates",
    "candidate_count",
    "eligible_candidate_count",
    "degraded_candidate_count",
    "blocked_candidate_count",
    "automatic_routing_status",
    "route_selection_status",
    "winner_selection_status",
    "model_invocation_status",
    "prompt_execution_status",
    "runtime_execution_status",
    "routing_contract_status",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class RoutingEligibilityViolation(ValueError):
    """Raised when a readiness-only routing contract is invalid."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _canonical_strings(values: Sequence[str]) -> list[str]:
    return sorted(set(values))


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_canonical_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(
            isinstance(item, str) and item.strip()
            for item in value
        )
        and value == sorted(set(value))
    )


def _routing_policy_identifiers() -> list[str]:
    return _canonical_strings(
        REQUIRED_POLICY_IDENTIFIERS
        + ROUTING_POLICY_IDENTIFIERS
    )


def _derive_candidate_state(
    *,
    registered_artifacts_status: str,
    privacy_policy_status: str,
    licensing_policy_status: str,
    health_status: str,
    cost_limit_status: str,
) -> tuple[str, list[str], list[str]]:
    blocking_reasons: list[str] = []
    degradation_reasons: list[str] = []

    if registered_artifacts_status != "VERIFIED":
        blocking_reasons.append(
            "registered_artifacts_not_verified"
        )

    if privacy_policy_status != "ALLOWED":
        blocking_reasons.append("privacy_policy_blocked")

    if licensing_policy_status != "ALLOWED":
        blocking_reasons.append("licensing_policy_blocked")

    if health_status == "UNAVAILABLE":
        blocking_reasons.append("provider_unavailable")
    elif health_status == "DEGRADED":
        degradation_reasons.append("provider_degraded")

    if cost_limit_status == "EXCEEDED":
        blocking_reasons.append("cost_limit_exceeded")
    elif cost_limit_status == "UNKNOWN":
        degradation_reasons.append("cost_limit_unknown")

    if blocking_reasons:
        return (
            "BLOCKED",
            _canonical_strings(blocking_reasons),
            _canonical_strings(degradation_reasons),
        )

    if degradation_reasons:
        return (
            "DEGRADED",
            [],
            _canonical_strings(degradation_reasons),
        )

    return "ELIGIBLE_FOR_OPERATOR_REVIEW", [], []


def build_routing_candidate(
    *,
    candidate_id: str,
    role_id: str,
    provider_id: str,
    model_version_id: str,
    prompt_version_id: str,
    policy_identifier: str,
    policy_version: str,
    policy_digest: str,
    config_snapshot_id: str,
    registered_artifacts_status: str,
    privacy_policy_status: str,
    licensing_policy_status: str,
    health_status: str,
    cost_limit_status: str,
) -> dict[str, Any]:
    """Build one non-executable routing eligibility candidate."""
    identifier_values = {
        "candidate_id": candidate_id,
        "role_id": role_id,
        "provider_id": provider_id,
        "model_version_id": model_version_id,
        "prompt_version_id": prompt_version_id,
        "policy_identifier": policy_identifier,
        "policy_version": policy_version,
        "policy_digest": policy_digest,
        "config_snapshot_id": config_snapshot_id,
    }

    invalid_fields = [
        field
        for field, value in identifier_values.items()
        if not _valid_identifier(value)
    ]
    if invalid_fields:
        raise RoutingEligibilityViolation(
            ";".join(
                f"{field}_invalid"
                for field in sorted(invalid_fields)
            )
        )

    allowed_statuses = {
        "registered_artifacts_status": REGISTRATION_STATUSES,
        "privacy_policy_status": POLICY_CHECK_STATUSES,
        "licensing_policy_status": POLICY_CHECK_STATUSES,
        "health_status": HEALTH_STATUSES,
        "cost_limit_status": COST_LIMIT_STATUSES,
    }

    values = {
        "registered_artifacts_status": (
            registered_artifacts_status
        ),
        "privacy_policy_status": privacy_policy_status,
        "licensing_policy_status": licensing_policy_status,
        "health_status": health_status,
        "cost_limit_status": cost_limit_status,
    }

    invalid_statuses = [
        field
        for field, allowed in allowed_statuses.items()
        if values[field] not in allowed
    ]
    if invalid_statuses:
        raise RoutingEligibilityViolation(
            ";".join(
                f"{field}_invalid"
                for field in sorted(invalid_statuses)
            )
        )

    (
        eligibility_status,
        blocking_reasons,
        degradation_reasons,
    ) = _derive_candidate_state(
        registered_artifacts_status=(
            registered_artifacts_status
        ),
        privacy_policy_status=privacy_policy_status,
        licensing_policy_status=licensing_policy_status,
        health_status=health_status,
        cost_limit_status=cost_limit_status,
    )

    return {
        **identifier_values,
        "registered_artifacts_status": (
            registered_artifacts_status
        ),
        "privacy_policy_status": privacy_policy_status,
        "licensing_policy_status": licensing_policy_status,
        "health_status": health_status,
        "cost_limit_status": cost_limit_status,
        "operator_review_required": True,
        "automatic_routing_allowed": False,
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "route_execution_status": "NOT_ALLOWED",
        "eligibility_status": eligibility_status,
        "blocking_reasons": blocking_reasons,
        "degradation_reasons": degradation_reasons,
    }


def _clone_candidate(
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    cloned = dict(candidate)
    cloned["blocking_reasons"] = list(
        candidate["blocking_reasons"]
    )
    cloned["degradation_reasons"] = list(
        candidate["degradation_reasons"]
    )
    return cloned


def _contract_status(
    candidates: Sequence[Mapping[str, Any]],
) -> str:
    statuses = {
        str(candidate["eligibility_status"])
        for candidate in candidates
    }

    if not candidates or statuses == {"BLOCKED"}:
        return "BLOCKED"

    if "BLOCKED" in statuses or "DEGRADED" in statuses:
        return "DEGRADED"

    return "READY_FOR_RUNTIME_LIMIT_CONTRACTS"


def build_routing_eligibility_contract(
    *,
    routing_contract_id: str,
    role_manifest: Mapping[str, Any],
    candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build deterministic non-executable D3 routing eligibility."""
    manifest_errors = (
        validate_machine_readable_role_contract_manifest(
            role_manifest
        )
    )
    if manifest_errors:
        raise RoutingEligibilityViolation(
            ";".join(manifest_errors)
        )

    if not _valid_identifier(routing_contract_id):
        raise RoutingEligibilityViolation(
            "routing_contract_id_invalid"
        )

    if not isinstance(candidates, Sequence) or isinstance(
        candidates,
        (str, bytes),
    ):
        raise RoutingEligibilityViolation(
            "candidates_must_be_sequence"
        )

    cloned_candidates = [
        _clone_candidate(candidate)
        for candidate in candidates
    ]

    role_ids = {
        str(role["role_id"])
        for role in role_manifest["roles"]
        if role["role_id"] != TERMINAL_OPERATOR_ROLE_ID
    }

    for candidate in cloned_candidates:
        if candidate.get("role_id") not in role_ids:
            raise RoutingEligibilityViolation(
                "candidate_role_id_not_routable"
            )

        candidate_errors = validate_routing_candidate(
            candidate
        )
        if candidate_errors:
            raise RoutingEligibilityViolation(
                ";".join(candidate_errors)
            )

    candidate_ids = [
        str(candidate["candidate_id"])
        for candidate in cloned_candidates
    ]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise RoutingEligibilityViolation(
            "candidate_ids_must_be_unique"
        )

    counts = {
        status: sum(
            1
            for candidate in cloned_candidates
            if candidate["eligibility_status"] == status
        )
        for status in ROUTING_ELIGIBILITY_STATUSES
    }

    return {
        "routing_contract_id": routing_contract_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "routing_contract_version": (
            ROUTING_CONTRACT_VERSION
        ),
        "readiness_mode": READINESS_MODE,
        "source_role_manifest_id": (
            role_manifest["manifest_id"]
        ),
        "policy_identifiers": (
            _routing_policy_identifiers()
        ),
        "config_snapshot_linkage_status": (
            "REQUIRED_NOT_ACTIVE"
        ),
        "candidates": cloned_candidates,
        "candidate_count": len(cloned_candidates),
        "eligible_candidate_count": counts[
            "ELIGIBLE_FOR_OPERATOR_REVIEW"
        ],
        "degraded_candidate_count": counts["DEGRADED"],
        "blocked_candidate_count": counts["BLOCKED"],
        "automatic_routing_status": "NOT_ALLOWED",
        "route_selection_status": "NOT_ALLOWED",
        "winner_selection_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "routing_contract_status": _contract_status(
            cloned_candidates
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "safety_flags": _safety_flags(),
    }


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    expected = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )
    if set(value.keys()) != expected:
        errors.append(
            "safety_flag_names_must_match_contract"
        )

    return errors


def validate_routing_candidate(
    candidate: object,
) -> list[str]:
    """Return deterministic candidate validation errors."""
    if not isinstance(candidate, Mapping):
        return ["candidate_must_be_mapping"]

    errors: list[str] = []

    if set(candidate.keys()) != set(
        REQUIRED_CANDIDATE_FIELDS
    ):
        errors.append("candidate_fields_must_match_schema")

    for field in (
        "candidate_id",
        "role_id",
        "provider_id",
        "model_version_id",
        "prompt_version_id",
        "policy_identifier",
        "policy_version",
        "policy_digest",
        "config_snapshot_id",
    ):
        if not _valid_identifier(candidate.get(field)):
            errors.append(f"{field}_invalid")

    allowed_statuses = {
        "registered_artifacts_status": REGISTRATION_STATUSES,
        "privacy_policy_status": POLICY_CHECK_STATUSES,
        "licensing_policy_status": POLICY_CHECK_STATUSES,
        "health_status": HEALTH_STATUSES,
        "cost_limit_status": COST_LIMIT_STATUSES,
    }

    for field, allowed in allowed_statuses.items():
        if candidate.get(field) not in allowed:
            errors.append(f"{field}_invalid")

    if candidate.get("operator_review_required") is not True:
        errors.append(
            "operator_review_required_must_be_true"
        )

    if candidate.get("automatic_routing_allowed") is not False:
        errors.append(
            "automatic_routing_allowed_must_be_false"
        )

    for field in (
        "model_invocation_status",
        "prompt_execution_status",
        "route_execution_status",
    ):
        if candidate.get(field) != "NOT_ALLOWED":
            errors.append(f"{field}_invalid")

    if candidate.get("eligibility_status") not in (
        ROUTING_ELIGIBILITY_STATUSES
    ):
        errors.append("eligibility_status_invalid")

    for field in (
        "blocking_reasons",
        "degradation_reasons",
    ):
        if not _valid_canonical_string_list(
            candidate.get(field)
        ):
            errors.append(f"{field}_invalid")

    statuses_valid = all(
        candidate.get(field) in allowed
        for field, allowed in allowed_statuses.items()
    )

    if statuses_valid:
        (
            expected_status,
            expected_blocking,
            expected_degradation,
        ) = _derive_candidate_state(
            registered_artifacts_status=str(
                candidate["registered_artifacts_status"]
            ),
            privacy_policy_status=str(
                candidate["privacy_policy_status"]
            ),
            licensing_policy_status=str(
                candidate["licensing_policy_status"]
            ),
            health_status=str(candidate["health_status"]),
            cost_limit_status=str(
                candidate["cost_limit_status"]
            ),
        )

        if candidate.get("eligibility_status") != (
            expected_status
        ):
            errors.append("eligibility_status_mismatch")

        if candidate.get("blocking_reasons") != (
            expected_blocking
        ):
            errors.append("blocking_reasons_mismatch")

        if candidate.get("degradation_reasons") != (
            expected_degradation
        ):
            errors.append("degradation_reasons_mismatch")

    return errors


def validate_routing_eligibility_contract(
    contract: object,
) -> list[str]:
    """Return deterministic D3 routing contract errors."""
    if not isinstance(contract, Mapping):
        return ["routing_contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(
        REQUIRED_ROUTING_CONTRACT_FIELDS
    ):
        errors.append(
            "routing_contract_fields_must_match_schema"
        )

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "routing_contract_version": (
            ROUTING_CONTRACT_VERSION
        ),
        "readiness_mode": READINESS_MODE,
        "config_snapshot_linkage_status": (
            "REQUIRED_NOT_ACTIVE"
        ),
        "automatic_routing_status": "NOT_ALLOWED",
        "route_selection_status": "NOT_ALLOWED",
        "winner_selection_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    for field in (
        "routing_contract_id",
        "source_role_manifest_id",
    ):
        if not _valid_identifier(contract.get(field)):
            errors.append(f"{field}_invalid")

    if contract.get("policy_identifiers") != (
        _routing_policy_identifiers()
    ):
        errors.append("policy_identifiers_invalid")

    candidates = contract.get("candidates")
    if not isinstance(candidates, list):
        errors.append("candidates_must_be_list")
        candidates = []

    candidate_ids: list[str] = []

    for candidate in candidates:
        errors.extend(validate_routing_candidate(candidate))
        if (
            isinstance(candidate, Mapping)
            and isinstance(
                candidate.get("candidate_id"),
                str,
            )
        ):
            candidate_ids.append(candidate["candidate_id"])

    if len(candidate_ids) != len(set(candidate_ids)):
        errors.append("candidate_ids_must_be_unique")

    expected_counts = {
        "candidate_count": len(candidates),
        "eligible_candidate_count": sum(
            1
            for candidate in candidates
            if isinstance(candidate, Mapping)
            and candidate.get("eligibility_status")
            == "ELIGIBLE_FOR_OPERATOR_REVIEW"
        ),
        "degraded_candidate_count": sum(
            1
            for candidate in candidates
            if isinstance(candidate, Mapping)
            and candidate.get("eligibility_status")
            == "DEGRADED"
        ),
        "blocked_candidate_count": sum(
            1
            for candidate in candidates
            if isinstance(candidate, Mapping)
            and candidate.get("eligibility_status")
            == "BLOCKED"
        ),
    }

    for field, expected in expected_counts.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    valid_candidates = [
        candidate
        for candidate in candidates
        if isinstance(candidate, Mapping)
        and candidate.get("eligibility_status")
        in ROUTING_ELIGIBILITY_STATUSES
    ]

    expected_status = _contract_status(valid_candidates)
    if contract.get("routing_contract_status") != (
        expected_status
    ):
        errors.append("routing_contract_status_invalid")

    if contract.get("routing_contract_status") not in (
        ROUTING_CONTRACT_STATUSES
    ):
        errors.append(
            "routing_contract_status_not_supported"
        )

    errors.extend(
        _validate_safety_flags(
            contract.get("safety_flags")
        )
    )

    return errors
