from __future__ import annotations

from copy import deepcopy
from typing import Any, Iterable, Mapping, Sequence

from .d1_boundary_contract import APP_ID
from .d2_source_manifest import (
    REQUIRED_ARTIFACT_TYPES,
    require_valid_source_manifest,
    require_valid_source_record,
)

CONTENT_ITEM_SCHEMA_VERSION = "1.0.0"
SOURCE_PAYLOAD_SCHEMA_VERSION = "1.0.0"
REPORT_SCHEMA_VERSION = "1.0.0"

SECTION_ORDER = (
    "EXECUTIVE_EVIDENCE_INDEX",
    "MARKET_NARRATIVE",
    "CAUSAL_REASONING",
    "CONTRARIAN_CHALLENGE",
    "SCENARIO_SIMULATION",
    "AI_EVALUATION_EVIDENCE",
    "VALIDATION_BASELINE",
    "RISK_AND_UNCERTAINTY",
    "SOURCE_REFERENCE_INDEX",
)

ARTIFACT_SECTION_MAP = {
    "MARKET_NARRATIVE_CONTEXT": "MARKET_NARRATIVE",
    "CAUSAL_REASONING_CHAIN": "CAUSAL_REASONING",
    "CONTRARIAN_CHALLENGE": "CONTRARIAN_CHALLENGE",
    "SCENARIO_SIMULATION": "SCENARIO_SIMULATION",
    "AI_EVALUATION_EVIDENCE": "AI_EVALUATION_EVIDENCE",
    "VALIDATION_BASELINE": "VALIDATION_BASELINE",
}

SECTION_TITLES = {
    "EXECUTIVE_EVIDENCE_INDEX": "Executive Evidence Index",
    "MARKET_NARRATIVE": "Market Narrative",
    "CAUSAL_REASONING": "Causal Reasoning",
    "CONTRARIAN_CHALLENGE": "Contrarian Challenge",
    "SCENARIO_SIMULATION": "Scenario Simulation",
    "AI_EVALUATION_EVIDENCE": "AI Evaluation Evidence",
    "VALIDATION_BASELINE": "Validation Baseline",
    "RISK_AND_UNCERTAINTY": "Risk and Uncertainty",
    "SOURCE_REFERENCE_INDEX": "Source Reference Index",
}

ALLOWED_CONCLUSION_STATES = {
    "PRESERVED",
    "UNDETERMINED",
    "REVIEW_REQUIRED",
    "NOT_APPLICABLE",
}

ALLOWED_UNCERTAINTY_STATES = {
    "UNDETERMINED",
    "OPEN",
    "PARTIAL",
    "RESOLVED_BY_SOURCE",
    "NOT_APPLICABLE",
}

CONTENT_ITEM_KEYS = {
    "item_type",
    "schema_version",
    "item_id",
    "statement_type",
    "statement_text",
    "conclusion_state",
    "uncertainty_state",
    "risk_flags",
    "reason_codes",
    "evidence_refs",
    "counterevidence_refs",
    "alternative_explanation_refs",
    "source_statement_preserved",
}

SOURCE_PAYLOAD_KEYS = {
    "payload_type",
    "schema_version",
    "artifact_id",
    "artifact_type",
    "artifact_version",
    "correlation_id",
    "research_run_id",
    "locked_sha256",
    "item_count",
    "items",
    "source_artifact_preserved",
    "original_conclusion_preserved",
    "operator_review_required",
}

REPORT_KEYS = {
    "report_type",
    "schema_version",
    "app_id",
    "status",
    "manifest_id",
    "correlation_id",
    "research_run_id",
    "section_order",
    "section_count",
    "sections",
    "source_reference_index",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "operator_review_required",
    "causal_truth",
    "probability",
    "winner",
    "live_model_invoked",
    "prompt_executed",
    "runtime_orchestrator_executed",
    "automatic_archive_executed",
    "trade_action_generated",
    "real_execution",
}


class ContentItemViolation(ValueError):
    """Raised when one registered content item is invalid."""


class SourcePayloadViolation(ValueError):
    """Raised when a registered source payload is invalid."""


class ReportAssemblyViolation(ValueError):
    """Raised when deterministic report assembly is invalid."""


def _require_non_empty_string(
    field_name: str,
    value: object,
    errors: list[str],
) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field_name} must be a non-empty string")


def _normalize_string_sequence(
    field_name: str,
    values: Iterable[str],
) -> list[str]:
    normalized: list[str] = []

    for value in values:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(
                f"{field_name} values must be non-empty strings"
            )

        normalized.append(value.strip())

    return sorted(set(normalized))


def _validate_string_sequence(
    field_name: str,
    value: object,
    errors: list[str],
) -> None:
    if not isinstance(value, Sequence) or isinstance(
        value,
        (str, bytes),
    ):
        errors.append(f"{field_name} must be a sequence")
        return

    normalized: list[str] = []

    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(
                f"{field_name}[{index}] must be a non-empty string"
            )
            continue

        normalized.append(item)

    if list(value) != sorted(set(normalized)):
        errors.append(
            f"{field_name} must be sorted and duplicate-free"
        )


def build_content_item(
    *,
    item_id: str,
    statement_type: str,
    statement_text: str,
    conclusion_state: str,
    uncertainty_state: str,
    risk_flags: Iterable[str] = (),
    reason_codes: Iterable[str] = (),
    evidence_refs: Iterable[str] = (),
    counterevidence_refs: Iterable[str] = (),
    alternative_explanation_refs: Iterable[str] = (),
) -> dict[str, Any]:
    """Build one source-preserving registered content item."""

    item = {
        "item_type": "REGISTERED_REPORT_CONTENT_ITEM",
        "schema_version": CONTENT_ITEM_SCHEMA_VERSION,
        "item_id": item_id,
        "statement_type": statement_type,
        "statement_text": statement_text,
        "conclusion_state": conclusion_state,
        "uncertainty_state": uncertainty_state,
        "risk_flags": _normalize_string_sequence(
            "risk_flags",
            risk_flags,
        ),
        "reason_codes": _normalize_string_sequence(
            "reason_codes",
            reason_codes,
        ),
        "evidence_refs": _normalize_string_sequence(
            "evidence_refs",
            evidence_refs,
        ),
        "counterevidence_refs": _normalize_string_sequence(
            "counterevidence_refs",
            counterevidence_refs,
        ),
        "alternative_explanation_refs": _normalize_string_sequence(
            "alternative_explanation_refs",
            alternative_explanation_refs,
        ),
        "source_statement_preserved": True,
    }

    require_valid_content_item(item)
    return item


def validate_content_item(
    item: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic content item validation errors."""

    errors: list[str] = []

    missing = sorted(CONTENT_ITEM_KEYS - set(item))
    unexpected = sorted(set(item) - CONTENT_ITEM_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    if item.get("item_type") != "REGISTERED_REPORT_CONTENT_ITEM":
        errors.append(
            "item_type must be 'REGISTERED_REPORT_CONTENT_ITEM'"
        )

    if item.get("schema_version") != CONTENT_ITEM_SCHEMA_VERSION:
        errors.append(
            f"schema_version must be {CONTENT_ITEM_SCHEMA_VERSION!r}"
        )

    for field_name in (
        "item_id",
        "statement_type",
        "statement_text",
    ):
        _require_non_empty_string(
            field_name,
            item.get(field_name),
            errors,
        )

    if item.get("conclusion_state") not in ALLOWED_CONCLUSION_STATES:
        errors.append("conclusion_state is not registered")

    if item.get("uncertainty_state") not in ALLOWED_UNCERTAINTY_STATES:
        errors.append("uncertainty_state is not registered")

    for field_name in (
        "risk_flags",
        "reason_codes",
        "evidence_refs",
        "counterevidence_refs",
        "alternative_explanation_refs",
    ):
        _validate_string_sequence(
            field_name,
            item.get(field_name),
            errors,
        )

    if item.get("source_statement_preserved") is not True:
        errors.append("source_statement_preserved must be True")

    return tuple(errors)


def require_valid_content_item(
    item: Mapping[str, object],
) -> Mapping[str, object]:
    """Require a valid registered content item."""

    errors = validate_content_item(item)

    if errors:
        raise ContentItemViolation("; ".join(errors))

    return item


def build_source_payload(
    *,
    source_record: Mapping[str, object],
    items: Iterable[Mapping[str, object]],
) -> dict[str, Any]:
    """Build content payload locked to one registered source record."""

    require_valid_source_record(source_record)

    content_items = [deepcopy(dict(item)) for item in items]

    if not content_items:
        raise SourcePayloadViolation(
            "items must contain at least one registered content item"
        )

    for item in content_items:
        require_valid_content_item(item)

    content_items.sort(key=lambda item: str(item["item_id"]))

    item_ids = [str(item["item_id"]) for item in content_items]

    if len(item_ids) != len(set(item_ids)):
        raise SourcePayloadViolation("item_id values must be unique")

    payload = {
        "payload_type": "REGISTERED_SOURCE_CONTENT_PAYLOAD",
        "schema_version": SOURCE_PAYLOAD_SCHEMA_VERSION,
        "artifact_id": source_record["artifact_id"],
        "artifact_type": source_record["artifact_type"],
        "artifact_version": source_record["artifact_version"],
        "correlation_id": source_record["correlation_id"],
        "research_run_id": source_record["research_run_id"],
        "locked_sha256": source_record["locked_sha256"],
        "item_count": len(content_items),
        "items": content_items,
        "source_artifact_preserved": True,
        "original_conclusion_preserved": True,
        "operator_review_required": True,
    }

    require_valid_source_payload(payload, source_record)
    return payload


def validate_source_payload(
    payload: Mapping[str, object],
    source_record: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic payload-to-source lock errors."""

    errors: list[str] = []

    try:
        require_valid_source_record(source_record)
    except ValueError as exc:
        return (f"source_record is invalid: {exc}",)

    missing = sorted(SOURCE_PAYLOAD_KEYS - set(payload))
    unexpected = sorted(set(payload) - SOURCE_PAYLOAD_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected_scalars = {
        "payload_type": "REGISTERED_SOURCE_CONTENT_PAYLOAD",
        "schema_version": SOURCE_PAYLOAD_SCHEMA_VERSION,
        "artifact_id": source_record["artifact_id"],
        "artifact_type": source_record["artifact_type"],
        "artifact_version": source_record["artifact_version"],
        "correlation_id": source_record["correlation_id"],
        "research_run_id": source_record["research_run_id"],
        "locked_sha256": source_record["locked_sha256"],
        "source_artifact_preserved": True,
        "original_conclusion_preserved": True,
        "operator_review_required": True,
    }

    for key, expected_value in expected_scalars.items():
        if payload.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    items = payload.get("items")

    if not isinstance(items, Sequence) or isinstance(
        items,
        (str, bytes),
    ):
        errors.append("items must be a sequence")
        return tuple(errors)

    if not items:
        errors.append(
            "items must contain at least one registered content item"
        )
        return tuple(errors)

    valid_items: list[Mapping[str, object]] = []

    for index, item in enumerate(items):
        if not isinstance(item, Mapping):
            errors.append(f"items[{index}] must be a mapping")
            continue

        valid_items.append(item)

        for item_error in validate_content_item(item):
            errors.append(f"items[{index}].{item_error}")

    if payload.get("item_count") != len(items):
        errors.append("item_count does not match items")

    item_ids = [
        str(item.get("item_id"))
        for item in valid_items
    ]

    if len(item_ids) != len(set(item_ids)):
        errors.append("item_id values must be unique")

    expected_order = sorted(
        valid_items,
        key=lambda item: str(item.get("item_id", "")),
    )

    if valid_items != expected_order:
        errors.append("items must use deterministic item_id order")

    return tuple(errors)


def require_valid_source_payload(
    payload: Mapping[str, object],
    source_record: Mapping[str, object],
) -> Mapping[str, object]:
    """Require one payload to match its registered source lock."""

    errors = validate_source_payload(payload, source_record)

    if errors:
        raise SourcePayloadViolation("; ".join(errors))

    return payload


def _build_evidence_index(
    sources: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    return [
        {
            "artifact_id": source["artifact_id"],
            "artifact_type": source["artifact_type"],
            "artifact_version": source["artifact_version"],
            "validation_state": source["validation_state"],
            "source_conclusion_state": source[
                "source_conclusion_state"
            ],
            "locked_sha256": source["locked_sha256"],
        }
        for source in sources
    ]


def _build_source_reference_index(
    sources: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    return [
        {
            "artifact_id": source["artifact_id"],
            "artifact_type": source["artifact_type"],
            "artifact_version": source["artifact_version"],
            "source_stage_id": source["source_stage_id"],
            "source_path": source["source_path"],
            "locked_sha256": source["locked_sha256"],
            "correlation_id": source["correlation_id"],
            "research_run_id": source["research_run_id"],
        }
        for source in sources
    ]


def _build_risk_and_uncertainty_items(
    payloads: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    items: list[dict[str, object]] = []

    for payload in payloads:
        for content_item in payload["items"]:
            has_governance_content = any(
                (
                    content_item["risk_flags"],
                    content_item["counterevidence_refs"],
                    content_item["alternative_explanation_refs"],
                    content_item["uncertainty_state"]
                    != "NOT_APPLICABLE",
                )
            )

            if not has_governance_content:
                continue

            items.append(
                {
                    "artifact_id": payload["artifact_id"],
                    "artifact_type": payload["artifact_type"],
                    "item_id": content_item["item_id"],
                    "uncertainty_state": content_item[
                        "uncertainty_state"
                    ],
                    "risk_flags": deepcopy(
                        content_item["risk_flags"]
                    ),
                    "counterevidence_refs": deepcopy(
                        content_item["counterevidence_refs"]
                    ),
                    "alternative_explanation_refs": deepcopy(
                        content_item[
                            "alternative_explanation_refs"
                        ]
                    ),
                    "source_statement_preserved": True,
                }
            )

    return sorted(
        items,
        key=lambda item: (
            str(item["artifact_type"]),
            str(item["artifact_id"]),
            str(item["item_id"]),
        ),
    )


def build_report_sections(
    *,
    manifest: Mapping[str, object],
    payloads: Iterable[Mapping[str, object]],
) -> dict[str, Any]:
    """Assemble deterministic sections without rewriting source content."""

    require_valid_source_manifest(manifest)

    source_records = list(manifest["sources"])
    source_by_id = {
        str(source["artifact_id"]): source
        for source in source_records
    }

    payload_list = [deepcopy(dict(payload)) for payload in payloads]

    if not payload_list:
        raise ReportAssemblyViolation(
            "payloads must contain registered source content"
        )

    payload_by_id: dict[str, Mapping[str, object]] = {}

    for payload in payload_list:
        artifact_id = str(payload.get("artifact_id", ""))

        if artifact_id not in source_by_id:
            raise ReportAssemblyViolation(
                f"payload source is not registered: {artifact_id}"
            )

        if artifact_id in payload_by_id:
            raise ReportAssemblyViolation(
                f"duplicate payload artifact_id: {artifact_id}"
            )

        require_valid_source_payload(
            payload,
            source_by_id[artifact_id],
        )
        payload_by_id[artifact_id] = payload

    required_source_ids = {
        str(source["artifact_id"])
        for source in source_records
        if source["artifact_type"] in REQUIRED_ARTIFACT_TYPES
    }

    missing_payload_ids = sorted(
        required_source_ids - set(payload_by_id)
    )

    if missing_payload_ids:
        raise ReportAssemblyViolation(
            "required source payloads are missing: "
            + ", ".join(missing_payload_ids)
        )

    ordered_payloads = [
        payload_by_id[str(source["artifact_id"])]
        for source in source_records
        if str(source["artifact_id"]) in payload_by_id
    ]

    sections: list[dict[str, object]] = []

    sections.append(
        {
            "section_id": "EXECUTIVE_EVIDENCE_INDEX",
            "section_title": SECTION_TITLES[
                "EXECUTIVE_EVIDENCE_INDEX"
            ],
            "section_type": "SOURCE_INDEX",
            "items": _build_evidence_index(source_records),
        }
    )

    for artifact_type in REQUIRED_ARTIFACT_TYPES:
        section_id = ARTIFACT_SECTION_MAP[artifact_type]

        section_items: list[dict[str, object]] = []

        for payload in ordered_payloads:
            if payload["artifact_type"] != artifact_type:
                continue

            for item in payload["items"]:
                section_items.append(
                    {
                        "artifact_id": payload["artifact_id"],
                        "artifact_type": payload["artifact_type"],
                        "artifact_version": payload[
                            "artifact_version"
                        ],
                        "item": deepcopy(item),
                    }
                )

        sections.append(
            {
                "section_id": section_id,
                "section_title": SECTION_TITLES[section_id],
                "section_type": "PRESERVED_SOURCE_CONTENT",
                "items": section_items,
            }
        )

    sections.append(
        {
            "section_id": "RISK_AND_UNCERTAINTY",
            "section_title": SECTION_TITLES[
                "RISK_AND_UNCERTAINTY"
            ],
            "section_type": "PRESERVED_GOVERNANCE_FIELDS",
            "items": _build_risk_and_uncertainty_items(
                ordered_payloads
            ),
        }
    )

    source_reference_index = _build_source_reference_index(
        source_records
    )

    sections.append(
        {
            "section_id": "SOURCE_REFERENCE_INDEX",
            "section_title": SECTION_TITLES[
                "SOURCE_REFERENCE_INDEX"
            ],
            "section_type": "SOURCE_REFERENCE_INDEX",
            "items": deepcopy(source_reference_index),
        }
    )

    report = {
        "report_type": "DETERMINISTIC_COMPREHENSIVE_REPORT_DRAFT",
        "schema_version": REPORT_SCHEMA_VERSION,
        "app_id": APP_ID,
        "status": "ASSEMBLED_REVIEW_REQUIRED",
        "manifest_id": manifest["manifest_id"],
        "correlation_id": manifest["correlation_id"],
        "research_run_id": manifest["research_run_id"],
        "section_order": list(SECTION_ORDER),
        "section_count": len(sections),
        "sections": sections,
        "source_reference_index": source_reference_index,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "operator_review_required": True,
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "automatic_archive_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    require_valid_report_sections(report)
    return report


def validate_report_sections(
    report: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic report section validation errors."""

    errors: list[str] = []

    missing = sorted(REPORT_KEYS - set(report))
    unexpected = sorted(set(report) - REPORT_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected_scalars = {
        "report_type": "DETERMINISTIC_COMPREHENSIVE_REPORT_DRAFT",
        "schema_version": REPORT_SCHEMA_VERSION,
        "app_id": APP_ID,
        "status": "ASSEMBLED_REVIEW_REQUIRED",
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "operator_review_required": True,
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "automatic_archive_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    for key, expected_value in expected_scalars.items():
        if report.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    for field_name in (
        "manifest_id",
        "correlation_id",
        "research_run_id",
    ):
        _require_non_empty_string(
            field_name,
            report.get(field_name),
            errors,
        )

    if report.get("section_order") != list(SECTION_ORDER):
        errors.append("section_order must match the registered order")

    sections = report.get("sections")

    if not isinstance(sections, Sequence) or isinstance(
        sections,
        (str, bytes),
    ):
        errors.append("sections must be a sequence")
        return tuple(errors)

    if report.get("section_count") != len(sections):
        errors.append("section_count does not match sections")

    section_ids: list[str] = []

    for index, section in enumerate(sections):
        if not isinstance(section, Mapping):
            errors.append(f"sections[{index}] must be a mapping")
            continue

        section_id = section.get("section_id")
        section_ids.append(str(section_id))

        if section_id not in SECTION_ORDER:
            errors.append(
                f"sections[{index}].section_id is not registered"
            )

        if section.get("section_title") != SECTION_TITLES.get(
            str(section_id)
        ):
            errors.append(
                f"sections[{index}].section_title is invalid"
            )

        items = section.get("items")

        if not isinstance(items, Sequence) or isinstance(
            items,
            (str, bytes),
        ):
            errors.append(
                f"sections[{index}].items must be a sequence"
            )

    if section_ids != list(SECTION_ORDER):
        errors.append("sections must match registered section order")

    source_reference_index = report.get("source_reference_index")

    if not isinstance(source_reference_index, Sequence) or isinstance(
        source_reference_index,
        (str, bytes),
    ):
        errors.append("source_reference_index must be a sequence")
    elif sections:
        source_sections = [
            section
            for section in sections
            if isinstance(section, Mapping)
            and section.get("section_id")
            == "SOURCE_REFERENCE_INDEX"
        ]

        if len(source_sections) != 1:
            errors.append(
                "exactly one SOURCE_REFERENCE_INDEX section is required"
            )
        elif source_sections[0].get("items") != source_reference_index:
            errors.append(
                "source_reference_index must match its report section"
            )

    return tuple(errors)


def require_valid_report_sections(
    report: Mapping[str, object],
) -> Mapping[str, object]:
    """Require a valid deterministic comprehensive report draft."""

    errors = validate_report_sections(report)

    if errors:
        raise ReportAssemblyViolation("; ".join(errors))

    return report