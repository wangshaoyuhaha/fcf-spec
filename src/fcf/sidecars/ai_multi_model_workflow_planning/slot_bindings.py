"""Planning-only role-to-model-slot binding contracts."""

import re
from typing import Any, Mapping, Sequence

from fcf.sidecars.ai_orchestration_runtime_readiness import (
    ROLE_AUTHORITIES,
    ROLE_KINDS,
    TERMINAL_OPERATOR_ROLE_ID,
    validate_machine_readable_role_contract_manifest,
)

from .contract import (
    APP_ID,
    MODEL_SLOT_TYPES,
    PLANNING_MODE,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    validate_multi_model_workflow_boundary_contract,
)

STAGE_ID = "AI-MULTI-MODEL-WORKFLOW-PLANNING-D2"
SLOT_BINDING_VERSION = "1.0.0"

EXECUTION_LOCATIONS = (
    "LOCAL",
    "CLOUD",
)

REQUIRED_SLOT_ASSIGNMENT_FIELDS = (
    "slot_type",
    "model_registry_entry_id",
    "prompt_registry_entry_id",
    "provider_id",
    "execution_location",
    "policy_identifier",
    "policy_version",
    "policy_digest",
    "config_snapshot_id",
    "binding_status",
    "cloud_eligibility_status",
    "operator_review_required",
    "automatic_selection_allowed",
    "automatic_switching_allowed",
    "model_invocation_status",
    "prompt_execution_status",
    "runtime_activation_status",
)

REQUIRED_ROLE_BINDING_FIELDS = (
    "role_id",
    "role_kind",
    "authority",
    "source_role_manifest_id",
    "required_slot_types",
    "model_slots",
    "slot_binding_status",
    "operator_review_required",
    "automatic_selection_status",
    "automatic_switching_status",
    "model_invocation_status",
    "prompt_execution_status",
    "runtime_activation_status",
)

REQUIRED_MANIFEST_FIELDS = (
    "manifest_id",
    "app_id",
    "stage_id",
    "slot_binding_version",
    "planning_mode",
    "source_boundary_contract_id",
    "source_boundary_contract_version",
    "source_role_manifest_id",
    "role_bindings",
    "role_binding_count",
    "planned_ai_role_count",
    "policy_authority",
    "operator_role_id",
    "automatic_selection_status",
    "automatic_switching_status",
    "model_invocation_status",
    "prompt_execution_status",
    "runtime_activation_status",
    "manifest_status",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class ModelSlotBindingViolation(ValueError):
    """Raised when a planning-only slot binding is invalid."""


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


def _clone_slot(
    slot: Mapping[str, Any],
) -> dict[str, Any]:
    return dict(slot)


def build_model_slot_assignment(
    *,
    slot_type: str,
    model_registry_entry_id: str,
    prompt_registry_entry_id: str,
    provider_id: str,
    execution_location: str,
    policy_identifier: str,
    policy_version: str,
    policy_digest: str,
    config_snapshot_id: str,
) -> dict[str, Any]:
    """Build one non-executable registered slot reference."""
    if slot_type not in MODEL_SLOT_TYPES:
        raise ModelSlotBindingViolation("slot_type_invalid")

    if execution_location not in EXECUTION_LOCATIONS:
        raise ModelSlotBindingViolation(
            "execution_location_invalid"
        )

    identifiers = {
        "model_registry_entry_id": model_registry_entry_id,
        "prompt_registry_entry_id": prompt_registry_entry_id,
        "provider_id": provider_id,
        "policy_identifier": policy_identifier,
        "policy_version": policy_version,
        "policy_digest": policy_digest,
        "config_snapshot_id": config_snapshot_id,
    }

    invalid_fields = [
        field
        for field, value in identifiers.items()
        if not _valid_identifier(value)
    ]

    if invalid_fields:
        raise ModelSlotBindingViolation(
            ";".join(
                f"{field}_invalid"
                for field in sorted(invalid_fields)
            )
        )

    if (
        slot_type == "LOCAL_ONLY"
        and execution_location != "LOCAL"
    ):
        raise ModelSlotBindingViolation(
            "local_only_slot_requires_local_location"
        )

    if (
        slot_type == "CLOUD_APPROVED"
        and execution_location != "CLOUD"
    ):
        raise ModelSlotBindingViolation(
            "cloud_approved_slot_requires_cloud_location"
        )

    cloud_eligibility_status = (
        "POLICY_REVIEW_REQUIRED"
        if execution_location == "CLOUD"
        else "NOT_APPLICABLE"
    )

    return {
        "slot_type": slot_type,
        **identifiers,
        "execution_location": execution_location,
        "binding_status": "PLANNED_NOT_ACTIVE",
        "cloud_eligibility_status": cloud_eligibility_status,
        "operator_review_required": True,
        "automatic_selection_allowed": False,
        "automatic_switching_allowed": False,
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_activation_status": "NOT_ALLOWED",
    }


def _validate_slot_assignment(
    slot: object,
) -> list[str]:
    if not isinstance(slot, Mapping):
        return ["slot_assignment_must_be_mapping"]

    errors: list[str] = []

    if set(slot.keys()) != set(
        REQUIRED_SLOT_ASSIGNMENT_FIELDS
    ):
        errors.append(
            "slot_assignment_fields_must_match_schema"
        )

    slot_type = slot.get("slot_type")
    if slot_type not in MODEL_SLOT_TYPES:
        errors.append("slot_type_invalid")

    location = slot.get("execution_location")
    if location not in EXECUTION_LOCATIONS:
        errors.append("execution_location_invalid")

    for field in (
        "model_registry_entry_id",
        "prompt_registry_entry_id",
        "provider_id",
        "policy_identifier",
        "policy_version",
        "policy_digest",
        "config_snapshot_id",
    ):
        if not _valid_identifier(slot.get(field)):
            errors.append(f"{field}_invalid")

    if (
        slot_type == "LOCAL_ONLY"
        and location != "LOCAL"
    ):
        errors.append(
            "local_only_slot_requires_local_location"
        )

    if (
        slot_type == "CLOUD_APPROVED"
        and location != "CLOUD"
    ):
        errors.append(
            "cloud_approved_slot_requires_cloud_location"
        )

    expected_cloud_status = (
        "POLICY_REVIEW_REQUIRED"
        if location == "CLOUD"
        else "NOT_APPLICABLE"
    )

    if slot.get("cloud_eligibility_status") != (
        expected_cloud_status
    ):
        errors.append("cloud_eligibility_status_invalid")

    expected_scalars = {
        "binding_status": "PLANNED_NOT_ACTIVE",
        "operator_review_required": True,
        "automatic_selection_allowed": False,
        "automatic_switching_allowed": False,
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_activation_status": "NOT_ALLOWED",
    }

    for field, expected in expected_scalars.items():
        if slot.get(field) != expected:
            errors.append(f"{field}_invalid")

    return errors


def _ordered_slots(
    slots: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    order = {
        slot_type: index
        for index, slot_type in enumerate(MODEL_SLOT_TYPES)
    }

    return sorted(
        [_clone_slot(slot) for slot in slots],
        key=lambda item: order[str(item["slot_type"])],
    )


def build_role_model_slot_binding_manifest(
    *,
    manifest_id: str,
    boundary_contract: Mapping[str, Any],
    role_manifest: Mapping[str, Any],
    assignments_by_role: Mapping[
        str,
        Sequence[Mapping[str, Any]],
    ],
) -> dict[str, Any]:
    """Build deterministic D2 role-to-slot bindings."""
    boundary_errors = (
        validate_multi_model_workflow_boundary_contract(
            boundary_contract
        )
    )
    if boundary_errors:
        raise ModelSlotBindingViolation(
            ";".join(boundary_errors)
        )

    role_errors = (
        validate_machine_readable_role_contract_manifest(
            role_manifest
        )
    )
    if role_errors:
        raise ModelSlotBindingViolation(
            ";".join(role_errors)
        )

    if not _valid_identifier(manifest_id):
        raise ModelSlotBindingViolation(
            "manifest_id_invalid"
        )

    if not isinstance(assignments_by_role, Mapping):
        raise ModelSlotBindingViolation(
            "assignments_by_role_must_be_mapping"
        )

    roles = role_manifest["roles"]
    role_ids = {
        str(role["role_id"])
        for role in roles
    }

    unknown_role_ids = sorted(
        set(assignments_by_role.keys()) - role_ids
    )
    if unknown_role_ids:
        raise ModelSlotBindingViolation(
            "unknown_assignment_role_ids:"
            + ",".join(unknown_role_ids)
        )

    role_bindings: list[dict[str, Any]] = []
    planned_ai_role_count = 0

    for role in roles:
        role_id = str(role["role_id"])
        role_kind = str(role["role_kind"])
        raw_slots = assignments_by_role.get(role_id, ())

        if isinstance(raw_slots, (str, bytes)):
            raise ModelSlotBindingViolation(
                f"role_slots_invalid:{role_id}"
            )

        if not isinstance(raw_slots, Sequence):
            raise ModelSlotBindingViolation(
                f"role_slots_invalid:{role_id}"
            )

        if role_kind == "PLANNED_AI_ROLE":
            planned_ai_role_count += 1

            slots = [
                _clone_slot(slot)
                for slot in raw_slots
            ]

            slot_errors: list[str] = []
            for slot in slots:
                slot_errors.extend(
                    _validate_slot_assignment(slot)
                )

            if slot_errors:
                raise ModelSlotBindingViolation(
                    ";".join(slot_errors)
                )

            slot_types = [
                str(slot["slot_type"])
                for slot in slots
            ]

            if len(slot_types) != len(set(slot_types)):
                raise ModelSlotBindingViolation(
                    f"duplicate_slot_types:{role_id}"
                )

            if set(slot_types) != set(MODEL_SLOT_TYPES):
                raise ModelSlotBindingViolation(
                    f"required_slot_types_missing:{role_id}"
                )

            model_slots = _ordered_slots(slots)
            required_slot_types = list(MODEL_SLOT_TYPES)
            slot_binding_status = "PLANNED_NOT_ACTIVE"
        else:
            if list(raw_slots):
                raise ModelSlotBindingViolation(
                    f"non_ai_role_cannot_bind_models:{role_id}"
                )

            model_slots = []
            required_slot_types = []
            slot_binding_status = "NOT_APPLICABLE"

        role_bindings.append(
            {
                "role_id": role_id,
                "role_kind": role_kind,
                "authority": str(role["authority"]),
                "source_role_manifest_id": (
                    role_manifest["manifest_id"]
                ),
                "required_slot_types": required_slot_types,
                "model_slots": model_slots,
                "slot_binding_status": slot_binding_status,
                "operator_review_required": True,
                "automatic_selection_status": "NOT_ALLOWED",
                "automatic_switching_status": "NOT_ALLOWED",
                "model_invocation_status": "NOT_ALLOWED",
                "prompt_execution_status": "NOT_ALLOWED",
                "runtime_activation_status": "NOT_ALLOWED",
            }
        )

    return {
        "manifest_id": manifest_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "slot_binding_version": SLOT_BINDING_VERSION,
        "planning_mode": PLANNING_MODE,
        "source_boundary_contract_id": (
            boundary_contract["contract_id"]
        ),
        "source_boundary_contract_version": (
            boundary_contract["contract_version"]
        ),
        "source_role_manifest_id": (
            role_manifest["manifest_id"]
        ),
        "role_bindings": role_bindings,
        "role_binding_count": len(role_bindings),
        "planned_ai_role_count": planned_ai_role_count,
        "policy_authority": "DETERMINISTIC_POLICY_ONLY",
        "operator_role_id": TERMINAL_OPERATOR_ROLE_ID,
        "automatic_selection_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_activation_status": "NOT_ALLOWED",
        "manifest_status": (
            "READY_FOR_POLICY_ELIGIBILITY_PLANNING"
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "safety_flags": _safety_flags(),
    }


def _validate_role_binding(
    binding: object,
) -> list[str]:
    if not isinstance(binding, Mapping):
        return ["role_binding_must_be_mapping"]

    errors: list[str] = []

    if set(binding.keys()) != set(
        REQUIRED_ROLE_BINDING_FIELDS
    ):
        errors.append(
            "role_binding_fields_must_match_schema"
        )

    if not _valid_identifier(binding.get("role_id")):
        errors.append("role_id_invalid")

    role_kind = binding.get("role_kind")
    if role_kind not in ROLE_KINDS:
        errors.append("role_kind_invalid")

    if binding.get("authority") not in ROLE_AUTHORITIES:
        errors.append("authority_invalid")

    if not _valid_identifier(
        binding.get("source_role_manifest_id")
    ):
        errors.append("source_role_manifest_id_invalid")

    if binding.get("operator_review_required") is not True:
        errors.append(
            "operator_review_required_must_be_true"
        )

    for field in (
        "automatic_selection_status",
        "automatic_switching_status",
        "model_invocation_status",
        "prompt_execution_status",
        "runtime_activation_status",
    ):
        if binding.get(field) != "NOT_ALLOWED":
            errors.append(f"{field}_invalid")

    slots = binding.get("model_slots")
    required_slot_types = binding.get(
        "required_slot_types"
    )

    if not isinstance(slots, list):
        errors.append("model_slots_must_be_list")
        slots = []

    if not isinstance(required_slot_types, list):
        errors.append(
            "required_slot_types_must_be_list"
        )
        required_slot_types = []

    if role_kind == "PLANNED_AI_ROLE":
        if binding.get("slot_binding_status") != (
            "PLANNED_NOT_ACTIVE"
        ):
            errors.append("slot_binding_status_invalid")

        if required_slot_types != list(MODEL_SLOT_TYPES):
            errors.append("required_slot_types_invalid")

        slot_types: list[str] = []

        for slot in slots:
            errors.extend(_validate_slot_assignment(slot))

            if (
                isinstance(slot, Mapping)
                and isinstance(slot.get("slot_type"), str)
            ):
                slot_types.append(slot["slot_type"])

        if len(slot_types) != len(set(slot_types)):
            errors.append("slot_types_must_be_unique")

        if slot_types != list(MODEL_SLOT_TYPES):
            errors.append("model_slots_order_invalid")
    else:
        if binding.get("slot_binding_status") != (
            "NOT_APPLICABLE"
        ):
            errors.append("slot_binding_status_invalid")

        if required_slot_types:
            errors.append(
                "non_ai_required_slot_types_must_be_empty"
            )

        if slots:
            errors.append(
                "non_ai_model_slots_must_be_empty"
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


def validate_role_model_slot_binding_manifest(
    manifest: object,
) -> list[str]:
    """Return deterministic D2 slot-binding errors."""
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
        "slot_binding_version": SLOT_BINDING_VERSION,
        "planning_mode": PLANNING_MODE,
        "policy_authority": "DETERMINISTIC_POLICY_ONLY",
        "operator_role_id": TERMINAL_OPERATOR_ROLE_ID,
        "automatic_selection_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_activation_status": "NOT_ALLOWED",
        "manifest_status": (
            "READY_FOR_POLICY_ELIGIBILITY_PLANNING"
        ),
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if manifest.get(field) != expected:
            errors.append(f"{field}_invalid")

    for field in (
        "manifest_id",
        "source_boundary_contract_id",
        "source_boundary_contract_version",
        "source_role_manifest_id",
    ):
        if not _valid_identifier(manifest.get(field)):
            errors.append(f"{field}_invalid")

    bindings = manifest.get("role_bindings")
    if not isinstance(bindings, list) or not bindings:
        errors.append(
            "role_bindings_must_be_non_empty_list"
        )
        bindings = []

    role_ids: list[str] = []

    for binding in bindings:
        errors.extend(_validate_role_binding(binding))

        if (
            isinstance(binding, Mapping)
            and isinstance(binding.get("role_id"), str)
        ):
            role_ids.append(binding["role_id"])

        if (
            isinstance(binding, Mapping)
            and binding.get("source_role_manifest_id")
            != manifest.get("source_role_manifest_id")
        ):
            errors.append(
                "role_binding_source_manifest_mismatch"
            )

    if len(role_ids) != len(set(role_ids)):
        errors.append("role_ids_must_be_unique")

    if (
        role_ids
        and role_ids[-1] != TERMINAL_OPERATOR_ROLE_ID
    ):
        errors.append(
            "human_operator_must_be_terminal_role"
        )

    if manifest.get("role_binding_count") != len(
        bindings
    ):
        errors.append("role_binding_count_invalid")

    planned_ai_count = sum(
        1
        for binding in bindings
        if (
            isinstance(binding, Mapping)
            and binding.get("role_kind")
            == "PLANNED_AI_ROLE"
        )
    )

    if manifest.get("planned_ai_role_count") != (
        planned_ai_count
    ):
        errors.append("planned_ai_role_count_invalid")

    errors.extend(
        _validate_safety_flags(
            manifest.get("safety_flags")
        )
    )

    return errors