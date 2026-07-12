"""Planning-only normalized data envelope contract."""

import re
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .contract import (
    APP_ID,
    PLANNING_MODE,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    validate_read_only_data_gateway_boundary_contract,
)

STAGE_ID = "READ-ONLY-DATA-GATEWAY-PLANNING-D2"
ENVELOPE_VERSION = "1.0.0"

SOURCE_CLASSES = ("A", "B", "C", "UNKNOWN")
TRUST_LEVELS = ("HIGH", "MEDIUM", "LOW", "UNKNOWN")
FRESHNESS_STATUSES = ("FRESH", "AGING", "STALE", "UNKNOWN")
LICENSE_TYPES = ("PUBLIC", "LICENSED", "RESTRICTED", "UNKNOWN")
ALLOWED_USE_STATUSES = ("ALLOWED", "RESTRICTED", "PROHIBITED")
NORMALIZATION_STATUSES = ("VALIDATED", "DEGRADED", "BLOCKED")
CREDENTIAL_SCAN_STATUSES = ("CLEAR", "DETECTED", "NOT_RUN")
ENVELOPE_STATUSES = (
    "READY_FOR_D3_SOURCE_POLICY",
    "DEGRADED",
    "BLOCKED",
)

REQUIRED_ENVELOPE_FIELDS = (
    "envelope_id",
    "app_id",
    "stage_id",
    "envelope_version",
    "planning_mode",
    "source_contract_id",
    "source_id",
    "source_class",
    "trust_level",
    "published_at",
    "retrieved_at",
    "evidence_id",
    "checksum",
    "freshness_status",
    "license_type",
    "allowed_use",
    "cloud_processing_allowed",
    "retention_period",
    "redistribution_allowed",
    "training_allowed",
    "data_format",
    "payload_reference",
    "normalization_status",
    "credential_scan_status",
    "blocking_reasons",
    "degradation_reasons",
    "gateway_status",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)
_CHECKSUM_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")


class NormalizedDataEnvelopeViolation(ValueError):
    """Raised when a D2 normalized envelope is invalid."""


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


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed


def _valid_timestamp(value: Any) -> bool:
    return _parse_timestamp(value) is not None


def _canonical_reasons(values: list[str]) -> list[str]:
    return sorted(set(values))


def _derive_status(
    *,
    source_class: str,
    trust_level: str,
    freshness_status: str,
    license_type: str,
    allowed_use: str,
    normalization_status: str,
    credential_scan_status: str,
) -> tuple[str, list[str], list[str]]:
    blocked: list[str] = []
    degraded: list[str] = []

    if credential_scan_status == "DETECTED":
        blocked.append("credential_detected")
    elif credential_scan_status == "NOT_RUN":
        blocked.append("credential_scan_not_run")

    if allowed_use == "PROHIBITED":
        blocked.append("source_use_prohibited")

    if normalization_status == "BLOCKED":
        blocked.append("normalization_blocked")
    elif normalization_status == "DEGRADED":
        degraded.append("normalization_degraded")

    if source_class == "UNKNOWN":
        degraded.append("source_class_unknown")
    if trust_level == "UNKNOWN":
        degraded.append("source_trust_unknown")
    if freshness_status == "UNKNOWN":
        degraded.append("freshness_unknown")
    elif freshness_status == "STALE":
        degraded.append("freshness_stale")
    if license_type == "UNKNOWN":
        degraded.append("license_unknown")
    if allowed_use == "RESTRICTED":
        degraded.append("source_use_restricted")

    blocked = _canonical_reasons(blocked)
    degraded = _canonical_reasons(degraded)

    if blocked:
        return "BLOCKED", blocked, degraded
    if degraded:
        return "DEGRADED", [], degraded
    return "READY_FOR_D3_SOURCE_POLICY", [], []


def build_normalized_data_envelope(
    *,
    envelope_id: str,
    boundary_contract: Mapping[str, Any],
    source_id: str,
    source_class: str,
    trust_level: str,
    published_at: str,
    retrieved_at: str,
    evidence_id: str,
    checksum: str,
    freshness_status: str,
    license_type: str,
    allowed_use: str,
    cloud_processing_allowed: bool,
    retention_period: str,
    redistribution_allowed: bool,
    training_allowed: bool,
    data_format: str,
    payload_reference: str,
    normalization_status: str = "VALIDATED",
    credential_scan_status: str = "CLEAR",
) -> dict[str, Any]:
    """Build a deterministic metadata-only normalized envelope."""
    contract_errors = (
        validate_read_only_data_gateway_boundary_contract(
            boundary_contract
        )
    )
    if contract_errors:
        raise NormalizedDataEnvelopeViolation(
            ";".join(contract_errors)
        )

    identifiers = {
        "envelope_id": envelope_id,
        "source_id": source_id,
        "evidence_id": evidence_id,
        "data_format": data_format,
        "payload_reference": payload_reference,
        "retention_period": retention_period,
    }
    invalid_identifiers = [
        name
        for name, value in identifiers.items()
        if not _valid_identifier(value)
    ]
    if invalid_identifiers:
        raise NormalizedDataEnvelopeViolation(
            ";".join(
                f"{name}_invalid"
                for name in sorted(invalid_identifiers)
            )
        )

    if _CHECKSUM_PATTERN.fullmatch(checksum) is None:
        raise NormalizedDataEnvelopeViolation("checksum_invalid")
    if not _valid_timestamp(published_at):
        raise NormalizedDataEnvelopeViolation("published_at_invalid")
    if not _valid_timestamp(retrieved_at):
        raise NormalizedDataEnvelopeViolation("retrieved_at_invalid")
    published_timestamp = _parse_timestamp(published_at)
    retrieved_timestamp = _parse_timestamp(retrieved_at)
    if (
        published_timestamp is not None
        and retrieved_timestamp is not None
        and retrieved_timestamp < published_timestamp
    ):
        raise NormalizedDataEnvelopeViolation(
            "retrieved_at_before_published_at"
        )

    enums = {
        "source_class": (source_class, SOURCE_CLASSES),
        "trust_level": (trust_level, TRUST_LEVELS),
        "freshness_status": (
            freshness_status,
            FRESHNESS_STATUSES,
        ),
        "license_type": (license_type, LICENSE_TYPES),
        "allowed_use": (allowed_use, ALLOWED_USE_STATUSES),
        "normalization_status": (
            normalization_status,
            NORMALIZATION_STATUSES,
        ),
        "credential_scan_status": (
            credential_scan_status,
            CREDENTIAL_SCAN_STATUSES,
        ),
    }
    invalid_enums = [
        name
        for name, (value, allowed) in enums.items()
        if value not in allowed
    ]
    if invalid_enums:
        raise NormalizedDataEnvelopeViolation(
            ";".join(
                f"{name}_invalid"
                for name in sorted(invalid_enums)
            )
        )

    for name, value in {
        "cloud_processing_allowed": cloud_processing_allowed,
        "redistribution_allowed": redistribution_allowed,
        "training_allowed": training_allowed,
    }.items():
        if not isinstance(value, bool):
            raise NormalizedDataEnvelopeViolation(
                f"{name}_must_be_boolean"
            )

    (
        gateway_status,
        blocking_reasons,
        degradation_reasons,
    ) = _derive_status(
        source_class=source_class,
        trust_level=trust_level,
        freshness_status=freshness_status,
        license_type=license_type,
        allowed_use=allowed_use,
        normalization_status=normalization_status,
        credential_scan_status=credential_scan_status,
    )

    return {
        "envelope_id": envelope_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "envelope_version": ENVELOPE_VERSION,
        "planning_mode": PLANNING_MODE,
        "source_contract_id": boundary_contract["contract_id"],
        "source_id": source_id,
        "source_class": source_class,
        "trust_level": trust_level,
        "published_at": published_at,
        "retrieved_at": retrieved_at,
        "evidence_id": evidence_id,
        "checksum": checksum,
        "freshness_status": freshness_status,
        "license_type": license_type,
        "allowed_use": allowed_use,
        "cloud_processing_allowed": cloud_processing_allowed,
        "retention_period": retention_period,
        "redistribution_allowed": redistribution_allowed,
        "training_allowed": training_allowed,
        "data_format": data_format,
        "payload_reference": payload_reference,
        "normalization_status": normalization_status,
        "credential_scan_status": credential_scan_status,
        "blocking_reasons": blocking_reasons,
        "degradation_reasons": degradation_reasons,
        "gateway_status": gateway_status,
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


def validate_normalized_data_envelope(
    envelope: object,
) -> list[str]:
    """Return deterministic D2 envelope validation errors."""
    if not isinstance(envelope, Mapping):
        return ["envelope_must_be_mapping"]

    errors: list[str] = []

    if set(envelope.keys()) != set(REQUIRED_ENVELOPE_FIELDS):
        errors.append("envelope_fields_must_match_schema")

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "envelope_version": ENVELOPE_VERSION,
        "planning_mode": PLANNING_MODE,
        "operator_review_status": "REVIEW_REQUIRED",
    }
    for field, expected in expected_scalars.items():
        if envelope.get(field) != expected:
            errors.append(f"{field}_invalid")

    for field in (
        "envelope_id",
        "source_contract_id",
        "source_id",
        "evidence_id",
        "data_format",
        "payload_reference",
        "retention_period",
    ):
        if not _valid_identifier(envelope.get(field)):
            errors.append(f"{field}_invalid")

    checksum = envelope.get("checksum")
    if (
        not isinstance(checksum, str)
        or _CHECKSUM_PATTERN.fullmatch(checksum) is None
    ):
        errors.append("checksum_invalid")

    for field in ("published_at", "retrieved_at"):
        if not _valid_timestamp(envelope.get(field)):
            errors.append(f"{field}_invalid")

    published = envelope.get("published_at")
    retrieved = envelope.get("retrieved_at")
    published_timestamp = _parse_timestamp(published)
    retrieved_timestamp = _parse_timestamp(retrieved)
    if (
        published_timestamp is not None
        and retrieved_timestamp is not None
        and retrieved_timestamp < published_timestamp
    ):
        errors.append("retrieved_at_before_published_at")

    enums = {
        "source_class": SOURCE_CLASSES,
        "trust_level": TRUST_LEVELS,
        "freshness_status": FRESHNESS_STATUSES,
        "license_type": LICENSE_TYPES,
        "allowed_use": ALLOWED_USE_STATUSES,
        "normalization_status": NORMALIZATION_STATUSES,
        "credential_scan_status": CREDENTIAL_SCAN_STATUSES,
        "gateway_status": ENVELOPE_STATUSES,
    }
    for field, allowed in enums.items():
        if envelope.get(field) not in allowed:
            errors.append(f"{field}_invalid")

    for field in (
        "cloud_processing_allowed",
        "redistribution_allowed",
        "training_allowed",
    ):
        if not isinstance(envelope.get(field), bool):
            errors.append(f"{field}_must_be_boolean")

    for field in ("blocking_reasons", "degradation_reasons"):
        value = envelope.get(field)
        if (
            not isinstance(value, list)
            or not all(
                isinstance(item, str) and item
                for item in value
            )
            or value != sorted(set(value))
        ):
            errors.append(f"{field}_invalid")

    status_inputs_valid = all(
        envelope.get(field) in allowed
        for field, allowed in {
            "source_class": SOURCE_CLASSES,
            "trust_level": TRUST_LEVELS,
            "freshness_status": FRESHNESS_STATUSES,
            "license_type": LICENSE_TYPES,
            "allowed_use": ALLOWED_USE_STATUSES,
            "normalization_status": NORMALIZATION_STATUSES,
            "credential_scan_status": CREDENTIAL_SCAN_STATUSES,
        }.items()
    )

    if status_inputs_valid:
        expected_status, expected_blocked, expected_degraded = (
            _derive_status(
                source_class=str(envelope["source_class"]),
                trust_level=str(envelope["trust_level"]),
                freshness_status=str(
                    envelope["freshness_status"]
                ),
                license_type=str(envelope["license_type"]),
                allowed_use=str(envelope["allowed_use"]),
                normalization_status=str(
                    envelope["normalization_status"]
                ),
                credential_scan_status=str(
                    envelope["credential_scan_status"]
                ),
            )
        )
        if envelope.get("gateway_status") != expected_status:
            errors.append("gateway_status_mismatch")
        if envelope.get("blocking_reasons") != expected_blocked:
            errors.append("blocking_reasons_mismatch")
        if (
            envelope.get("degradation_reasons")
            != expected_degraded
        ):
            errors.append("degradation_reasons_mismatch")

    errors.extend(
        _validate_safety_flags(envelope.get("safety_flags"))
    )
    return errors
