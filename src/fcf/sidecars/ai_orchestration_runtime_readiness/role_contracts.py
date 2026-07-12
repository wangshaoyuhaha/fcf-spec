"""Machine-readable readiness-only role contracts."""

import re
from typing import Any, Mapping, Sequence

from .contract import (
    APP_ID,
    READINESS_MODE,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_POLICY_IDENTIFIERS,
    REQUIRED_TRUE_FLAGS,
    validate_runtime_readiness_boundary_contract,
)

STAGE_ID = "AI-ORCHESTRATION-RUNTIME-READINESS-D2"
ROLE_CONTRACT_VERSION = "1.0.0"
ROLE_MANIFEST_VERSION = "1.0.0"

ROLE_KINDS = (
    "DETERMINISTIC_COORDINATOR",
    "PLANNED_AI_ROLE",
    "HUMAN_OPERATOR",
)

ROLE_AUTHORITIES = (
    "COORDINATION_ONLY",
    "ADVISORY_ONLY",
    "FINAL_MANUAL_REVIEW",
)

ROLE_STATUSES = (
    "READY_FOR_POLICY_EVALUATION",
    "BLOCKED",
    "DEGRADED",
)

ROLE_POLICY_IDENTIFIERS = (
    "FCF.POLICY.RUNTIME.ROLE.CONTRACT_REQUIRED",
    "FCF.POLICY.RUNTIME.ROLE.NO_AUTHORITY_ESCALATION",
    "FCF.POLICY.RUNTIME.ROLE.OUTPUT_OWNERSHIP_REQUIRED",
)

TERMINAL_OPERATOR_ROLE_ID = "human_operator"

ROLE_DEFINITIONS = (
    {
        "role_id": "runtime_orchestration_coordinator",
        "role_kind": "DETERMINISTIC_COORDINATOR",
        "authority": "COORDINATION_ONLY",
        "responsibility": (
            "Prepare deterministic readiness metadata without selecting "
            "models, Prompts, routes, conclusions, or actions."
        ),
        "allowed_input_artifact_types": (
            "RUNTIME_READINESS_BOUNDARY_CONTRACT",
            "REGISTERED_AI_ORCHESTRATION_ROADMAP_ARTIFACT",
            "REGISTERED_CONFIG_SNAPSHOT_REFERENCE",
            "REGISTERED_POLICY_REFERENCE",
        ),
        "planned_output_artifact_types": (
            "MACHINE_READABLE_ROLE_CONTRACT_MANIFEST",
        ),
    },
    {
        "role_id": "market_narrative_context_analyst",
        "role_kind": "PLANNED_AI_ROLE",
        "authority": "ADVISORY_ONLY",
        "responsibility": (
            "Review registered market narrative and context evidence "
            "without determining truth or changing deterministic outputs."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_CONTEXT_ARTIFACT",
            "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
            "REGISTERED_POLICY_REFERENCE",
        ),
        "planned_output_artifact_types": (
            "PLANNED_NARRATIVE_CONTEXT_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": "causal_reasoning_analyst",
        "role_kind": "PLANNED_AI_ROLE",
        "authority": "ADVISORY_ONLY",
        "responsibility": (
            "Review registered causal reasoning evidence without assigning "
            "authoritative probability, ranking, or portfolio weight."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_CAUSAL_REASONING_ARTIFACT",
            "REGISTERED_AI_CONTEXT_ARTIFACT",
            "REGISTERED_POLICY_REFERENCE",
        ),
        "planned_output_artifact_types": (
            "PLANNED_CAUSAL_REASONING_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": "contrarian_challenge_reviewer",
        "role_kind": "PLANNED_AI_ROLE",
        "authority": "ADVISORY_ONLY",
        "responsibility": (
            "Review contradictions, counterarguments, risk flags, and "
            "evidence gaps without replacing conclusions."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_CAUSAL_REASONING_ARTIFACT",
            "REGISTERED_AI_CHALLENGE_ARTIFACT",
            "REGISTERED_POLICY_REFERENCE",
        ),
        "planned_output_artifact_types": (
            "PLANNED_CONTRARIAN_CHALLENGE_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": "comprehensive_report_synthesizer",
        "role_kind": "PLANNED_AI_ROLE",
        "authority": "ADVISORY_ONLY",
        "responsibility": (
            "Prepare a review-only synthesis from registered evidence "
            "without creating authoritative scores, weights, or actions."
        ),
        "allowed_input_artifact_types": (
            "REGISTERED_AI_CAUSAL_REASONING_ARTIFACT",
            "REGISTERED_AI_CHALLENGE_ARTIFACT",
            "REGISTERED_AI_COMPREHENSIVE_REPORT_ARTIFACT",
            "REGISTERED_MARKET_NARRATIVE_ARTIFACT",
            "REGISTERED_POLICY_REFERENCE",
        ),
        "planned_output_artifact_types": (
            "PLANNED_COMPREHENSIVE_REPORT_REVIEW_ARTIFACT",
        ),
    },
    {
        "role_id": TERMINAL_OPERATOR_ROLE_ID,
        "role_kind": "HUMAN_OPERATOR",
        "authority": "FINAL_MANUAL_REVIEW",
        "responsibility": (
            "Perform final manual review and decide whether separately "
            "approved future work may proceed."
        ),
        "allowed_input_artifact_types": (
            "MACHINE_READABLE_ROLE_CONTRACT_MANIFEST",
            "PLANNED_CAUSAL_REASONING_REVIEW_ARTIFACT",
            "PLANNED_COMPREHENSIVE_REPORT_REVIEW_ARTIFACT",
            "PLANNED_CONTRARIAN_CHALLENGE_REVIEW_ARTIFACT",
            "PLANNED_NARRATIVE_CONTEXT_REVIEW_ARTIFACT",
            "REGISTERED_CONFIG_SNAPSHOT_REFERENCE",
            "REGISTERED_POLICY_REFERENCE",
        ),
        "planned_output_artifact_types": (
            "PLANNED_OPERATOR_READINESS_DECISION_RECORD",
        ),
    },
)

REQUIRED_ROLE_FIELDS = (
    "role_id",
    "role_kind",
    "authority",
    "responsibility",
    "allowed_input_artifact_types",
    "planned_output_artifact_types",
    "required_policy_identifiers",
    "sequence_index",
    "operator_gate_required",
    "model_invocation_status",
    "prompt_execution_status",
    "automatic_routing_status",
    "automatic_activation_status",
    "archive_writing_status",
    "runtime_execution_status",
    "role_status",
    "safety_flags",
)

REQUIRED_OUTPUT_OWNERSHIP_FIELDS = (
    "output_artifact_type",
    "owner_role_id",
)

REQUIRED_MANIFEST_FIELDS = (
    "manifest_id",
    "app_id",
    "stage_id",
    "role_contract_version",
    "role_manifest_version",
    "source_boundary_contract_version",
    "readiness_mode",
    "roles",
    "output_ownership",
    "terminal_operator_role_id",
    "policy_identifiers",
    "config_snapshot_linkage_status",
    "automatic_routing_status",
    "model_invocation_status",
    "prompt_execution_status",
    "archive_writing_status",
    "runtime_execution_status",
    "manifest_status",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class RoleContractViolation(ValueError):
    """Raised when a readiness-only role contract is invalid."""


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


def _role_policy_identifiers() -> list[str]:
    return _canonical_strings(
        REQUIRED_POLICY_IDENTIFIERS + ROLE_POLICY_IDENTIFIERS
    )


def _build_roles() -> list[dict[str, Any]]:
    roles: list[dict[str, Any]] = []

    for sequence_index, definition in enumerate(
        ROLE_DEFINITIONS,
        start=1,
    ):
        roles.append(
            {
                "role_id": definition["role_id"],
                "role_kind": definition["role_kind"],
                "authority": definition["authority"],
                "responsibility": definition["responsibility"],
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
                "required_policy_identifiers": (
                    _role_policy_identifiers()
                ),
                "sequence_index": sequence_index,
                "operator_gate_required": True,
                "model_invocation_status": "NOT_ALLOWED",
                "prompt_execution_status": "NOT_ALLOWED",
                "automatic_routing_status": "NOT_ALLOWED",
                "automatic_activation_status": "NOT_ALLOWED",
                "archive_writing_status": "NOT_ALLOWED",
                "runtime_execution_status": "NOT_ALLOWED",
                "role_status": "READY_FOR_POLICY_EVALUATION",
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
    cloned["required_policy_identifiers"] = list(
        role["required_policy_identifiers"]
    )
    cloned["safety_flags"] = dict(role["safety_flags"])
    return cloned


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


def build_machine_readable_role_contract_manifest(
    *,
    manifest_id: str,
    boundary_contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Build deterministic non-executable D2 role contracts."""
    boundary_errors = (
        validate_runtime_readiness_boundary_contract(
            boundary_contract
        )
    )
    if boundary_errors:
        raise RoleContractViolation(
            ";".join(boundary_errors)
        )

    if not _valid_identifier(manifest_id):
        raise RoleContractViolation("manifest_id_invalid")

    roles = [
        _clone_role(role)
        for role in _build_roles()
    ]

    return {
        "manifest_id": manifest_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "role_contract_version": ROLE_CONTRACT_VERSION,
        "role_manifest_version": ROLE_MANIFEST_VERSION,
        "source_boundary_contract_version": (
            boundary_contract["contract_version"]
        ),
        "readiness_mode": READINESS_MODE,
        "roles": roles,
        "output_ownership": _output_ownership(roles),
        "terminal_operator_role_id": (
            TERMINAL_OPERATOR_ROLE_ID
        ),
        "policy_identifiers": _role_policy_identifiers(),
        "config_snapshot_linkage_status": (
            "REQUIRED_NOT_ACTIVE"
        ),
        "automatic_routing_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "archive_writing_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "manifest_status": (
            "READY_FOR_ROUTING_ELIGIBILITY_CONTRACT"
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


def _validate_role(
    role: object,
    sequence_index: int,
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

    if role.get("authority") not in ROLE_AUTHORITIES:
        errors.append("role_authority_invalid")

    responsibility = role.get("responsibility")
    if not isinstance(responsibility, str) or not responsibility.strip():
        errors.append("responsibility_invalid")

    if role.get("sequence_index") != sequence_index:
        errors.append("sequence_index_invalid")

    for field in (
        "allowed_input_artifact_types",
        "planned_output_artifact_types",
        "required_policy_identifiers",
    ):
        if not _valid_canonical_string_list(
            role.get(field)
        ):
            errors.append(f"{field}_invalid")

    if role.get("required_policy_identifiers") != (
        _role_policy_identifiers()
    ):
        errors.append(
            "required_policy_identifiers_invalid"
        )

    if role.get("operator_gate_required") is not True:
        errors.append(
            "operator_gate_required_must_be_true"
        )

    for field in (
        "model_invocation_status",
        "prompt_execution_status",
        "automatic_routing_status",
        "automatic_activation_status",
        "archive_writing_status",
        "runtime_execution_status",
    ):
        if role.get(field) != "NOT_ALLOWED":
            errors.append(f"{field}_invalid")

    if role.get("role_status") not in ROLE_STATUSES:
        errors.append("role_status_invalid")

    if (
        role.get("role_kind") == "PLANNED_AI_ROLE"
        and role.get("authority") != "ADVISORY_ONLY"
    ):
        errors.append("planned_ai_role_authority_invalid")

    if (
        role.get("role_kind")
        == "DETERMINISTIC_COORDINATOR"
        and role.get("authority") != "COORDINATION_ONLY"
    ):
        errors.append("coordinator_authority_invalid")

    if (
        role.get("role_kind") == "HUMAN_OPERATOR"
        and role.get("authority") != "FINAL_MANUAL_REVIEW"
    ):
        errors.append("human_operator_authority_invalid")

    errors.extend(
        _validate_safety_flags(role.get("safety_flags"))
    )

    return errors


def validate_machine_readable_role_contract_manifest(
    manifest: object,
) -> list[str]:
    """Return deterministic D2 role contract errors."""
    if not isinstance(manifest, Mapping):
        return ["manifest_must_be_mapping"]

    errors: list[str] = []

    if set(manifest.keys()) != set(REQUIRED_MANIFEST_FIELDS):
        errors.append("manifest_fields_must_match_schema")

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "role_contract_version": ROLE_CONTRACT_VERSION,
        "role_manifest_version": ROLE_MANIFEST_VERSION,
        "readiness_mode": READINESS_MODE,
        "terminal_operator_role_id": (
            TERMINAL_OPERATOR_ROLE_ID
        ),
        "config_snapshot_linkage_status": (
            "REQUIRED_NOT_ACTIVE"
        ),
        "automatic_routing_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "archive_writing_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "manifest_status": (
            "READY_FOR_ROUTING_ELIGIBILITY_CONTRACT"
        ),
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if manifest.get(field) != expected:
            errors.append(f"{field}_invalid")

    if not _valid_identifier(manifest.get("manifest_id")):
        errors.append("manifest_id_invalid")

    if not _valid_identifier(
        manifest.get("source_boundary_contract_version")
    ):
        errors.append(
            "source_boundary_contract_version_invalid"
        )

    if manifest.get("policy_identifiers") != (
        _role_policy_identifiers()
    ):
        errors.append("policy_identifiers_invalid")

    roles = manifest.get("roles")
    if not isinstance(roles, list) or not roles:
        errors.append("roles_must_be_non_empty_list")
        roles = []

    role_ids: list[str] = []

    for sequence_index, role in enumerate(
        roles,
        start=1,
    ):
        errors.extend(
            _validate_role(role, sequence_index)
        )
        if (
            isinstance(role, Mapping)
            and isinstance(role.get("role_id"), str)
        ):
            role_ids.append(role["role_id"])

    if len(role_ids) != len(set(role_ids)):
        errors.append("role_ids_must_be_unique")

    if (
        role_ids
        and role_ids[-1] != TERMINAL_OPERATOR_ROLE_ID
    ):
        errors.append("human_operator_must_be_terminal_role")

    ownership = manifest.get("output_ownership")
    if not isinstance(ownership, list):
        errors.append("output_ownership_must_be_list")
        ownership = []

    owned_output_types: list[str] = []

    for item in ownership:
        if not isinstance(item, Mapping):
            errors.append(
                "output_ownership_item_must_be_mapping"
            )
            continue

        if set(item.keys()) != set(
            REQUIRED_OUTPUT_OWNERSHIP_FIELDS
        ):
            errors.append(
                "output_ownership_fields_must_match_schema"
            )

        if not _valid_identifier(
            item.get("output_artifact_type")
        ):
            errors.append("output_artifact_type_invalid")

        if item.get("owner_role_id") not in role_ids:
            errors.append("output_owner_role_id_invalid")

        if isinstance(
            item.get("output_artifact_type"),
            str,
        ):
            owned_output_types.append(
                item["output_artifact_type"]
            )

    if len(owned_output_types) != len(
        set(owned_output_types)
    ):
        errors.append(
            "output_artifact_ownership_must_be_unique"
        )

    expected_ownership = _output_ownership(
        [
            role
            for role in roles
            if isinstance(role, Mapping)
        ]
    )

    if ownership != expected_ownership:
        errors.append("output_ownership_invalid")

    errors.extend(
        _validate_safety_flags(
            manifest.get("safety_flags")
        )
    )

    return errors