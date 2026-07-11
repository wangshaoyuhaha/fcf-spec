"""Registered artifact and version-lock roadmap plan."""

import re
from typing import Any, Mapping, Sequence

from .contract import (
    ALLOWED_INPUTS,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    ROADMAP_MODE,
)


STAGE_ID = "AI-ORCHESTRATION-ROADMAP-D2"
ARTIFACT_PLAN_VERSION = "1.0.0"

REGISTRATION_STATUSES = (
    "REGISTERED",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "ARCHIVED",
)

VERSION_PIN_STATUSES = (
    "PINNED",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

DEPENDENCY_ROLES = (
    "SOURCE",
    "GOVERNANCE_EVIDENCE",
    "VERSION_REGISTRY",
    "VALIDATION_GATE",
    "TRACEABILITY",
    "OPERATOR_GATE",
)

PLAN_STATUSES = (
    "READY_FOR_DAG_PLANNING",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

REQUIRED_ARTIFACT_REFERENCE_FIELDS = (
    "artifact_id",
    "artifact_type",
    "artifact_version",
    "registration_status",
    "dependency_role",
    "correlation_id",
    "research_run_id",
    "version_pin_status",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "safety_flags",
)

REQUIRED_VERSION_LOCK_FIELDS = (
    "artifact_id",
    "artifact_type",
    "artifact_version",
    "version_pin_status",
)

REQUIRED_PLAN_FIELDS = (
    "plan_id",
    "artifact_references",
    "required_artifact_types",
    "present_artifact_types",
    "missing_required_artifact_types",
    "version_locks",
    "plan_status",
    "operator_review_status",
    "roadmap_mode",
    "runtime_execution_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)

_VERSION_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,63}$"
)


class ArtifactPlanViolation(ValueError):
    """Raised when registered roadmap artifact inputs are invalid."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_version(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _VERSION_PATTERN.fullmatch(value) is not None
    )


def _valid_canonical_string_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False

    if any(
        not isinstance(item, str) or not item
        for item in value
    ):
        return False

    return value == sorted(set(value))


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
        errors.append("safety_flag_names_must_match_contract")

    return errors


def build_registered_artifact_reference(
    *,
    artifact_id: str,
    artifact_type: str,
    artifact_version: str,
    registration_status: str,
    dependency_role: str,
    correlation_id: str,
    research_run_id: str,
    version_pin_status: str,
) -> dict[str, Any]:
    """Build a non-executable registered artifact reference."""
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "artifact_version": artifact_version,
        "registration_status": registration_status,
        "dependency_role": dependency_role,
        "correlation_id": correlation_id,
        "research_run_id": research_run_id,
        "version_pin_status": version_pin_status,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "safety_flags": _safety_flags(),
    }


def validate_registered_artifact_reference(
    reference: object,
) -> list[str]:
    """Return deterministic artifact-reference errors."""
    if not isinstance(reference, Mapping):
        return ["artifact_reference_must_be_mapping"]

    errors: list[str] = []

    if set(reference.keys()) != set(
        REQUIRED_ARTIFACT_REFERENCE_FIELDS
    ):
        errors.append(
            "artifact_reference_fields_must_match_schema"
        )

    for field in (
        "artifact_id",
        "correlation_id",
        "research_run_id",
    ):
        if not _valid_identifier(reference.get(field)):
            errors.append(f"{field}_invalid")

    if reference.get("artifact_type") not in ALLOWED_INPUTS:
        errors.append("artifact_type_invalid")

    if not _valid_version(
        reference.get("artifact_version")
    ):
        errors.append("artifact_version_invalid")

    if reference.get("registration_status") not in (
        REGISTRATION_STATUSES
    ):
        errors.append("registration_status_invalid")

    if reference.get("dependency_role") not in (
        DEPENDENCY_ROLES
    ):
        errors.append("dependency_role_invalid")

    if reference.get("version_pin_status") not in (
        VERSION_PIN_STATUSES
    ):
        errors.append("version_pin_status_invalid")

    if reference.get("source_artifacts_preserved") is not True:
        errors.append(
            "source_artifacts_preserved_must_be_true"
        )

    if (
        reference.get("original_conclusions_preserved")
        is not True
    ):
        errors.append(
            "original_conclusions_preserved_must_be_true"
        )

    errors.extend(
        _validate_safety_flags(
            reference.get("safety_flags")
        )
    )

    return errors


def _clone_reference(
    reference: Mapping[str, Any],
) -> dict[str, Any]:
    cloned = dict(reference)
    cloned["safety_flags"] = dict(
        reference["safety_flags"]
    )
    return cloned


def _canonical_references(
    references: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        [_clone_reference(reference) for reference in references],
        key=lambda item: (
            str(item["artifact_type"]),
            str(item["artifact_id"]),
            str(item["artifact_version"]),
        ),
    )


def _version_locks(
    references: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    return [
        {
            "artifact_id": str(reference["artifact_id"]),
            "artifact_type": str(reference["artifact_type"]),
            "artifact_version": str(
                reference["artifact_version"]
            ),
            "version_pin_status": str(
                reference["version_pin_status"]
            ),
        }
        for reference in references
    ]


def _derive_plan_status(
    references: Sequence[Mapping[str, Any]],
    missing_required_artifact_types: Sequence[str],
) -> str:
    if any(
        reference["registration_status"] == "BLOCKED"
        or reference["version_pin_status"] == "BLOCKED"
        for reference in references
    ):
        return "BLOCKED"

    if missing_required_artifact_types:
        return "REVIEW_REQUIRED"

    if any(
        reference["registration_status"] != "REGISTERED"
        or reference["version_pin_status"] != "PINNED"
        for reference in references
    ):
        return "REVIEW_REQUIRED"

    return "READY_FOR_DAG_PLANNING"


def build_registered_artifact_dependency_plan(
    *,
    plan_id: str,
    artifact_references: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build the deterministic D2 dependency and version plan."""
    if (
        not isinstance(artifact_references, Sequence)
        or isinstance(artifact_references, (str, bytes))
    ):
        raise ArtifactPlanViolation(
            "artifact_references_must_be_sequence"
        )

    validated: list[Mapping[str, Any]] = []
    artifact_ids: set[str] = set()

    for index, reference in enumerate(artifact_references):
        errors = validate_registered_artifact_reference(
            reference
        )

        if errors:
            raise ArtifactPlanViolation(
                "artifact_reference:"
                + str(index)
                + ":"
                + ";".join(errors)
            )

        artifact_id = str(reference["artifact_id"])

        if artifact_id in artifact_ids:
            raise ArtifactPlanViolation(
                f"duplicate_artifact_id:{artifact_id}"
            )

        artifact_ids.add(artifact_id)
        validated.append(reference)

    canonical_references = _canonical_references(validated)

    present_artifact_types = sorted(
        {
            str(reference["artifact_type"])
            for reference in canonical_references
        }
    )

    required_artifact_types = sorted(ALLOWED_INPUTS)

    missing_required_artifact_types = sorted(
        set(required_artifact_types)
        - set(present_artifact_types)
    )

    locks = _version_locks(canonical_references)

    return {
        "plan_id": plan_id,
        "artifact_references": canonical_references,
        "required_artifact_types": required_artifact_types,
        "present_artifact_types": present_artifact_types,
        "missing_required_artifact_types": (
            missing_required_artifact_types
        ),
        "version_locks": locks,
        "plan_status": _derive_plan_status(
            canonical_references,
            missing_required_artifact_types,
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "roadmap_mode": ROADMAP_MODE,
        "runtime_execution_status": "NOT_ALLOWED",
        "safety_flags": _safety_flags(),
    }


def _valid_version_lock(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False

    if set(value.keys()) != set(
        REQUIRED_VERSION_LOCK_FIELDS
    ):
        return False

    if not _valid_identifier(value.get("artifact_id")):
        return False

    if value.get("artifact_type") not in ALLOWED_INPUTS:
        return False

    if not _valid_version(value.get("artifact_version")):
        return False

    if value.get("version_pin_status") not in (
        VERSION_PIN_STATUSES
    ):
        return False

    return True


def validate_registered_artifact_dependency_plan(
    plan: object,
) -> list[str]:
    """Return deterministic D2 dependency-plan errors."""
    if not isinstance(plan, Mapping):
        return ["artifact_plan_must_be_mapping"]

    errors: list[str] = []

    if set(plan.keys()) != set(REQUIRED_PLAN_FIELDS):
        errors.append("artifact_plan_fields_must_match_schema")

    if not _valid_identifier(plan.get("plan_id")):
        errors.append("plan_id_invalid")

    artifact_references = plan.get("artifact_references")

    if not isinstance(artifact_references, list):
        errors.append("artifact_references_must_be_list")
        artifact_references = []
    else:
        for index, reference in enumerate(
            artifact_references
        ):
            for reference_error in (
                validate_registered_artifact_reference(
                    reference
                )
            ):
                errors.append(
                    "artifact_reference:"
                    + str(index)
                    + ":"
                    + reference_error
                )

        expected_references = _canonical_references(
            artifact_references
        )

        if artifact_references != expected_references:
            errors.append(
                "artifact_references_must_be_canonical"
            )

        artifact_ids = [
            reference.get("artifact_id")
            for reference in artifact_references
            if isinstance(reference, Mapping)
        ]

        if len(artifact_ids) != len(set(artifact_ids)):
            errors.append("artifact_ids_must_be_unique")

    for field in (
        "required_artifact_types",
        "present_artifact_types",
        "missing_required_artifact_types",
    ):
        if not _valid_canonical_string_list(
            plan.get(field)
        ):
            errors.append(f"{field}_invalid")

    if plan.get("required_artifact_types") != sorted(
        ALLOWED_INPUTS
    ):
        errors.append("required_artifact_types_invalid")

    valid_references = [
        reference
        for reference in artifact_references
        if isinstance(reference, Mapping)
    ]

    expected_present = sorted(
        {
            str(reference.get("artifact_type"))
            for reference in valid_references
            if reference.get("artifact_type") in ALLOWED_INPUTS
        }
    )

    expected_missing = sorted(
        set(ALLOWED_INPUTS) - set(expected_present)
    )

    if plan.get("present_artifact_types") != expected_present:
        errors.append("present_artifact_types_mismatch")

    if (
        plan.get("missing_required_artifact_types")
        != expected_missing
    ):
        errors.append(
            "missing_required_artifact_types_mismatch"
        )

    version_locks = plan.get("version_locks")

    if not isinstance(version_locks, list):
        errors.append("version_locks_must_be_list")
    else:
        for index, lock in enumerate(version_locks):
            if not _valid_version_lock(lock):
                errors.append(
                    f"version_lock:{index}:invalid"
                )

        expected_locks = _version_locks(valid_references)

        if version_locks != expected_locks:
            errors.append("version_locks_mismatch")

    expected_status = _derive_plan_status(
        valid_references,
        expected_missing,
    )

    if plan.get("plan_status") not in PLAN_STATUSES:
        errors.append("plan_status_invalid")
    elif plan.get("plan_status") != expected_status:
        errors.append("plan_status_mismatch")

    if plan.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if plan.get("roadmap_mode") != ROADMAP_MODE:
        errors.append("roadmap_mode_invalid")

    if plan.get("runtime_execution_status") != "NOT_ALLOWED":
        errors.append("runtime_execution_must_not_be_allowed")

    errors.extend(
        _validate_safety_flags(
            plan.get("safety_flags")
        )
    )

    return errors
