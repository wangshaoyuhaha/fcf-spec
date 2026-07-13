"""Planning-only model role assignment profiles."""

from copy import deepcopy
import re
from typing import Any, Mapping

from fcf.sidecars.ai_orchestration_runtime_readiness import (
    ROUTING_ELIGIBILITY_STATUSES,
    validate_runtime_limit_contract_bundle,
)

from .contract import (
    APP_ID,
    MODEL_SLOT_TYPES,
    PLANNING_MODE,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
)
from .policy_eligibility import (
    validate_policy_eligibility_manifest,
)

STAGE_ID = "AI-MULTI-MODEL-WORKFLOW-PLANNING-D4"
ASSIGNMENT_PROFILE_VERSION = "1.0.0"

ASSIGNMENT_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "DEGRADED",
    "BLOCKED",
)

REQUIRED_PROFILE_METADATA_FIELDS = (
    "output_schema_id",
    "output_schema_version",
    "privacy_level",
    "evaluation_baseline_id",
)

REQUIRED_ASSIGNMENT_FIELDS = (
    "role_id",
    "slot_type",
    "source_candidate_id",
    "model_registry_entry_id",
    "prompt_registry_entry_id",
    "provider_id",
    "execution_location",
    "eligibility_status",
    "output_schema_id",
    "output_schema_version",
    "privacy_level",
    "evaluation_baseline_id",
    "approval_status",
    "runtime_limit_bundle",
    "assignment_status",
    "operator_review_required",
    "automatic_selection_status",
    "automatic_switching_status",
    "automatic_routing_status",
    "automatic_retry_status",
    "automatic_fallback_status",
    "model_invocation_status",
    "prompt_execution_status",
    "runtime_execution_status",
)

REQUIRED_MANIFEST_FIELDS = (
    "manifest_id",
    "app_id",
    "stage_id",
    "assignment_profile_version",
    "planning_mode",
    "source_policy_manifest_id",
    "source_policy_eligibility_version",
    "assignments",
    "assignment_count",
    "ready_count",
    "degraded_count",
    "blocked_count",
    "policy_authority",
    "automatic_selection_status",
    "automatic_switching_status",
    "automatic_routing_status",
    "automatic_retry_status",
    "automatic_fallback_status",
    "model_invocation_status",
    "prompt_execution_status",
    "runtime_execution_status",
    "manifest_status",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class AssignmentProfileViolation(ValueError):
    """Raised when a planning-only assignment profile is invalid."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _role_slot_key(role_id: str, slot_type: str) -> str:
    return f"{role_id}::{slot_type}"


def _assignment_status(
    eligibility_status: str,
    bundle_status: str,
) -> str:
    if (
        eligibility_status == "BLOCKED"
        or bundle_status == "BLOCKED"
    ):
        return "BLOCKED"

    if (
        eligibility_status == "DEGRADED"
        or bundle_status == "DEGRADED"
    ):
        return "DEGRADED"

    return "READY_FOR_OPERATOR_REVIEW"


def _manifest_status(
    assignments: list[Mapping[str, Any]],
) -> str:
    statuses = {
        str(item["assignment_status"])
        for item in assignments
    }

    if not assignments or statuses == {"BLOCKED"}:
        return "BLOCKED"

    if "BLOCKED" in statuses or "DEGRADED" in statuses:
        return "DEGRADED"

    return "READY_FOR_OPERATOR_REVIEW"


def build_assignment_profile_manifest(
    *,
    manifest_id: str,
    policy_eligibility_manifest: Mapping[str, Any],
    profile_metadata_by_role_slot: Mapping[
        str,
        Mapping[str, Any],
    ],
    runtime_limit_bundles_by_role_slot: Mapping[
        str,
        Mapping[str, Any],
    ],
) -> dict[str, Any]:
    """Build deterministic non-executable D4 assignment profiles."""
    policy_errors = validate_policy_eligibility_manifest(
        policy_eligibility_manifest
    )

    if policy_errors:
        raise AssignmentProfileViolation(
            ";".join(policy_errors)
        )

    if not _valid_identifier(manifest_id):
        raise AssignmentProfileViolation(
            "manifest_id_invalid"
        )

    if not isinstance(
        profile_metadata_by_role_slot,
        Mapping,
    ):
        raise AssignmentProfileViolation(
            "profile_metadata_must_be_mapping"
        )

    if not isinstance(
        runtime_limit_bundles_by_role_slot,
        Mapping,
    ):
        raise AssignmentProfileViolation(
            "runtime_limit_bundles_must_be_mapping"
        )

    expected_keys = {
        _role_slot_key(
            str(evaluation["role_id"]),
            str(evaluation["slot_type"]),
        )
        for evaluation in policy_eligibility_manifest[
            "evaluations"
        ]
    }

    if set(profile_metadata_by_role_slot.keys()) != expected_keys:
        raise AssignmentProfileViolation(
            "profile_metadata_keys_invalid"
        )

    if set(runtime_limit_bundles_by_role_slot.keys()) != (
        expected_keys
    ):
        raise AssignmentProfileViolation(
            "runtime_limit_bundle_keys_invalid"
        )

    assignments: list[dict[str, Any]] = []

    for evaluation in policy_eligibility_manifest[
        "evaluations"
    ]:
        role_id = str(evaluation["role_id"])
        slot_type = str(evaluation["slot_type"])
        key = _role_slot_key(role_id, slot_type)
        metadata = profile_metadata_by_role_slot[key]

        if not isinstance(metadata, Mapping):
            raise AssignmentProfileViolation(
                f"profile_metadata_invalid:{key}"
            )

        if set(metadata.keys()) != set(
            REQUIRED_PROFILE_METADATA_FIELDS
        ):
            raise AssignmentProfileViolation(
                f"profile_metadata_fields_invalid:{key}"
            )

        invalid_metadata = [
            field
            for field in REQUIRED_PROFILE_METADATA_FIELDS
            if not _valid_identifier(metadata.get(field))
        ]

        if invalid_metadata:
            raise AssignmentProfileViolation(
                ";".join(
                    f"{field}_invalid"
                    for field in sorted(invalid_metadata)
                )
            )

        runtime_bundle = (
            runtime_limit_bundles_by_role_slot[key]
        )
        bundle_errors = (
            validate_runtime_limit_contract_bundle(
                runtime_bundle
            )
        )

        if bundle_errors:
            raise AssignmentProfileViolation(
                ";".join(bundle_errors)
            )

        status = _assignment_status(
            str(evaluation["eligibility_status"]),
            str(runtime_bundle["bundle_status"]),
        )

        assignments.append(
            {
                "role_id": role_id,
                "slot_type": slot_type,
                "source_candidate_id": (
                    evaluation["source_candidate_id"]
                ),
                "model_registry_entry_id": (
                    evaluation["model_registry_entry_id"]
                ),
                "prompt_registry_entry_id": (
                    evaluation["prompt_registry_entry_id"]
                ),
                "provider_id": evaluation["provider_id"],
                "execution_location": (
                    evaluation["execution_location"]
                ),
                "eligibility_status": (
                    evaluation["eligibility_status"]
                ),
                "output_schema_id": (
                    metadata["output_schema_id"]
                ),
                "output_schema_version": (
                    metadata["output_schema_version"]
                ),
                "privacy_level": metadata["privacy_level"],
                "evaluation_baseline_id": (
                    metadata["evaluation_baseline_id"]
                ),
                "approval_status": "REVIEW_REQUIRED",
                "runtime_limit_bundle": deepcopy(
                    runtime_bundle
                ),
                "assignment_status": status,
                "operator_review_required": True,
                "automatic_selection_status": "NOT_ALLOWED",
                "automatic_switching_status": "NOT_ALLOWED",
                "automatic_routing_status": "NOT_ALLOWED",
                "automatic_retry_status": "NOT_ALLOWED",
                "automatic_fallback_status": "NOT_ALLOWED",
                "model_invocation_status": "NOT_ALLOWED",
                "prompt_execution_status": "NOT_ALLOWED",
                "runtime_execution_status": "NOT_ALLOWED",
            }
        )

    counts = {
        status: sum(
            1
            for assignment in assignments
            if assignment["assignment_status"] == status
        )
        for status in ASSIGNMENT_STATUSES
    }

    return {
        "manifest_id": manifest_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "assignment_profile_version": (
            ASSIGNMENT_PROFILE_VERSION
        ),
        "planning_mode": PLANNING_MODE,
        "source_policy_manifest_id": (
            policy_eligibility_manifest["manifest_id"]
        ),
        "source_policy_eligibility_version": (
            policy_eligibility_manifest[
                "policy_eligibility_version"
            ]
        ),
        "assignments": assignments,
        "assignment_count": len(assignments),
        "ready_count": counts[
            "READY_FOR_OPERATOR_REVIEW"
        ],
        "degraded_count": counts["DEGRADED"],
        "blocked_count": counts["BLOCKED"],
        "policy_authority": "DETERMINISTIC_POLICY_ONLY",
        "automatic_selection_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_retry_status": "NOT_ALLOWED",
        "automatic_fallback_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "manifest_status": _manifest_status(assignments),
        "operator_review_status": "REVIEW_REQUIRED",
        "safety_flags": _safety_flags(),
    }


def _validate_assignment(
    assignment: object,
) -> list[str]:
    if not isinstance(assignment, Mapping):
        return ["assignment_must_be_mapping"]

    errors: list[str] = []

    if set(assignment.keys()) != set(
        REQUIRED_ASSIGNMENT_FIELDS
    ):
        errors.append(
            "assignment_fields_must_match_schema"
        )

    for field in (
        "role_id",
        "source_candidate_id",
        "model_registry_entry_id",
        "prompt_registry_entry_id",
        "provider_id",
        "output_schema_id",
        "output_schema_version",
        "privacy_level",
        "evaluation_baseline_id",
    ):
        if not _valid_identifier(assignment.get(field)):
            errors.append(f"{field}_invalid")

    if assignment.get("slot_type") not in MODEL_SLOT_TYPES:
        errors.append("slot_type_invalid")

    if assignment.get("execution_location") not in (
        "LOCAL",
        "CLOUD",
    ):
        errors.append("execution_location_invalid")

    if assignment.get(
        "eligibility_status"
    ) not in ROUTING_ELIGIBILITY_STATUSES:
        errors.append("eligibility_status_invalid")

    if assignment.get(
        "assignment_status"
    ) not in ASSIGNMENT_STATUSES:
        errors.append("assignment_status_invalid")

    if assignment.get("approval_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("approval_status_invalid")

    expected_values = {
        "operator_review_required": True,
        "automatic_selection_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_retry_status": "NOT_ALLOWED",
        "automatic_fallback_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
    }

    for field, expected in expected_values.items():
        if assignment.get(field) != expected:
            errors.append(f"{field}_invalid")

    runtime_bundle = assignment.get(
        "runtime_limit_bundle"
    )
    errors.extend(
        validate_runtime_limit_contract_bundle(
            runtime_bundle
        )
    )

    if isinstance(runtime_bundle, Mapping):
        expected_status = _assignment_status(
            str(assignment.get("eligibility_status")),
            str(runtime_bundle.get("bundle_status")),
        )

        if assignment.get("assignment_status") != (
            expected_status
        ):
            errors.append(
                "assignment_status_derivation_invalid"
            )

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


def validate_assignment_profile_manifest(
    manifest: object,
) -> list[str]:
    """Return deterministic D4 assignment profile errors."""
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
        "assignment_profile_version": (
            ASSIGNMENT_PROFILE_VERSION
        ),
        "planning_mode": PLANNING_MODE,
        "policy_authority": "DETERMINISTIC_POLICY_ONLY",
        "automatic_selection_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_retry_status": "NOT_ALLOWED",
        "automatic_fallback_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if manifest.get(field) != expected:
            errors.append(f"{field}_invalid")

    for field in (
        "manifest_id",
        "source_policy_manifest_id",
        "source_policy_eligibility_version",
    ):
        if not _valid_identifier(manifest.get(field)):
            errors.append(f"{field}_invalid")

    assignments = manifest.get("assignments")

    if not isinstance(assignments, list):
        errors.append("assignments_must_be_list")
        assignments = []

    assignment_keys: list[tuple[str, str]] = []

    for assignment in assignments:
        errors.extend(
            _validate_assignment(assignment)
        )

        if isinstance(assignment, Mapping):
            assignment_keys.append(
                (
                    str(assignment.get("role_id")),
                    str(assignment.get("slot_type")),
                )
            )

    if len(assignment_keys) != len(set(assignment_keys)):
        errors.append(
            "role_slot_assignments_must_be_unique"
        )

    expected_counts = {
        "assignment_count": len(assignments),
        "ready_count": sum(
            1
            for item in assignments
            if isinstance(item, Mapping)
            and item.get("assignment_status")
            == "READY_FOR_OPERATOR_REVIEW"
        ),
        "degraded_count": sum(
            1
            for item in assignments
            if isinstance(item, Mapping)
            and item.get("assignment_status")
            == "DEGRADED"
        ),
        "blocked_count": sum(
            1
            for item in assignments
            if isinstance(item, Mapping)
            and item.get("assignment_status")
            == "BLOCKED"
        ),
    }

    for field, expected in expected_counts.items():
        if manifest.get(field) != expected:
            errors.append(f"{field}_invalid")

    valid_assignments = [
        item
        for item in assignments
        if isinstance(item, Mapping)
    ]

    if manifest.get("manifest_status") != (
        _manifest_status(valid_assignments)
    ):
        errors.append("manifest_status_invalid")

    errors.extend(
        _validate_safety_flags(
            manifest.get("safety_flags")
        )
    )

    return errors