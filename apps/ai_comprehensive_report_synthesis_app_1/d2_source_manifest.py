from __future__ import annotations

import re
from copy import deepcopy
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping, Sequence

APP_ID = "AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1"
SOURCE_SCHEMA_VERSION = "1.0.0"
MANIFEST_SCHEMA_VERSION = "1.0.0"

ALLOWED_ARTIFACT_TYPES = (
    "MARKET_NARRATIVE_CONTEXT",
    "CAUSAL_REASONING_CHAIN",
    "CONTRARIAN_CHALLENGE",
    "SCENARIO_SIMULATION",
    "AI_EVALUATION_EVIDENCE",
    "VALIDATION_BASELINE",
    "PROMPT_MODEL_VERSION_REGISTRY",
    "ARCHIVE_CORRELATION_ROLLUP",
    "OPERATOR_REVIEW",
)

REQUIRED_ARTIFACT_TYPES = (
    "MARKET_NARRATIVE_CONTEXT",
    "CAUSAL_REASONING_CHAIN",
    "CONTRARIAN_CHALLENGE",
    "SCENARIO_SIMULATION",
    "AI_EVALUATION_EVIDENCE",
    "VALIDATION_BASELINE",
)

ALLOWED_CONCLUSION_STATES = {
    "PRESERVED",
    "UNDETERMINED",
    "REVIEW_REQUIRED",
    "NOT_APPLICABLE",
}

ALLOWED_VALIDATION_STATES = {
    "VALIDATED",
    "REVIEW_REQUIRED",
    "BLOCKED",
}

ALLOWED_REQUIREMENT_LEVELS = {
    "REQUIRED",
    "OPTIONAL",
}

SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

SOURCE_RECORD_KEYS = {
    "record_type",
    "schema_version",
    "artifact_id",
    "artifact_type",
    "artifact_version",
    "correlation_id",
    "research_run_id",
    "source_stage_id",
    "source_path",
    "locked_sha256",
    "source_conclusion_state",
    "validation_state",
    "requirement_level",
    "source_artifact_preserved",
    "original_conclusion_preserved",
    "operator_review_required",
}

MANIFEST_KEYS = {
    "manifest_type",
    "schema_version",
    "app_id",
    "manifest_id",
    "status",
    "correlation_id",
    "research_run_id",
    "required_artifact_types",
    "source_count",
    "sources",
    "version_locks",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "operator_review_required",
    "report_synthesis_started",
}


class SourceRecordViolation(ValueError):
    """Raised when a registered source artifact record is invalid."""


class ManifestViolation(ValueError):
    """Raised when a source manifest or version lock is invalid."""


def _require_non_empty_string(
    field_name: str,
    value: object,
    errors: list[str],
) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field_name} must be a non-empty string")


def _normalize_repo_path(source_path: str) -> str:
    normalized = source_path.replace("\\", "/").strip()

    if not normalized:
        raise ValueError("source_path must be a non-empty repository path")

    if re.match(r"^[A-Za-z]:", normalized):
        raise ValueError("source_path must not contain a drive prefix")

    path = PurePosixPath(normalized)

    if path.is_absolute():
        raise ValueError("source_path must be repository-relative")

    if ".." in path.parts:
        raise ValueError("source_path must not traverse parent directories")

    if not path.parts:
        raise ValueError("source_path must be a non-empty repository path")

    if path.parts[0].lower() == "runtime":
        raise ValueError("runtime artifacts are not registered source truth")

    return path.as_posix()


def build_source_record(
    *,
    artifact_id: str,
    artifact_type: str,
    artifact_version: str,
    correlation_id: str,
    research_run_id: str,
    source_stage_id: str,
    source_path: str,
    locked_sha256: str,
    source_conclusion_state: str,
    validation_state: str,
    requirement_level: str,
) -> dict[str, Any]:
    """Build one immutable registered source artifact record."""

    record = {
        "record_type": "REGISTERED_SOURCE_ARTIFACT",
        "schema_version": SOURCE_SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "artifact_version": artifact_version,
        "correlation_id": correlation_id,
        "research_run_id": research_run_id,
        "source_stage_id": source_stage_id,
        "source_path": _normalize_repo_path(source_path),
        "locked_sha256": locked_sha256,
        "source_conclusion_state": source_conclusion_state,
        "validation_state": validation_state,
        "requirement_level": requirement_level,
        "source_artifact_preserved": True,
        "original_conclusion_preserved": True,
        "operator_review_required": True,
    }

    require_valid_source_record(record)
    return record


def validate_source_record(
    record: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic validation errors for one source record."""

    errors: list[str] = []

    missing = sorted(SOURCE_RECORD_KEYS - set(record))
    unexpected = sorted(set(record) - SOURCE_RECORD_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    if record.get("record_type") != "REGISTERED_SOURCE_ARTIFACT":
        errors.append(
            "record_type must be 'REGISTERED_SOURCE_ARTIFACT'"
        )

    if record.get("schema_version") != SOURCE_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {SOURCE_SCHEMA_VERSION!r}"
        )

    string_fields = (
        "artifact_id",
        "artifact_version",
        "correlation_id",
        "research_run_id",
        "source_stage_id",
        "source_path",
    )

    for field_name in string_fields:
        _require_non_empty_string(
            field_name,
            record.get(field_name),
            errors,
        )

    artifact_type = record.get("artifact_type")
    if artifact_type not in ALLOWED_ARTIFACT_TYPES:
        errors.append(
            f"artifact_type must be one of {ALLOWED_ARTIFACT_TYPES!r}"
        )

    conclusion_state = record.get("source_conclusion_state")
    if conclusion_state not in ALLOWED_CONCLUSION_STATES:
        errors.append(
            "source_conclusion_state is not registered"
        )

    validation_state = record.get("validation_state")
    if validation_state not in ALLOWED_VALIDATION_STATES:
        errors.append("validation_state is not registered")

    requirement_level = record.get("requirement_level")
    if requirement_level not in ALLOWED_REQUIREMENT_LEVELS:
        errors.append("requirement_level is not registered")

    if (
        artifact_type in REQUIRED_ARTIFACT_TYPES
        and requirement_level != "REQUIRED"
    ):
        errors.append(
            "required artifact types must use requirement_level 'REQUIRED'"
        )

    locked_sha256 = record.get("locked_sha256")
    if (
        not isinstance(locked_sha256, str)
        or not SHA256_PATTERN.fullmatch(locked_sha256)
    ):
        errors.append(
            "locked_sha256 must be a lowercase 64-character SHA-256 value"
        )

    source_path = record.get("source_path")
    if isinstance(source_path, str):
        try:
            normalized_path = _normalize_repo_path(source_path)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if normalized_path != source_path:
                errors.append(
                    "source_path must already use normalized POSIX form"
                )

    required_true_fields = (
        "source_artifact_preserved",
        "original_conclusion_preserved",
        "operator_review_required",
    )

    for field_name in required_true_fields:
        if record.get(field_name) is not True:
            errors.append(f"{field_name} must be True")

    return tuple(errors)


def require_valid_source_record(
    record: Mapping[str, object],
) -> Mapping[str, object]:
    """Require a valid source record without mutating it."""

    errors = validate_source_record(record)

    if errors:
        raise SourceRecordViolation("; ".join(errors))

    return record


def build_version_lock(
    record: Mapping[str, object],
) -> dict[str, str]:
    """Build the immutable version lock for one source artifact."""

    require_valid_source_record(record)

    return {
        "artifact_id": str(record["artifact_id"]),
        "artifact_type": str(record["artifact_type"]),
        "artifact_version": str(record["artifact_version"]),
        "locked_sha256": str(record["locked_sha256"]),
        "correlation_id": str(record["correlation_id"]),
        "research_run_id": str(record["research_run_id"]),
    }


def _source_sort_key(
    record: Mapping[str, object],
) -> tuple[str, str]:
    return (
        str(record.get("artifact_type", "")),
        str(record.get("artifact_id", "")),
    )


def build_source_manifest(
    *,
    manifest_id: str,
    sources: Iterable[Mapping[str, object]],
) -> dict[str, Any]:
    """Build a deterministic version-locked source manifest."""

    source_records = [deepcopy(dict(source)) for source in sources]

    if not source_records:
        raise ManifestViolation("sources must contain at least one record")

    for source in source_records:
        require_valid_source_record(source)

    source_records.sort(key=_source_sort_key)

    correlation_ids = {
        str(source["correlation_id"])
        for source in source_records
    }
    research_run_ids = {
        str(source["research_run_id"])
        for source in source_records
    }

    if len(correlation_ids) != 1:
        raise ManifestViolation(
            "all source records must use one correlation_id"
        )

    if len(research_run_ids) != 1:
        raise ManifestViolation(
            "all source records must use one research_run_id"
        )

    manifest = {
        "manifest_type": "REGISTERED_SOURCE_MANIFEST",
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "app_id": APP_ID,
        "manifest_id": manifest_id,
        "status": "VERSION_LOCKED",
        "correlation_id": next(iter(correlation_ids)),
        "research_run_id": next(iter(research_run_ids)),
        "required_artifact_types": list(REQUIRED_ARTIFACT_TYPES),
        "source_count": len(source_records),
        "sources": source_records,
        "version_locks": [
            build_version_lock(source)
            for source in source_records
        ],
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "operator_review_required": True,
        "report_synthesis_started": False,
    }

    require_valid_source_manifest(manifest)
    return manifest


def validate_source_manifest(
    manifest: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic manifest and version-lock errors."""

    errors: list[str] = []

    missing = sorted(MANIFEST_KEYS - set(manifest))
    unexpected = sorted(set(manifest) - MANIFEST_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected_scalars = {
        "manifest_type": "REGISTERED_SOURCE_MANIFEST",
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "app_id": APP_ID,
        "status": "VERSION_LOCKED",
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "operator_review_required": True,
        "report_synthesis_started": False,
    }

    for key, expected_value in expected_scalars.items():
        if manifest.get(key) != expected_value:
            errors.append(
                f"{key} must be {expected_value!r}"
            )

    _require_non_empty_string(
        "manifest_id",
        manifest.get("manifest_id"),
        errors,
    )
    _require_non_empty_string(
        "correlation_id",
        manifest.get("correlation_id"),
        errors,
    )
    _require_non_empty_string(
        "research_run_id",
        manifest.get("research_run_id"),
        errors,
    )

    if manifest.get("required_artifact_types") != list(
        REQUIRED_ARTIFACT_TYPES
    ):
        errors.append(
            "required_artifact_types must match the registered order"
        )

    sources = manifest.get("sources")

    if not isinstance(sources, Sequence) or isinstance(
        sources,
        (str, bytes),
    ):
        errors.append("sources must be a sequence")
        return tuple(errors)

    if not sources:
        errors.append("sources must contain at least one record")
        return tuple(errors)

    normalized_sources: list[Mapping[str, object]] = []

    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            errors.append(f"sources[{index}] must be a mapping")
            continue

        normalized_sources.append(source)

        for source_error in validate_source_record(source):
            errors.append(f"sources[{index}].{source_error}")

    if len(normalized_sources) != len(sources):
        return tuple(errors)

    if manifest.get("source_count") != len(normalized_sources):
        errors.append("source_count does not match sources")

    expected_order = sorted(
        normalized_sources,
        key=_source_sort_key,
    )

    if list(normalized_sources) != expected_order:
        errors.append(
            "sources must use deterministic artifact_type and artifact_id order"
        )

    artifact_ids = [
        str(source.get("artifact_id"))
        for source in normalized_sources
    ]

    if len(artifact_ids) != len(set(artifact_ids)):
        errors.append("artifact_id values must be unique")

    source_types = {
        str(source.get("artifact_type"))
        for source in normalized_sources
    }

    missing_required = sorted(
        set(REQUIRED_ARTIFACT_TYPES) - source_types
    )

    for artifact_type in missing_required:
        errors.append(
            f"required artifact type is missing: {artifact_type}"
        )

    correlation_ids = {
        str(source.get("correlation_id"))
        for source in normalized_sources
    }

    if len(correlation_ids) != 1:
        errors.append(
            "all source records must use one correlation_id"
        )
    elif manifest.get("correlation_id") not in correlation_ids:
        errors.append(
            "manifest correlation_id does not match source records"
        )

    research_run_ids = {
        str(source.get("research_run_id"))
        for source in normalized_sources
    }

    if len(research_run_ids) != 1:
        errors.append(
            "all source records must use one research_run_id"
        )
    elif manifest.get("research_run_id") not in research_run_ids:
        errors.append(
            "manifest research_run_id does not match source records"
        )

    expected_locks = [
        build_version_lock(source)
        for source in normalized_sources
        if not validate_source_record(source)
    ]

    if manifest.get("version_locks") != expected_locks:
        errors.append(
            "version_locks do not match registered source records"
        )

    return tuple(errors)


def require_valid_source_manifest(
    manifest: Mapping[str, object],
) -> Mapping[str, object]:
    """Require a valid source manifest without mutating it."""

    errors = validate_source_manifest(manifest)

    if errors:
        raise ManifestViolation("; ".join(errors))

    return manifest