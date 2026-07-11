"""Planning-only role, interface, and responsibility matrix."""

import re
from typing import Any, Mapping, Sequence

from .contract import (
    ALLOWED_INPUTS,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    ROADMAP_MODE,
)
from .gate_plan import (
    GATE_PLAN_STATUSES,
    validate_governance_gate_plan,
)


STAGE_ID = "AI-ORCHESTRATION-ROADMAP-D5"
ROLE_PLAN_VERSION = "1.0.0"

ROLE_KINDS = (
    "PLANNED_AI_ROLE",
    "HUMAN_OPERATOR",
)

ROLE_STATUSES = (
    "PLANNED",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

ROLE_PLAN_STATUSES = (
    "READY_FOR_REVIEW_PACKET",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "INVALID",
)

HUMAN_OPERATOR_ROLE_ID = "human_operator"

ROLE_DEFINITIONS = (
    {
        "role_id": "context_analyst",
        "role_kind": "PLANNED_AI_ROLE",
        "responsibility": (
            "Review registered context evidence without "
            "creating or replacing conclusions."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_CONTEXT_ARTIFACT",
            "REGISTERED_MODEL_VERSION_ARTIFACT",
            "REGISTERED_PROMPT_VERSION_ARTIFACT",
            "REGISTERED_VALIDATION_BASELINE_ARTIFACT",
        ),
        "planned_output_artifact_types": (
            "PLANNED_CONTEXT_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": "evaluation_auditor",
        "role_kind": "PLANNED_AI_ROLE",
        "responsibility": (
            "Review registered evaluation evidence and "
            "version locks without selecting a model."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_CONTEXT_ARTIFACT",
            "REGISTERED_AI_EVALUATION_ARTIFACT",
            "REGISTERED_MODEL_VERSION_ARTIFACT",
            "REGISTERED_PROMPT_VERSION_ARTIFACT",
            "REGISTERED_VALIDATION_BASELINE_ARTIFACT",
        ),
        "planned_output_artifact_types": (
            "PLANNED_EVALUATION_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": "contrarian_reviewer",
        "role_kind": "PLANNED_AI_ROLE",
        "responsibility": (
            "Review registered challenge evidence, "
            "contradictions, and evidence gaps."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_CHALLENGE_ARTIFACT",
            "REGISTERED_AI_CONTEXT_ARTIFACT",
            "REGISTERED_AI_EVALUATION_ARTIFACT",
        ),
        "planned_output_artifact_types": (
            "PLANNED_CHALLENGE_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": "narrative_assessor",
        "role_kind": "PLANNED_AI_ROLE",
        "responsibility": (
            "Review registered market narrative evidence "
            "without determining narrative truth."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_CHALLENGE_ARTIFACT",
            "REGISTERED_AI_CONTEXT_ARTIFACT",
            "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
        ),
        "planned_output_artifact_types": (
            "PLANNED_NARRATIVE_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": "scenario_planner",
        "role_kind": "PLANNED_AI_ROLE",
        "responsibility": (
            "Review registered scenario simulation evidence "
            "without probability, ranking, or winner selection."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_CHALLENGE_ARTIFACT",
            "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
            "REGISTERED_SCENARIO_SIMULATION_ARTIFACT",
        ),
        "planned_output_artifact_types": (
            "PLANNED_SCENARIO_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": "traceability_curator",
        "role_kind": "PLANNED_AI_ROLE",
        "responsibility": (
            "Review registered correlation and provenance "
            "evidence without mutating source artifacts."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_EVALUATION_ARTIFACT",
            "REGISTERED_CORRELATION_ROLLUP_ARTIFACT",
            "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
            "REGISTERED_SCENARIO_SIMULATION_ARTIFACT",
        ),
        "planned_output_artifact_types": (
            "PLANNED_TRACEABILITY_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": HUMAN_OPERATOR_ROLE_ID,
        "role_kind": "HUMAN_OPERATOR",
        "responsibility": (
            "Perform the final manual review and decide "
            "whether any separately approved future work "
            "may proceed."
        ),
        "allowed_input_artifact_types": ALLOWED_INPUTS,
        "planned_output_artifact_types": (
            "PLANNED_OPERATOR_DECISION_RECORD",
        ),
    },
)

REQUIRED_ROLE_FIELDS = (
    "role_id",
    "role_kind",
    "responsibility",
    "allowed_input_artifact_types",
    "planned_output_artifact_types",
    "sequence_index",
    "operator_gate_required",
    "automatic_activation_allowed",
    "automatic_routing_allowed",
    "automatic_switching_allowed",
    "runtime_execution_status",
    "role_status",
    "safety_flags",
)

REQUIRED_OUTPUT_OWNERSHIP_FIELDS = (
    "output_artifact_type",
    "owner_role_id",
)

REQUIRED_ROLE_PLAN_FIELDS = (
    "role_plan_id",
    "source_gate_plan_id",
    "source_gate_plan_status",
    "roles",
    "output_ownership",
    "human_operator_terminal_role_id",
    "automatic_role_switching_status",
    "automatic_route_selection_status",
    "model_invocation_status",
    "prompt_execution_status",
    "role_plan_status",
    "operator_review_status",
    "roadmap_mode",
    "runtime_execution_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class RolePlanViolation(ValueError):
    """Raised when a planning-only role matrix is invalid."""


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


def _valid_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _canonical_strings(
    values: Sequence[str],
) -> list[str]:
    return sorted(set(values))


def _valid_canonical_string_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False

    if any(
        not isinstance(item, str) or not item.strip()
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


def _role_status(source_gate_plan_status: str) -> str:
    if source_gate_plan_status in ("BLOCKED", "INVALID"):
        return "BLOCKED"

    if source_gate_plan_status == "READY_FOR_ROLE_PLANNING":
        return "PLANNED"

    return "REVIEW_REQUIRED"


def _derive_role_plan_status(
    source_gate_plan_status: str,
) -> str:
    if source_gate_plan_status == "BLOCKED":
        return "BLOCKED"

    if source_gate_plan_status == "INVALID":
        return "INVALID"

    if source_gate_plan_status != "READY_FOR_ROLE_PLANNING":
        return "REVIEW_REQUIRED"

    return "READY_FOR_REVIEW_PACKET"


def _build_roles(
    source_gate_plan_status: str,
) -> list[dict[str, Any]]:
    roles: list[dict[str, Any]] = []

    for sequence_index, definition in enumerate(
        ROLE_DEFINITIONS,
        start=1,
    ):
        roles.append(
            {
                "role_id": definition["role_id"],
                "role_kind": definition["role_kind"],
                "responsibility": definition[
                    "responsibility"
                ],
                "allowed_input_artifact_types": (
                    _canonical_strings(
                        definition[
                            "allowed_input_artifact_types"
                        ]
                    )
                ),
                "planned_output_artifact_types": (
                    _canonical_strings(
                        definition[
                            "planned_output_artifact_types"
                        ]
                    )
                ),
                "sequence_index": sequence_index,
                "operator_gate_required": True,
                "automatic_activation_allowed": False,
                "automatic_routing_allowed": False,
                "automatic_switching_allowed": False,
                "runtime_execution_status": "NOT_ALLOWED",
                "role_status": _role_status(
                    source_gate_plan_status
                ),
                "safety_flags": _safety_flags(),
            }
        )

    return roles


def _clone_role(
    role: Mapping[str, Any],
) -> dict[str, Any]:
    cloned = dict(role)
    cloned["allowed_input_artifact_types"] = list(
        role["allowed_input_artifact_types"]
    )
    cloned["planned_output_artifact_types"] = list(
        role["planned_output_artifact_types"]
    )
    cloned["safety_flags"] = dict(role["safety_flags"])
    return cloned


def _canonical_roles(
    roles: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        [_clone_role(role) for role in roles],
        key=lambda item: (
            int(item["sequence_index"]),
            str(item["role_id"]),
        ),
    )


def _output_ownership(
    roles: Sequence[Mapping[str, Any]],
) -> list[dict[str, str]]:
    ownership: list[dict[str, str]] = []

    for role in roles:
        for output_type in role[
            "planned_output_artifact_types"
        ]:
            ownership.append(
                {
                    "output_artifact_type": str(output_type),
                    "owner_role_id": str(role["role_id"]),
                }
            )

    return sorted(
        ownership,
        key=lambda item: (
            item["output_artifact_type"],
            item["owner_role_id"],
        ),
    )


def build_role_responsibility_plan(
    *,
    role_plan_id: str,
    gate_plan: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a non-executable future role responsibility matrix."""
    gate_errors = validate_governance_gate_plan(gate_plan)

    if gate_errors:
        raise RolePlanViolation(";".join(gate_errors))

    source_status = str(gate_plan["gate_plan_status"])
    roles = _canonical_roles(_build_roles(source_status))

    return {
        "role_plan_id": role_plan_id,
        "source_gate_plan_id": gate_plan["gate_plan_id"],
        "source_gate_plan_status": source_status,
        "roles": roles,
        "output_ownership": _output_ownership(roles),
        "human_operator_terminal_role_id": (
            HUMAN_OPERATOR_ROLE_ID
        ),
        "automatic_role_switching_status": "NOT_ALLOWED",
        "automatic_route_selection_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "role_plan_status": _derive_role_plan_status(
            source_status
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "roadmap_mode": ROADMAP_MODE,
        "runtime_execution_status": "NOT_ALLOWED",
        "safety_flags": _safety_flags(),
    }


def _validate_role(
    role: object,
    source_gate_plan_status: str,
) -> list[str]:
    if not isinstance(role, Mapping):
        return ["role_must_be_mapping"]

    errors: list[str] = []

    if set(role.keys()) != set(REQUIRED_ROLE_FIELDS):
        errors.append("role_fields_must_match_schema")

    if not _valid_identifier(role.get("role_id")):
        errors.append("role_id_invalid")

    if role.get("role_kind") not in ROLE_KINDS:
        errors.append("role_kind_invalid")

    if not _valid_non_empty_string(
        role.get("responsibility")
    ):
        errors.append("responsibility_invalid")

    inputs = role.get("allowed_input_artifact_types")

    if not _valid_canonical_string_list(inputs):
        errors.append(
            "allowed_input_artifact_types_invalid"
        )
    elif any(
        artifact_type not in ALLOWED_INPUTS
        for artifact_type in inputs
    ):
        errors.append(
            "allowed_input_artifact_types_not_registered"
        )

    outputs = role.get("planned_output_artifact_types")

    if not _valid_canonical_string_list(outputs):
        errors.append(
            "planned_output_artifact_types_invalid"
        )
    elif not outputs:
        errors.append(
            "planned_output_artifact_types_empty"
        )

    sequence_index = role.get("sequence_index")

    if (
        not isinstance(sequence_index, int)
        or isinstance(sequence_index, bool)
        or sequence_index < 1
    ):
        errors.append("sequence_index_invalid")

    if role.get("operator_gate_required") is not True:
        errors.append(
            "operator_gate_required_must_be_true"
        )

    for field in (
        "automatic_activation_allowed",
        "automatic_routing_allowed",
        "automatic_switching_allowed",
    ):
        if role.get(field) is not False:
            errors.append(f"{field}_must_be_false")

    if role.get("runtime_execution_status") != "NOT_ALLOWED":
        errors.append(
            "runtime_execution_must_not_be_allowed"
        )

    expected_role_status = _role_status(
        source_gate_plan_status
    )

    if role.get("role_status") not in ROLE_STATUSES:
        errors.append("role_status_invalid")
    elif role.get("role_status") != expected_role_status:
        errors.append("role_status_mismatch")

    errors.extend(
        _validate_safety_flags(role.get("safety_flags"))
    )

    return errors


def _valid_output_ownership(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False

    if set(value.keys()) != set(
        REQUIRED_OUTPUT_OWNERSHIP_FIELDS
    ):
        return False

    return (
        _valid_non_empty_string(
            value.get("output_artifact_type")
        )
        and _valid_identifier(value.get("owner_role_id"))
    )


def validate_role_responsibility_plan(
    plan: object,
) -> list[str]:
    """Return deterministic D5 role-plan validation errors."""
    if not isinstance(plan, Mapping):
        return ["role_plan_must_be_mapping"]

    errors: list[str] = []

    if set(plan.keys()) != set(REQUIRED_ROLE_PLAN_FIELDS):
        errors.append("role_plan_fields_must_match_schema")

    for field in (
        "role_plan_id",
        "source_gate_plan_id",
    ):
        if not _valid_identifier(plan.get(field)):
            errors.append(f"{field}_invalid")

    source_status = plan.get("source_gate_plan_status")

    if source_status not in GATE_PLAN_STATUSES:
        errors.append("source_gate_plan_status_invalid")
        source_status_for_validation = "REVIEW_REQUIRED"
    else:
        source_status_for_validation = str(source_status)

    roles = plan.get("roles")

    if not isinstance(roles, list):
        errors.append("roles_must_be_list")
        roles = []
    else:
        for index, role in enumerate(roles):
            for role_error in _validate_role(
                role,
                source_status_for_validation,
            ):
                errors.append(
                    f"role:{index}:{role_error}"
                )

    valid_roles = [
        role
        for role in roles
        if isinstance(role, Mapping)
    ]

    role_ids = [
        str(role.get("role_id"))
        for role in valid_roles
    ]
    sequence_indices = [
        role.get("sequence_index")
        for role in valid_roles
    ]

    if len(role_ids) != len(set(role_ids)):
        errors.append("role_ids_must_be_unique")

    if len(sequence_indices) != len(
        set(sequence_indices)
    ):
        errors.append("sequence_indices_must_be_unique")

    canonical_check_allowed = all(
        isinstance(role.get("sequence_index"), int)
        and not isinstance(
            role.get("sequence_index"),
            bool,
        )
        and "safety_flags" in role
        and "allowed_input_artifact_types" in role
        and "planned_output_artifact_types" in role
        for role in valid_roles
    )

    if canonical_check_allowed:
        if roles != _canonical_roles(valid_roles):
            errors.append("roles_must_be_canonical")

    expected_ownership: list[dict[str, str]] = []

    for role in valid_roles:
        role_id = role.get("role_id")
        outputs = role.get(
            "planned_output_artifact_types"
        )

        if isinstance(role_id, str) and isinstance(
            outputs,
            list,
        ):
            for output_type in outputs:
                if isinstance(output_type, str):
                    expected_ownership.append(
                        {
                            "output_artifact_type": (
                                output_type
                            ),
                            "owner_role_id": role_id,
                        }
                    )

    expected_ownership = sorted(
        expected_ownership,
        key=lambda item: (
            item["output_artifact_type"],
            item["owner_role_id"],
        ),
    )

    ownership = plan.get("output_ownership")

    if not isinstance(ownership, list):
        errors.append("output_ownership_must_be_list")
    else:
        for index, item in enumerate(ownership):
            if not _valid_output_ownership(item):
                errors.append(
                    f"output_ownership:{index}:invalid"
                )

        if ownership != expected_ownership:
            errors.append("output_ownership_mismatch")

        output_types = [
            item.get("output_artifact_type")
            for item in ownership
            if isinstance(item, Mapping)
        ]

        if len(output_types) != len(set(output_types)):
            errors.append(
                "output_artifact_owners_must_be_unique"
            )

    if plan.get("human_operator_terminal_role_id") != (
        HUMAN_OPERATOR_ROLE_ID
    ):
        errors.append(
            "human_operator_terminal_role_id_invalid"
        )

    if valid_roles:
        ordered_roles = sorted(
            valid_roles,
            key=lambda item: (
                item.get("sequence_index")
                if isinstance(
                    item.get("sequence_index"),
                    int,
                )
                else 999999
            ),
        )

        if ordered_roles[-1].get("role_id") != (
            HUMAN_OPERATOR_ROLE_ID
        ):
            errors.append(
                "human_operator_must_be_terminal_role"
            )

    for field in (
        "automatic_role_switching_status",
        "automatic_route_selection_status",
        "model_invocation_status",
        "prompt_execution_status",
        "runtime_execution_status",
    ):
        if plan.get(field) != "NOT_ALLOWED":
            errors.append(f"{field}_must_be_not_allowed")

    expected_status = _derive_role_plan_status(
        source_status_for_validation
    )

    if plan.get("role_plan_status") not in (
        ROLE_PLAN_STATUSES
    ):
        errors.append("role_plan_status_invalid")
    elif plan.get("role_plan_status") != expected_status:
        errors.append("role_plan_status_mismatch")

    if plan.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if plan.get("roadmap_mode") != ROADMAP_MODE:
        errors.append("roadmap_mode_invalid")

    errors.extend(
        _validate_safety_flags(plan.get("safety_flags"))
    )

    return errors
