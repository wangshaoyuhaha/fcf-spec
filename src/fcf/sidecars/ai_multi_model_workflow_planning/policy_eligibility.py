"""Deterministic policy eligibility planning for model slots."""

import re
from typing import Any, Mapping, Sequence

from fcf.sidecars.ai_orchestration_runtime_readiness import (
    COST_LIMIT_STATUSES,
    HEALTH_STATUSES,
    POLICY_CHECK_STATUSES,
    REGISTRATION_STATUSES,
    ROUTING_ELIGIBILITY_STATUSES,
    validate_routing_candidate,
)

from .contract import (
    APP_ID,
    MODEL_SLOT_TYPES,
    PLANNING_MODE,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
)
from .slot_bindings import (
    validate_role_model_slot_binding_manifest,
)

STAGE_ID = "AI-MULTI-MODEL-WORKFLOW-PLANNING-D3"
POLICY_ELIGIBILITY_VERSION = "1.0.0"

REQUIRED_EVALUATION_FIELDS = (
    "role_id",
    "slot_type",
    "model_registry_entry_id",
    "prompt_registry_entry_id",
    "provider_id",
    "execution_location",
    "policy_identifier",
    "policy_version",
    "policy_digest",
    "config_snapshot_id",
    "source_candidate_id",
    "registered_artifacts_status",
    "privacy_policy_status",
    "licensing_policy_status",
    "health_status",
    "cost_limit_status",
    "eligibility_status",
    "blocking_reasons",
    "degradation_reasons",
    "operator_review_required",
    "automatic_selection_allowed",
    "automatic_switching_allowed",
    "automatic_routing_allowed",
    "model_invocation_status",
    "prompt_execution_status",
    "route_execution_status",
    "runtime_activation_status",
)

REQUIRED_MANIFEST_FIELDS = (
    "manifest_id",
    "app_id",
    "stage_id",
    "policy_eligibility_version",
    "planning_mode",
    "source_slot_manifest_id",
    "source_slot_binding_version",
    "evaluations",
    "evaluation_count",
    "eligible_count",
    "degraded_count",
    "blocked_count",
    "policy_authority",
    "automatic_selection_status",
    "automatic_switching_status",
    "automatic_routing_status",
    "model_invocation_status",
    "prompt_execution_status",
    "route_execution_status",
    "runtime_activation_status",
    "manifest_status",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class PolicyEligibilityViolation(ValueError):
    """Raised when policy eligibility planning is invalid."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _canonical_strings(values: Sequence[str]) -> list[str]:
    return sorted(set(values))


def _valid_canonical_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(
            isinstance(item, str) and item.strip()
            for item in value
        )
        and value == sorted(set(value))
    )


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
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


def _slot_key(
    role_id: str,
    slot: Mapping[str, Any],
) -> tuple[str, ...]:
    return (
        role_id,
        str(slot["model_registry_entry_id"]),
        str(slot["prompt_registry_entry_id"]),
        str(slot["provider_id"]),
        str(slot["policy_identifier"]),
        str(slot["policy_version"]),
        str(slot["policy_digest"]),
        str(slot["config_snapshot_id"]),
    )


def _candidate_key(
    candidate: Mapping[str, Any],
) -> tuple[str, ...]:
    return (
        str(candidate["role_id"]),
        str(candidate["model_version_id"]),
        str(candidate["prompt_version_id"]),
        str(candidate["provider_id"]),
        str(candidate["policy_identifier"]),
        str(candidate["policy_version"]),
        str(candidate["policy_digest"]),
        str(candidate["config_snapshot_id"]),
    )


def _blocked_evaluation(
    *,
    role_id: str,
    slot: Mapping[str, Any],
    source_candidate_id: str,
    reason: str,
) -> dict[str, Any]:
    return {
        "role_id": role_id,
        "slot_type": slot["slot_type"],
        "model_registry_entry_id": (
            slot["model_registry_entry_id"]
        ),
        "prompt_registry_entry_id": (
            slot["prompt_registry_entry_id"]
        ),
        "provider_id": slot["provider_id"],
        "execution_location": slot["execution_location"],
        "policy_identifier": slot["policy_identifier"],
        "policy_version": slot["policy_version"],
        "policy_digest": slot["policy_digest"],
        "config_snapshot_id": slot["config_snapshot_id"],
        "source_candidate_id": source_candidate_id,
        "registered_artifacts_status": "MISSING",
        "privacy_policy_status": "BLOCKED",
        "licensing_policy_status": "BLOCKED",
        "health_status": "UNAVAILABLE",
        "cost_limit_status": "UNKNOWN",
        "eligibility_status": "BLOCKED",
        "blocking_reasons": [reason],
        "degradation_reasons": [],
        "operator_review_required": True,
        "automatic_selection_allowed": False,
        "automatic_switching_allowed": False,
        "automatic_routing_allowed": False,
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "route_execution_status": "NOT_ALLOWED",
        "runtime_activation_status": "NOT_ALLOWED",
    }


def _candidate_evaluation(
    *,
    role_id: str,
    slot: Mapping[str, Any],
    candidate: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "role_id": role_id,
        "slot_type": slot["slot_type"],
        "model_registry_entry_id": (
            slot["model_registry_entry_id"]
        ),
        "prompt_registry_entry_id": (
            slot["prompt_registry_entry_id"]
        ),
        "provider_id": slot["provider_id"],
        "execution_location": slot["execution_location"],
        "policy_identifier": slot["policy_identifier"],
        "policy_version": slot["policy_version"],
        "policy_digest": slot["policy_digest"],
        "config_snapshot_id": slot["config_snapshot_id"],
        "source_candidate_id": candidate["candidate_id"],
        "registered_artifacts_status": (
            candidate["registered_artifacts_status"]
        ),
        "privacy_policy_status": (
            candidate["privacy_policy_status"]
        ),
        "licensing_policy_status": (
            candidate["licensing_policy_status"]
        ),
        "health_status": candidate["health_status"],
        "cost_limit_status": candidate["cost_limit_status"],
        "eligibility_status": candidate["eligibility_status"],
        "blocking_reasons": list(
            candidate["blocking_reasons"]
        ),
        "degradation_reasons": list(
            candidate["degradation_reasons"]
        ),
        "operator_review_required": True,
        "automatic_selection_allowed": False,
        "automatic_switching_allowed": False,
        "automatic_routing_allowed": False,
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "route_execution_status": "NOT_ALLOWED",
        "runtime_activation_status": "NOT_ALLOWED",
    }


def _manifest_status(
    evaluations: Sequence[Mapping[str, Any]],
) -> str:
    statuses = {
        str(item["eligibility_status"])
        for item in evaluations
    }

    if not evaluations or statuses == {"BLOCKED"}:
        return "BLOCKED"

    if "BLOCKED" in statuses or "DEGRADED" in statuses:
        return "DEGRADED"

    return "ELIGIBLE_FOR_OPERATOR_REVIEW"


def build_policy_eligibility_manifest(
    *,
    manifest_id: str,
    slot_binding_manifest: Mapping[str, Any],
    routing_candidates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build deterministic non-executable D3 policy evaluations."""
    slot_errors = (
        validate_role_model_slot_binding_manifest(
            slot_binding_manifest
        )
    )

    if slot_errors:
        raise PolicyEligibilityViolation(
            ";".join(slot_errors)
        )

    if not _valid_identifier(manifest_id):
        raise PolicyEligibilityViolation(
            "manifest_id_invalid"
        )

    if not isinstance(routing_candidates, Sequence):
        raise PolicyEligibilityViolation(
            "routing_candidates_must_be_sequence"
        )

    if isinstance(routing_candidates, (str, bytes)):
        raise PolicyEligibilityViolation(
            "routing_candidates_must_be_sequence"
        )

    candidates = [
        _clone_candidate(candidate)
        for candidate in routing_candidates
    ]

    candidate_ids: list[str] = []

    for candidate in candidates:
        candidate_errors = validate_routing_candidate(
            candidate
        )

        if candidate_errors:
            raise PolicyEligibilityViolation(
                ";".join(candidate_errors)
            )

        candidate_ids.append(
            str(candidate["candidate_id"])
        )

    if len(candidate_ids) != len(set(candidate_ids)):
        raise PolicyEligibilityViolation(
            "candidate_ids_must_be_unique"
        )

    slot_keys: set[tuple[str, ...]] = set()

    for binding in slot_binding_manifest["role_bindings"]:
        if binding["role_kind"] != "PLANNED_AI_ROLE":
            continue

        role_id = str(binding["role_id"])

        for slot in binding["model_slots"]:
            slot_keys.add(_slot_key(role_id, slot))

    for candidate in candidates:
        if _candidate_key(candidate) not in slot_keys:
            raise PolicyEligibilityViolation(
                "candidate_not_bound_to_slot"
            )

    evaluations: list[dict[str, Any]] = []

    for binding in slot_binding_manifest["role_bindings"]:
        if binding["role_kind"] != "PLANNED_AI_ROLE":
            continue

        role_id = str(binding["role_id"])

        for slot in binding["model_slots"]:
            key = _slot_key(role_id, slot)

            matches = [
                candidate
                for candidate in candidates
                if _candidate_key(candidate) == key
            ]

            if len(matches) == 0:
                evaluations.append(
                    _blocked_evaluation(
                        role_id=role_id,
                        slot=slot,
                        source_candidate_id="NOT_AVAILABLE",
                        reason="routing_candidate_missing",
                    )
                )
                continue

            if len(matches) > 1:
                evaluations.append(
                    _blocked_evaluation(
                        role_id=role_id,
                        slot=slot,
                        source_candidate_id="MULTIPLE_MATCHES",
                        reason="routing_candidate_ambiguous",
                    )
                )
                continue

            evaluations.append(
                _candidate_evaluation(
                    role_id=role_id,
                    slot=slot,
                    candidate=matches[0],
                )
            )

    counts = {
        status: sum(
            1
            for evaluation in evaluations
            if evaluation["eligibility_status"] == status
        )
        for status in ROUTING_ELIGIBILITY_STATUSES
    }

    return {
        "manifest_id": manifest_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "policy_eligibility_version": (
            POLICY_ELIGIBILITY_VERSION
        ),
        "planning_mode": PLANNING_MODE,
        "source_slot_manifest_id": (
            slot_binding_manifest["manifest_id"]
        ),
        "source_slot_binding_version": (
            slot_binding_manifest["slot_binding_version"]
        ),
        "evaluations": evaluations,
        "evaluation_count": len(evaluations),
        "eligible_count": counts[
            "ELIGIBLE_FOR_OPERATOR_REVIEW"
        ],
        "degraded_count": counts["DEGRADED"],
        "blocked_count": counts["BLOCKED"],
        "policy_authority": "DETERMINISTIC_POLICY_ONLY",
        "automatic_selection_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "route_execution_status": "NOT_ALLOWED",
        "runtime_activation_status": "NOT_ALLOWED",
        "manifest_status": _manifest_status(evaluations),
        "operator_review_status": "REVIEW_REQUIRED",
        "safety_flags": _safety_flags(),
    }


def _validate_evaluation(
    evaluation: object,
) -> list[str]:
    if not isinstance(evaluation, Mapping):
        return ["evaluation_must_be_mapping"]

    errors: list[str] = []

    if set(evaluation.keys()) != set(
        REQUIRED_EVALUATION_FIELDS
    ):
        errors.append(
            "evaluation_fields_must_match_schema"
        )

    for field in (
        "role_id",
        "model_registry_entry_id",
        "prompt_registry_entry_id",
        "provider_id",
        "policy_identifier",
        "policy_version",
        "policy_digest",
        "config_snapshot_id",
        "source_candidate_id",
    ):
        if not _valid_identifier(evaluation.get(field)):
            errors.append(f"{field}_invalid")

    if evaluation.get("slot_type") not in MODEL_SLOT_TYPES:
        errors.append("slot_type_invalid")

    if evaluation.get("execution_location") not in (
        "LOCAL",
        "CLOUD",
    ):
        errors.append("execution_location_invalid")

    if evaluation.get(
        "registered_artifacts_status"
    ) not in REGISTRATION_STATUSES:
        errors.append(
            "registered_artifacts_status_invalid"
        )

    for field in (
        "privacy_policy_status",
        "licensing_policy_status",
    ):
        if evaluation.get(field) not in POLICY_CHECK_STATUSES:
            errors.append(f"{field}_invalid")

    if evaluation.get("health_status") not in HEALTH_STATUSES:
        errors.append("health_status_invalid")

    if evaluation.get(
        "cost_limit_status"
    ) not in COST_LIMIT_STATUSES:
        errors.append("cost_limit_status_invalid")

    if evaluation.get(
        "eligibility_status"
    ) not in ROUTING_ELIGIBILITY_STATUSES:
        errors.append("eligibility_status_invalid")

    for field in (
        "blocking_reasons",
        "degradation_reasons",
    ):
        if not _valid_canonical_string_list(
            evaluation.get(field)
        ):
            errors.append(f"{field}_invalid")

    expected_values = {
        "operator_review_required": True,
        "automatic_selection_allowed": False,
        "automatic_switching_allowed": False,
        "automatic_routing_allowed": False,
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "route_execution_status": "NOT_ALLOWED",
        "runtime_activation_status": "NOT_ALLOWED",
    }

    for field, expected in expected_values.items():
        if evaluation.get(field) != expected:
            errors.append(f"{field}_invalid")

    return errors


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

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )

    if set(value.keys()) != expected_names:
        errors.append(
            "safety_flag_names_must_match_contract"
        )

    return errors


def validate_policy_eligibility_manifest(
    manifest: object,
) -> list[str]:
    """Return deterministic D3 policy eligibility errors."""
    if not isinstance(manifest, Mapping):
        return ["manifest_must_be_mapping"]

    errors: list[str] = []

    if set(manifest.keys()) != set(
        REQUIRED_MANIFEST_FIELDS
    ):
        errors.append(
            "manifest_fields_must_match_schema"
        )

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "policy_eligibility_version": (
            POLICY_ELIGIBILITY_VERSION
        ),
        "planning_mode": PLANNING_MODE,
        "policy_authority": "DETERMINISTIC_POLICY_ONLY",
        "automatic_selection_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "route_execution_status": "NOT_ALLOWED",
        "runtime_activation_status": "NOT_ALLOWED",
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if manifest.get(field) != expected:
            errors.append(f"{field}_invalid")

    for field in (
        "manifest_id",
        "source_slot_manifest_id",
        "source_slot_binding_version",
    ):
        if not _valid_identifier(manifest.get(field)):
            errors.append(f"{field}_invalid")

    evaluations = manifest.get("evaluations")

    if not isinstance(evaluations, list):
        errors.append("evaluations_must_be_list")
        evaluations = []

    evaluation_keys: list[tuple[str, str]] = []

    for evaluation in evaluations:
        errors.extend(
            _validate_evaluation(evaluation)
        )

        if isinstance(evaluation, Mapping):
            evaluation_keys.append(
                (
                    str(evaluation.get("role_id")),
                    str(evaluation.get("slot_type")),
                )
            )

    if len(evaluation_keys) != len(set(evaluation_keys)):
        errors.append(
            "role_slot_evaluations_must_be_unique"
        )

    expected_counts = {
        "evaluation_count": len(evaluations),
        "eligible_count": sum(
            1
            for item in evaluations
            if isinstance(item, Mapping)
            and item.get("eligibility_status")
            == "ELIGIBLE_FOR_OPERATOR_REVIEW"
        ),
        "degraded_count": sum(
            1
            for item in evaluations
            if isinstance(item, Mapping)
            and item.get("eligibility_status")
            == "DEGRADED"
        ),
        "blocked_count": sum(
            1
            for item in evaluations
            if isinstance(item, Mapping)
            and item.get("eligibility_status")
            == "BLOCKED"
        ),
    }

    for field, expected in expected_counts.items():
        if manifest.get(field) != expected:
            errors.append(f"{field}_invalid")

    valid_evaluations = [
        item
        for item in evaluations
        if isinstance(item, Mapping)
    ]

    if manifest.get("manifest_status") != (
        _manifest_status(valid_evaluations)
    ):
        errors.append("manifest_status_invalid")

    errors.extend(
        _validate_safety_flags(
            manifest.get("safety_flags")
        )
    )

    return errors