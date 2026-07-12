
"""Policy and Config Snapshot linkage with review-only handoff."""

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
from .role_contracts import validate_machine_readable_role_contract_manifest
from .routing_eligibility import validate_routing_eligibility_contract
from .runtime_limits import validate_runtime_limit_contract_bundle


STAGE_ID = "AI-ORCHESTRATION-RUNTIME-READINESS-D5"
POLICY_CONFIG_LINK_VERSION = "1.0.0"
READINESS_REVIEW_PACKET_VERSION = "1.0.0"
OPERATOR_HANDOFF_VERSION = "1.0.0"

READINESS_STATUSES = (
    "READY_FOR_OPERATOR_REVIEW",
    "BLOCKED",
    "DEGRADED",
)
REGISTRATION_STATUSES = (
    "VERIFIED",
    "MISSING",
    "MISMATCH",
)
POLICY_CONFIG_POLICY_IDENTIFIERS = (
    "FCF.POLICY.RUNTIME.LINKAGE.CONFIG_DIGEST_REQUIRED",
    "FCF.POLICY.RUNTIME.LINKAGE.CONFIG_VERSION_REQUIRED",
    "FCF.POLICY.RUNTIME.LINKAGE.FAIL_CLOSED_REQUIRED",
    "FCF.POLICY.RUNTIME.LINKAGE.OPERATOR_REVIEW_REQUIRED",
    "FCF.POLICY.RUNTIME.LINKAGE.POLICY_DIGEST_REQUIRED",
    "FCF.POLICY.RUNTIME.LINKAGE.POLICY_VERSION_REQUIRED",
)
ALLOWED_OPERATOR_ACTIONS = (
    "ACKNOWLEDGE_READINESS_PACKET",
    "APPROVE_D6_CLOSEOUT_VALIDATION",
    "REJECT_READINESS_PACKET",
    "REQUEST_REPAIR",
)

REQUIRED_LINK_FIELDS = (
    "link_id",
    "app_id",
    "stage_id",
    "link_version",
    "readiness_mode",
    "source_runtime_limit_bundle_id",
    "source_runtime_limit_bundle_status",
    "policy_identifier",
    "policy_version",
    "policy_digest",
    "policy_registration_status",
    "config_snapshot_id",
    "config_version",
    "config_digest",
    "config_registration_status",
    "policy_identifiers",
    "startup_policy_check_status",
    "pre_workflow_policy_check_status",
    "automatic_policy_activation_status",
    "runtime_enforcement_status",
    "link_status",
    "blocking_reasons",
    "degradation_reasons",
    "operator_review_status",
    "safety_flags",
)

REQUIRED_PACKET_FIELDS = (
    "review_packet_id",
    "app_id",
    "stage_id",
    "review_packet_version",
    "readiness_mode",
    "source_boundary_contract_version",
    "source_role_manifest_id",
    "source_routing_contract_id",
    "source_runtime_limit_bundle_id",
    "source_policy_config_link_id",
    "policy_identifier",
    "policy_version",
    "policy_digest",
    "config_snapshot_id",
    "config_version",
    "config_digest",
    "component_statuses",
    "overall_status",
    "operator_review_status",
    "operator_decision_status",
    "archive_authorization_status",
    "archive_writing_status",
    "automatic_activation_status",
    "model_invocation_status",
    "prompt_execution_status",
    "runtime_execution_status",
    "safety_flags",
)

REQUIRED_HANDOFF_FIELDS = (
    "handoff_id",
    "app_id",
    "stage_id",
    "handoff_version",
    "readiness_mode",
    "source_review_packet_id",
    "overall_status",
    "allowed_operator_actions",
    "operator_action_required",
    "operator_decision_status",
    "manual_archive_authorization_status",
    "automatic_archive_status",
    "archive_writing_status",
    "model_invocation_status",
    "prompt_execution_status",
    "automatic_routing_status",
    "runtime_execution_status",
    "handoff_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class PolicyConfigReviewViolation(ValueError):
    """Raised when D5 readiness linkage or review data is invalid."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _canonical(values: Sequence[str]) -> list[str]:
    return sorted(set(values))


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and item for item in value)
        and value == sorted(set(value))
    )


def _policy_identifiers() -> list[str]:
    return _canonical(
        REQUIRED_POLICY_IDENTIFIERS
        + POLICY_CONFIG_POLICY_IDENTIFIERS
    )


def _derive_status(
    *,
    bundle_status: str,
    policy_status: str,
    config_status: str,
) -> tuple[str, list[str], list[str]]:
    blocked: list[str] = []
    degraded: list[str] = []

    if bundle_status == "BLOCKED":
        blocked.append("runtime_limit_bundle_blocked")
    elif bundle_status == "DEGRADED":
        degraded.append("runtime_limit_bundle_degraded")

    if policy_status == "MISSING":
        blocked.append("policy_registration_missing")
    elif policy_status == "MISMATCH":
        blocked.append("policy_registration_mismatch")

    if config_status == "MISSING":
        blocked.append("config_registration_missing")
    elif config_status == "MISMATCH":
        blocked.append("config_registration_mismatch")

    if blocked:
        return "BLOCKED", _canonical(blocked), _canonical(degraded)
    if degraded:
        return "DEGRADED", [], _canonical(degraded)
    return "READY_FOR_OPERATOR_REVIEW", [], []


def build_policy_config_snapshot_link(
    *,
    link_id: str,
    runtime_limit_bundle: Mapping[str, Any],
    policy_identifier: str,
    policy_version: str,
    policy_digest: str,
    policy_registration_status: str,
    config_snapshot_id: str,
    config_version: str,
    config_digest: str,
    config_registration_status: str,
) -> dict[str, Any]:
    """Build deterministic Policy and Config Snapshot linkage."""
    errors = validate_runtime_limit_contract_bundle(
        runtime_limit_bundle
    )
    if errors:
        raise PolicyConfigReviewViolation(";".join(errors))

    identifiers = (
        link_id,
        policy_identifier,
        policy_version,
        policy_digest,
        config_snapshot_id,
        config_version,
        config_digest,
    )
    if not all(_valid_identifier(value) for value in identifiers):
        raise PolicyConfigReviewViolation("link_identifier_invalid")

    if policy_registration_status not in REGISTRATION_STATUSES:
        raise PolicyConfigReviewViolation(
            "policy_registration_status_invalid"
        )
    if config_registration_status not in REGISTRATION_STATUSES:
        raise PolicyConfigReviewViolation(
            "config_registration_status_invalid"
        )

    bundle_status = str(runtime_limit_bundle["bundle_status"])
    link_status, blocked, degraded = _derive_status(
        bundle_status=bundle_status,
        policy_status=policy_registration_status,
        config_status=config_registration_status,
    )

    return {
        "link_id": link_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "link_version": POLICY_CONFIG_LINK_VERSION,
        "readiness_mode": READINESS_MODE,
        "source_runtime_limit_bundle_id": (
            runtime_limit_bundle["runtime_limit_bundle_id"]
        ),
        "source_runtime_limit_bundle_status": bundle_status,
        "policy_identifier": policy_identifier,
        "policy_version": policy_version,
        "policy_digest": policy_digest,
        "policy_registration_status": policy_registration_status,
        "config_snapshot_id": config_snapshot_id,
        "config_version": config_version,
        "config_digest": config_digest,
        "config_registration_status": config_registration_status,
        "policy_identifiers": _policy_identifiers(),
        "startup_policy_check_status": "PLANNED_NOT_ACTIVE",
        "pre_workflow_policy_check_status": "PLANNED_NOT_ACTIVE",
        "automatic_policy_activation_status": "NOT_ALLOWED",
        "runtime_enforcement_status": "NOT_ACTIVE",
        "link_status": link_status,
        "blocking_reasons": blocked,
        "degradation_reasons": degraded,
        "operator_review_status": "REVIEW_REQUIRED",
        "safety_flags": _safety_flags(),
    }


def _validate_safety(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []
    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")
    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    expected = set(REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS)
    if set(value.keys()) != expected:
        errors.append("safety_flag_names_must_match_contract")
    return errors


def validate_policy_config_snapshot_link(
    link: object,
) -> list[str]:
    """Return deterministic Policy and Config linkage errors."""
    if not isinstance(link, Mapping):
        return ["policy_config_link_must_be_mapping"]

    errors: list[str] = []
    if set(link.keys()) != set(REQUIRED_LINK_FIELDS):
        errors.append("policy_config_link_fields_must_match_schema")

    expected = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "link_version": POLICY_CONFIG_LINK_VERSION,
        "readiness_mode": READINESS_MODE,
        "startup_policy_check_status": "PLANNED_NOT_ACTIVE",
        "pre_workflow_policy_check_status": "PLANNED_NOT_ACTIVE",
        "automatic_policy_activation_status": "NOT_ALLOWED",
        "runtime_enforcement_status": "NOT_ACTIVE",
        "operator_review_status": "REVIEW_REQUIRED",
    }
    for field, value in expected.items():
        if link.get(field) != value:
            errors.append(f"{field}_invalid")

    for field in (
        "link_id",
        "source_runtime_limit_bundle_id",
        "policy_identifier",
        "policy_version",
        "policy_digest",
        "config_snapshot_id",
        "config_version",
        "config_digest",
    ):
        if not _valid_identifier(link.get(field)):
            errors.append(f"{field}_invalid")

    bundle_status = link.get("source_runtime_limit_bundle_status")
    if bundle_status not in (
        "READY_FOR_POLICY_CONFIG_LINKAGE",
        "BLOCKED",
        "DEGRADED",
    ):
        errors.append("source_runtime_limit_bundle_status_invalid")

    policy_status = link.get("policy_registration_status")
    config_status = link.get("config_registration_status")
    if policy_status not in REGISTRATION_STATUSES:
        errors.append("policy_registration_status_invalid")
    if config_status not in REGISTRATION_STATUSES:
        errors.append("config_registration_status_invalid")

    if link.get("policy_identifiers") != _policy_identifiers():
        errors.append("policy_identifiers_invalid")

    for field in ("blocking_reasons", "degradation_reasons"):
        if not _valid_string_list(link.get(field)):
            errors.append(f"{field}_invalid")

    if (
        bundle_status in (
            "READY_FOR_POLICY_CONFIG_LINKAGE",
            "BLOCKED",
            "DEGRADED",
        )
        and policy_status in REGISTRATION_STATUSES
        and config_status in REGISTRATION_STATUSES
    ):
        status, blocked, degraded = _derive_status(
            bundle_status=str(bundle_status),
            policy_status=str(policy_status),
            config_status=str(config_status),
        )
        if link.get("link_status") != status:
            errors.append("link_status_mismatch")
        if link.get("blocking_reasons") != blocked:
            errors.append("blocking_reasons_mismatch")
        if link.get("degradation_reasons") != degraded:
            errors.append("degradation_reasons_mismatch")

    if link.get("link_status") not in READINESS_STATUSES:
        errors.append("link_status_invalid")

    errors.extend(_validate_safety(link.get("safety_flags")))
    return errors


def _overall_status(component_statuses: Mapping[str, str]) -> str:
    values = set(component_statuses.values())
    if "BLOCKED" in values:
        return "BLOCKED"
    if "DEGRADED" in values:
        return "DEGRADED"
    return "READY_FOR_OPERATOR_REVIEW"


def build_runtime_readiness_review_packet(
    *,
    review_packet_id: str,
    boundary_contract: Mapping[str, Any],
    role_manifest: Mapping[str, Any],
    routing_contract: Mapping[str, Any],
    runtime_limit_bundle: Mapping[str, Any],
    policy_config_link: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the deterministic D5 Operator review packet."""
    checks = (
        (
            validate_runtime_readiness_boundary_contract,
            boundary_contract,
        ),
        (
            validate_machine_readable_role_contract_manifest,
            role_manifest,
        ),
        (
            validate_routing_eligibility_contract,
            routing_contract,
        ),
        (
            validate_runtime_limit_contract_bundle,
            runtime_limit_bundle,
        ),
        (
            validate_policy_config_snapshot_link,
            policy_config_link,
        ),
    )
    for validator, artifact in checks:
        errors = validator(artifact)
        if errors:
            raise PolicyConfigReviewViolation(";".join(errors))

    if not _valid_identifier(review_packet_id):
        raise PolicyConfigReviewViolation(
            "review_packet_id_invalid"
        )

    links_valid = (
        role_manifest["source_boundary_contract_version"]
        == boundary_contract["contract_version"]
        and routing_contract["source_role_manifest_id"]
        == role_manifest["manifest_id"]
        and runtime_limit_bundle["source_routing_contract_id"]
        == routing_contract["routing_contract_id"]
        and policy_config_link[
            "source_runtime_limit_bundle_id"
        ]
        == runtime_limit_bundle["runtime_limit_bundle_id"]
    )
    if not links_valid:
        raise PolicyConfigReviewViolation(
            "readiness_chain_linkage_invalid"
        )

    component_statuses = {
        "boundary_contract_status": "VALID",
        "role_manifest_status": str(
            role_manifest["manifest_status"]
        ),
        "routing_contract_status": str(
            routing_contract["routing_contract_status"]
        ),
        "runtime_limit_bundle_status": str(
            runtime_limit_bundle["bundle_status"]
        ),
        "policy_config_link_status": str(
            policy_config_link["link_status"]
        ),
    }

    return {
        "review_packet_id": review_packet_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "review_packet_version": READINESS_REVIEW_PACKET_VERSION,
        "readiness_mode": READINESS_MODE,
        "source_boundary_contract_version": (
            boundary_contract["contract_version"]
        ),
        "source_role_manifest_id": role_manifest["manifest_id"],
        "source_routing_contract_id": (
            routing_contract["routing_contract_id"]
        ),
        "source_runtime_limit_bundle_id": (
            runtime_limit_bundle["runtime_limit_bundle_id"]
        ),
        "source_policy_config_link_id": policy_config_link["link_id"],
        "policy_identifier": policy_config_link["policy_identifier"],
        "policy_version": policy_config_link["policy_version"],
        "policy_digest": policy_config_link["policy_digest"],
        "config_snapshot_id": policy_config_link["config_snapshot_id"],
        "config_version": policy_config_link["config_version"],
        "config_digest": policy_config_link["config_digest"],
        "component_statuses": component_statuses,
        "overall_status": _overall_status(component_statuses),
        "operator_review_status": "REVIEW_REQUIRED",
        "operator_decision_status": "PENDING",
        "archive_authorization_status": "NOT_GRANTED",
        "archive_writing_status": "NOT_ALLOWED",
        "automatic_activation_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "safety_flags": _safety_flags(),
    }


def validate_runtime_readiness_review_packet(
    packet: object,
) -> list[str]:
    """Return deterministic D5 review packet errors."""
    if not isinstance(packet, Mapping):
        return ["review_packet_must_be_mapping"]

    errors: list[str] = []
    if set(packet.keys()) != set(REQUIRED_PACKET_FIELDS):
        errors.append("review_packet_fields_must_match_schema")

    expected = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "review_packet_version": READINESS_REVIEW_PACKET_VERSION,
        "readiness_mode": READINESS_MODE,
        "operator_review_status": "REVIEW_REQUIRED",
        "operator_decision_status": "PENDING",
        "archive_authorization_status": "NOT_GRANTED",
        "archive_writing_status": "NOT_ALLOWED",
        "automatic_activation_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
    }
    for field, value in expected.items():
        if packet.get(field) != value:
            errors.append(f"{field}_invalid")

    for field in (
        "review_packet_id",
        "source_boundary_contract_version",
        "source_role_manifest_id",
        "source_routing_contract_id",
        "source_runtime_limit_bundle_id",
        "source_policy_config_link_id",
        "policy_identifier",
        "policy_version",
        "policy_digest",
        "config_snapshot_id",
        "config_version",
        "config_digest",
    ):
        if not _valid_identifier(packet.get(field)):
            errors.append(f"{field}_invalid")

    component_statuses = packet.get("component_statuses")
    if not isinstance(component_statuses, Mapping):
        errors.append("component_statuses_must_be_mapping")
        component_statuses = {}

    required_components = {
        "boundary_contract_status",
        "role_manifest_status",
        "routing_contract_status",
        "runtime_limit_bundle_status",
        "policy_config_link_status",
    }
    if set(component_statuses.keys()) != required_components:
        errors.append("component_status_fields_must_match_schema")

    expected_status = _overall_status(
        {
            str(key): str(value)
            for key, value in component_statuses.items()
        }
    )
    if packet.get("overall_status") != expected_status:
        errors.append("overall_status_invalid")
    if packet.get("overall_status") not in READINESS_STATUSES:
        errors.append("overall_status_not_supported")

    errors.extend(_validate_safety(packet.get("safety_flags")))
    return errors


def build_operator_handoff(
    *,
    handoff_id: str,
    review_packet: Mapping[str, Any],
) -> dict[str, Any]:
    """Build a manual-only D5 Operator handoff."""
    errors = validate_runtime_readiness_review_packet(
        review_packet
    )
    if errors:
        raise PolicyConfigReviewViolation(";".join(errors))
    if not _valid_identifier(handoff_id):
        raise PolicyConfigReviewViolation("handoff_id_invalid")

    status = str(review_packet["overall_status"])
    return {
        "handoff_id": handoff_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "handoff_version": OPERATOR_HANDOFF_VERSION,
        "readiness_mode": READINESS_MODE,
        "source_review_packet_id": (
            review_packet["review_packet_id"]
        ),
        "overall_status": status,
        "allowed_operator_actions": list(
            ALLOWED_OPERATOR_ACTIONS
        ),
        "operator_action_required": True,
        "operator_decision_status": "PENDING",
        "manual_archive_authorization_status": "NOT_GRANTED",
        "automatic_archive_status": "NOT_ALLOWED",
        "archive_writing_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "handoff_status": status,
        "safety_flags": _safety_flags(),
    }


def validate_operator_handoff(
    handoff: object,
) -> list[str]:
    """Return deterministic D5 Operator handoff errors."""
    if not isinstance(handoff, Mapping):
        return ["operator_handoff_must_be_mapping"]

    errors: list[str] = []
    if set(handoff.keys()) != set(REQUIRED_HANDOFF_FIELDS):
        errors.append("operator_handoff_fields_must_match_schema")

    expected = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "handoff_version": OPERATOR_HANDOFF_VERSION,
        "readiness_mode": READINESS_MODE,
        "operator_action_required": True,
        "operator_decision_status": "PENDING",
        "manual_archive_authorization_status": "NOT_GRANTED",
        "automatic_archive_status": "NOT_ALLOWED",
        "archive_writing_status": "NOT_ALLOWED",
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
    }
    for field, value in expected.items():
        if handoff.get(field) != value:
            errors.append(f"{field}_invalid")

    for field in ("handoff_id", "source_review_packet_id"):
        if not _valid_identifier(handoff.get(field)):
            errors.append(f"{field}_invalid")

    if handoff.get("allowed_operator_actions") != list(
        ALLOWED_OPERATOR_ACTIONS
    ):
        errors.append("allowed_operator_actions_invalid")
    if handoff.get("overall_status") not in READINESS_STATUSES:
        errors.append("overall_status_invalid")
    if handoff.get("handoff_status") != handoff.get(
        "overall_status"
    ):
        errors.append("handoff_status_invalid")

    errors.extend(_validate_safety(handoff.get("safety_flags")))
    return errors
