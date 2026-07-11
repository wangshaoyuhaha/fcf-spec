"""D2 registered source loader and exact version-lock validation."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import apps.ai_comprehensive_report_synthesis_app_1 as synthesis_source

APP_ID = "AI-COMPREHENSIVE-REPORT-INTEGRATION-APP-1"
STAGE = "D2"
SOURCE_APP_ID = "AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1"
SOURCE_MODULE = "apps.ai_comprehensive_report_synthesis_app_1"
SOURCE_ARTIFACT_TYPE = "comprehensive_report_synthesis_packet"

REQUIRED_ENVELOPE_FIELDS = (
    "source_app_id",
    "source_module",
    "source_artifact_type",
    "source_artifact_ref",
    "source_artifact_version",
    "source_sha256",
    "correlation_id",
    "source_payload",
    "operator_review_required",
)

FORBIDDEN_SOURCE_PREFIXES = (
    "http://",
    "https://",
    "ftp://",
    "s3://",
    "gs://",
)


def canonical_payload_sha256(payload: Mapping[str, Any]) -> str:
    """Return a deterministic SHA-256 digest for a mapping payload."""

    encoded = json.dumps(
        payload,
        allow_nan=False,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    return hashlib.sha256(encoded).hexdigest()


def build_registered_source_envelope(
    *,
    source_payload: Mapping[str, Any],
    source_artifact_ref: str,
    source_artifact_version: str,
    correlation_id: str,
) -> dict[str, Any]:
    """Build an immutable-style registered source envelope."""

    payload_copy = deepcopy(dict(source_payload))

    return {
        "source_app_id": SOURCE_APP_ID,
        "source_module": synthesis_source.__name__,
        "source_artifact_type": SOURCE_ARTIFACT_TYPE,
        "source_artifact_ref": source_artifact_ref,
        "source_artifact_version": source_artifact_version,
        "source_sha256": canonical_payload_sha256(payload_copy),
        "correlation_id": correlation_id,
        "source_payload": payload_copy,
        "operator_review_required": True,
    }


def validate_registered_source_envelope(
    envelope: Mapping[str, Any],
    *,
    expected_source_artifact_ref: str | None = None,
    expected_source_artifact_version: str | None = None,
    expected_correlation_id: str | None = None,
    expected_source_sha256: str | None = None,
) -> dict[str, Any]:
    """Validate exact source identity and version locks."""

    errors: list[str] = []

    for field in REQUIRED_ENVELOPE_FIELDS:
        if field not in envelope:
            errors.append(f"MISSING_{field.upper()}")

    if envelope.get("source_app_id") != SOURCE_APP_ID:
        errors.append("INVALID_SOURCE_APP_ID")

    if envelope.get("source_module") != SOURCE_MODULE:
        errors.append("INVALID_SOURCE_MODULE")

    if envelope.get("source_artifact_type") != SOURCE_ARTIFACT_TYPE:
        errors.append("INVALID_SOURCE_ARTIFACT_TYPE")

    source_ref = envelope.get("source_artifact_ref")

    if not isinstance(source_ref, str) or not source_ref.strip():
        errors.append("INVALID_SOURCE_ARTIFACT_REF")
    elif source_ref.lower().startswith(FORBIDDEN_SOURCE_PREFIXES):
        errors.append("NON_LOCAL_SOURCE_ARTIFACT_REF")

    source_version = envelope.get("source_artifact_version")

    if not isinstance(source_version, str) or not source_version.strip():
        errors.append("INVALID_SOURCE_ARTIFACT_VERSION")

    correlation_id = envelope.get("correlation_id")

    if not isinstance(correlation_id, str) or not correlation_id.strip():
        errors.append("INVALID_CORRELATION_ID")

    source_payload = envelope.get("source_payload")

    calculated_sha256: str | None = None

    if not isinstance(source_payload, Mapping):
        errors.append("INVALID_SOURCE_PAYLOAD")
    else:
        try:
            calculated_sha256 = canonical_payload_sha256(source_payload)
        except (TypeError, ValueError):
            errors.append("NON_CANONICAL_SOURCE_PAYLOAD")

    registered_sha256 = envelope.get("source_sha256")

    if (
        not isinstance(registered_sha256, str)
        or len(registered_sha256) != 64
    ):
        errors.append("INVALID_SOURCE_SHA256")
    elif calculated_sha256 is not None:
        if registered_sha256 != calculated_sha256:
            errors.append("SOURCE_SHA256_MISMATCH")

    if envelope.get("operator_review_required") is not True:
        errors.append("OPERATOR_REVIEW_REQUIREMENT_REMOVED")

    if (
        expected_source_artifact_ref is not None
        and source_ref != expected_source_artifact_ref
    ):
        errors.append("SOURCE_ARTIFACT_REF_LOCK_MISMATCH")

    if (
        expected_source_artifact_version is not None
        and source_version != expected_source_artifact_version
    ):
        errors.append("SOURCE_ARTIFACT_VERSION_LOCK_MISMATCH")

    if (
        expected_correlation_id is not None
        and correlation_id != expected_correlation_id
    ):
        errors.append("CORRELATION_ID_LOCK_MISMATCH")

    if (
        expected_source_sha256 is not None
        and registered_sha256 != expected_source_sha256
    ):
        errors.append("SOURCE_SHA256_LOCK_MISMATCH")

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": not errors,
        "errors": sorted(set(errors)),
        "source_app_id": envelope.get("source_app_id"),
        "source_artifact_ref": source_ref,
        "source_artifact_version": source_version,
        "source_sha256": registered_sha256,
        "calculated_source_sha256": calculated_sha256,
        "correlation_id": correlation_id,
        "operator_review_required": True,
        "source_mutation_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def load_registered_source_from_mapping(
    envelope: Mapping[str, Any],
    *,
    expected_source_artifact_ref: str | None = None,
    expected_source_artifact_version: str | None = None,
    expected_correlation_id: str | None = None,
    expected_source_sha256: str | None = None,
) -> dict[str, Any]:
    """Load a registered source mapping without mutating its contents."""

    validation = validate_registered_source_envelope(
        envelope,
        expected_source_artifact_ref=expected_source_artifact_ref,
        expected_source_artifact_version=expected_source_artifact_version,
        expected_correlation_id=expected_correlation_id,
        expected_source_sha256=expected_source_sha256,
    )

    return {
        "app_id": APP_ID,
        "stage": STAGE,
        "ok": validation["ok"],
        "validation": validation,
        "registered_source": (
            deepcopy(dict(envelope))
            if validation["ok"]
            else None
        ),
        "operator_review_required": True,
        "source_mutation_performed": False,
        "archive_execution_performed": False,
        "runtime_execution_performed": False,
        "real_execution_performed": False,
    }


def load_registered_source_from_file(
    source_file: str | Path,
    *,
    expected_source_artifact_ref: str | None = None,
    expected_source_artifact_version: str | None = None,
    expected_correlation_id: str | None = None,
    expected_source_sha256: str | None = None,
) -> dict[str, Any]:
    """Load a local JSON registered source file in read-only mode."""

    path = Path(source_file)

    if not path.is_file():
        return {
            "app_id": APP_ID,
            "stage": STAGE,
            "ok": False,
            "errors": ["SOURCE_FILE_NOT_FOUND"],
            "registered_source": None,
            "operator_review_required": True,
            "source_mutation_performed": False,
            "archive_execution_performed": False,
            "runtime_execution_performed": False,
            "real_execution_performed": False,
        }

    try:
        raw = path.read_text(encoding="utf-8-sig")
        loaded = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return {
            "app_id": APP_ID,
            "stage": STAGE,
            "ok": False,
            "errors": ["INVALID_SOURCE_FILE"],
            "registered_source": None,
            "operator_review_required": True,
            "source_mutation_performed": False,
            "archive_execution_performed": False,
            "runtime_execution_performed": False,
            "real_execution_performed": False,
        }

    if not isinstance(loaded, Mapping):
        return {
            "app_id": APP_ID,
            "stage": STAGE,
            "ok": False,
            "errors": ["SOURCE_FILE_ROOT_NOT_OBJECT"],
            "registered_source": None,
            "operator_review_required": True,
            "source_mutation_performed": False,
            "archive_execution_performed": False,
            "runtime_execution_performed": False,
            "real_execution_performed": False,
        }

    result = load_registered_source_from_mapping(
        loaded,
        expected_source_artifact_ref=expected_source_artifact_ref,
        expected_source_artifact_version=expected_source_artifact_version,
        expected_correlation_id=expected_correlation_id,
        expected_source_sha256=expected_source_sha256,
    )

    result["source_file"] = str(path)
    result["source_file_mode"] = "LOCAL_READ_ONLY_JSON"

    return result
