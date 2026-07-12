"""Planning-only request envelope for the FCF API Gateway."""

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import (
    ALLOWED_REQUEST_CLASSES,
    APP_ID,
    PLANNING_MODE,
    PROHIBITED_REQUEST_CLASSES,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    validate_fcf_api_gateway_boundary_contract,
)

STAGE_ID = "FCF-API-GATEWAY-PLANNING-D2"
REQUEST_ENVELOPE_VERSION = "1.0.0"

REQUEST_STATUSES = (
    "VALIDATED",
    "BLOCKED",
)

REQUIRED_REQUEST_ENVELOPE_FIELDS = (
    "request_id",
    "app_id",
    "stage_id",
    "request_envelope_version",
    "planning_mode",
    "source_contract_id",
    "request_class",
    "requested_at_utc",
    "correlation_id",
    "policy_version",
    "config_snapshot_id",
    "source_artifact_ids",
    "operator_action",
    "request_status",
    "blocking_reasons",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class FcfApiGatewayRequestEnvelopeViolation(ValueError):
    """Raised when a D2 planning request envelope is invalid."""


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        return False

    return parsed.tzinfo is not None


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _canonical_source_artifact_ids(
    values: object,
) -> list[str]:
    if not isinstance(values, (list, tuple)):
        raise FcfApiGatewayRequestEnvelopeViolation(
            "source_artifact_ids_must_be_sequence"
        )

    if any(not _valid_identifier(value) for value in values):
        raise FcfApiGatewayRequestEnvelopeViolation(
            "source_artifact_id_invalid"
        )

    if len(set(values)) != len(values):
        raise FcfApiGatewayRequestEnvelopeViolation(
            "source_artifact_ids_must_be_unique"
        )

    return sorted(values)


def _derive_request_state(
    request_class: str,
) -> tuple[str, list[str]]:
    if request_class in ALLOWED_REQUEST_CLASSES:
        return "VALIDATED", []

    if request_class in PROHIBITED_REQUEST_CLASSES:
        return "BLOCKED", ["prohibited_request_class"]

    return "BLOCKED", ["request_class_unregistered"]


def build_fcf_api_gateway_request_envelope(
    *,
    boundary_contract: Mapping[str, Any],
    request_id: str,
    request_class: str,
    requested_at_utc: str,
    correlation_id: str,
    policy_version: str,
    config_snapshot_id: str,
    source_artifact_ids: list[str] | tuple[str, ...],
    operator_action: str,
) -> dict[str, Any]:
    """Build a deterministic planning-only API request envelope."""
    contract_errors = (
        validate_fcf_api_gateway_boundary_contract(
            boundary_contract
        )
    )
    if contract_errors:
        raise FcfApiGatewayRequestEnvelopeViolation(
            ";".join(contract_errors)
        )

    identifiers = {
        "request_id": request_id,
        "request_class": request_class,
        "correlation_id": correlation_id,
        "policy_version": policy_version,
        "config_snapshot_id": config_snapshot_id,
        "operator_action": operator_action,
    }

    invalid_identifiers = [
        name
        for name, value in identifiers.items()
        if not _valid_identifier(value)
    ]
    if invalid_identifiers:
        raise FcfApiGatewayRequestEnvelopeViolation(
            ";".join(
                f"{name}_invalid"
                for name in sorted(invalid_identifiers)
            )
        )

    if not _valid_timestamp(requested_at_utc):
        raise FcfApiGatewayRequestEnvelopeViolation(
            "requested_at_utc_invalid"
        )

    canonical_artifact_ids = (
        _canonical_source_artifact_ids(
            source_artifact_ids
        )
    )

    request_status, blocking_reasons = (
        _derive_request_state(request_class)
    )

    return {
        "request_id": request_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "request_envelope_version": REQUEST_ENVELOPE_VERSION,
        "planning_mode": PLANNING_MODE,
        "source_contract_id": boundary_contract["contract_id"],
        "request_class": request_class,
        "requested_at_utc": requested_at_utc,
        "correlation_id": correlation_id,
        "policy_version": policy_version,
        "config_snapshot_id": config_snapshot_id,
        "source_artifact_ids": canonical_artifact_ids,
        "operator_action": operator_action,
        "request_status": request_status,
        "blocking_reasons": blocking_reasons,
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

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )
    if set(value.keys()) != expected_names:
        errors.append(
            "safety_flag_names_must_match_contract"
        )

    return errors


def validate_fcf_api_gateway_request_envelope(
    envelope: object,
) -> list[str]:
    """Return deterministic D2 request-envelope errors."""
    if not isinstance(envelope, Mapping):
        return ["request_envelope_must_be_mapping"]

    errors: list[str] = []

    if set(envelope.keys()) != set(
        REQUIRED_REQUEST_ENVELOPE_FIELDS
    ):
        errors.append(
            "request_envelope_fields_must_match_schema"
        )

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "request_envelope_version": REQUEST_ENVELOPE_VERSION,
        "planning_mode": PLANNING_MODE,
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if envelope.get(field) != expected:
            errors.append(f"{field}_invalid")

    for field in (
        "request_id",
        "source_contract_id",
        "request_class",
        "correlation_id",
        "policy_version",
        "config_snapshot_id",
        "operator_action",
    ):
        if not _valid_identifier(envelope.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_timestamp(
        envelope.get("requested_at_utc")
    ):
        errors.append("requested_at_utc_invalid")

    source_artifact_ids = envelope.get(
        "source_artifact_ids"
    )
    if not isinstance(source_artifact_ids, list):
        errors.append(
            "source_artifact_ids_must_be_list"
        )
    else:
        if any(
            not _valid_identifier(value)
            for value in source_artifact_ids
        ):
            errors.append("source_artifact_id_invalid")

        if source_artifact_ids != sorted(
            set(source_artifact_ids)
        ):
            errors.append(
                "source_artifact_ids_must_be_canonical"
            )

    request_class = envelope.get("request_class")
    if _valid_identifier(request_class):
        expected_status, expected_reasons = (
            _derive_request_state(request_class)
        )

        if envelope.get("request_status") != (
            expected_status
        ):
            errors.append("request_status_invalid")

        if envelope.get("blocking_reasons") != (
            expected_reasons
        ):
            errors.append("blocking_reasons_invalid")

    if envelope.get("request_status") not in (
        REQUEST_STATUSES
    ):
        errors.append("request_status_invalid")

    errors.extend(
        _validate_safety_flags(
            envelope.get("safety_flags")
        )
    )

    return errors
