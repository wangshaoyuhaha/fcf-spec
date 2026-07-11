from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from typing import Any, Iterable, Mapping, Sequence

from .d1_boundary_contract import APP_ID
from .d2_source_manifest import (
    REQUIRED_ARTIFACT_TYPES,
    require_valid_source_manifest,
)
from .d3_report_assembly import (
    ARTIFACT_SECTION_MAP,
    require_valid_report_sections,
)

GOVERNANCE_ASSESSMENT_SCHEMA_VERSION = "1.0.0"

REGISTERED_ISSUE_CODES = (
    "REPORT_MANIFEST_ID_MISMATCH",
    "CORRELATION_ID_MISMATCH",
    "RESEARCH_RUN_ID_MISMATCH",
    "REQUIRED_REPORT_SECTION_MISSING",
    "REQUIRED_REPORT_SECTION_EMPTY",
    "SOURCE_REFERENCE_MISSING",
    "UNREGISTERED_SOURCE_REFERENCE",
    "SOURCE_VERSION_DRIFT",
    "EVIDENCE_INDEX_VERSION_DRIFT",
    "CROSS_ARTIFACT_CONCLUSION_CONFLICT",
    "CAUSAL_EVIDENCE_GAP",
    "SCENARIO_COVERAGE_GAP",
    "EVALUATION_DRIFT_OPEN",
    "VALIDATION_BASELINE_GAP",
    "SOURCE_VALIDATION_REVIEW_REQUIRED",
    "UNRESOLVED_COUNTEREVIDENCE",
    "ALTERNATIVE_EXPLANATION_OPEN",
    "SOURCE_CONCLUSION_UNRESOLVED",
    "RISK_FLAG_OPEN",
    "RISK_AND_UNCERTAINTY_VISIBILITY_GAP",
)

REGISTERED_SEVERITIES = (
    "BLOCKING",
    "HIGH",
    "MEDIUM",
    "LOW",
)

SEVERITY_ORDER = {
    "BLOCKING": 0,
    "HIGH": 1,
    "MEDIUM": 2,
    "LOW": 3,
}

ISSUE_KEYS = {
    "issue_type",
    "schema_version",
    "issue_id",
    "issue_code",
    "severity",
    "status",
    "artifact_ids",
    "section_ids",
    "item_ids",
    "details",
    "operator_action_required",
    "automatic_resolution_allowed",
}

ASSESSMENT_KEYS = {
    "assessment_type",
    "schema_version",
    "app_id",
    "status",
    "manifest_id",
    "correlation_id",
    "research_run_id",
    "issue_count",
    "blocking_issue_count",
    "unresolved_issue_count",
    "issue_code_counts",
    "issues",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "operator_review_required",
    "operator_decision",
    "causal_truth",
    "probability",
    "winner",
    "report_mutated",
    "live_model_invoked",
    "prompt_executed",
    "runtime_orchestrator_executed",
    "automatic_archive_executed",
    "trade_action_generated",
    "real_execution",
}

DRIFT_MARKERS = (
    "EVALUATION_DRIFT",
    "MODEL_DRIFT",
    "PROMPT_DRIFT",
    "SAMPLE_DRIFT",
    "RESULT_DRIFT",
)

SOURCE_REFERENCE_FIELDS = (
    "artifact_id",
    "artifact_type",
    "artifact_version",
    "source_stage_id",
    "source_path",
    "locked_sha256",
    "correlation_id",
    "research_run_id",
)

EVIDENCE_INDEX_FIELDS = (
    "artifact_id",
    "artifact_type",
    "artifact_version",
    "validation_state",
    "source_conclusion_state",
    "locked_sha256",
)


class GovernanceAssessmentViolation(ValueError):
    """Raised when a D4 governance assessment is invalid."""


def _normalize_strings(values: Iterable[object]) -> list[str]:
    normalized: list[str] = []

    for value in values:
        text = str(value).strip()

        if text:
            normalized.append(text)

    return sorted(set(normalized))


def _append_issue(
    issues: list[dict[str, Any]],
    *,
    issue_code: str,
    severity: str,
    details: str,
    artifact_ids: Iterable[object] = (),
    section_ids: Iterable[object] = (),
    item_ids: Iterable[object] = (),
) -> None:
    if issue_code not in REGISTERED_ISSUE_CODES:
        raise GovernanceAssessmentViolation(
            f"issue_code is not registered: {issue_code}"
        )

    if severity not in REGISTERED_SEVERITIES:
        raise GovernanceAssessmentViolation(
            f"severity is not registered: {severity}"
        )

    issues.append(
        {
            "issue_type": "CROSS_ARTIFACT_GOVERNANCE_ISSUE",
            "schema_version": GOVERNANCE_ASSESSMENT_SCHEMA_VERSION,
            "issue_id": "",
            "issue_code": issue_code,
            "severity": severity,
            "status": "OPEN",
            "artifact_ids": _normalize_strings(artifact_ids),
            "section_ids": _normalize_strings(section_ids),
            "item_ids": _normalize_strings(item_ids),
            "details": details,
            "operator_action_required": True,
            "automatic_resolution_allowed": False,
        }
    )


def _issue_sort_key(
    issue: Mapping[str, object],
) -> tuple[object, ...]:
    return (
        SEVERITY_ORDER[str(issue["severity"])],
        str(issue["issue_code"]),
        tuple(issue["artifact_ids"]),
        tuple(issue["section_ids"]),
        tuple(issue["item_ids"]),
        str(issue["details"]),
    )


def _finalize_issues(
    issues: Iterable[Mapping[str, object]],
) -> list[dict[str, Any]]:
    ordered = [
        deepcopy(dict(issue))
        for issue in sorted(issues, key=_issue_sort_key)
    ]

    for index, issue in enumerate(ordered, start=1):
        issue["issue_id"] = f"GOV-{index:04d}"

    return ordered


def _section_map(
    report: Mapping[str, object],
) -> dict[str, Mapping[str, object]]:
    sections = report["sections"]

    return {
        str(section["section_id"]): section
        for section in sections
        if isinstance(section, Mapping)
    }


def _content_entries(
    report: Mapping[str, object],
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []

    for section in report["sections"]:
        if not isinstance(section, Mapping):
            continue

        if section.get("section_type") != "PRESERVED_SOURCE_CONTENT":
            continue

        section_id = str(section["section_id"])

        for raw_entry in section["items"]:
            if not isinstance(raw_entry, Mapping):
                continue

            item = raw_entry.get("item")

            if not isinstance(item, Mapping):
                continue

            entries.append(
                {
                    "section_id": section_id,
                    "artifact_id": str(
                        raw_entry.get("artifact_id", "")
                    ),
                    "artifact_type": str(
                        raw_entry.get("artifact_type", "")
                    ),
                    "artifact_version": str(
                        raw_entry.get("artifact_version", "")
                    ),
                    "item": item,
                }
            )

    return sorted(
        entries,
        key=lambda entry: (
            entry["section_id"],
            entry["artifact_type"],
            entry["artifact_id"],
            str(entry["item"].get("item_id", "")),
        ),
    )


def _check_identity_alignment(
    *,
    manifest: Mapping[str, object],
    report: Mapping[str, object],
    issues: list[dict[str, Any]],
) -> None:
    if report["manifest_id"] != manifest["manifest_id"]:
        _append_issue(
            issues,
            issue_code="REPORT_MANIFEST_ID_MISMATCH",
            severity="BLOCKING",
            details=(
                "The report manifest_id does not match the "
                "version-locked source manifest."
            ),
        )

    if report["correlation_id"] != manifest["correlation_id"]:
        _append_issue(
            issues,
            issue_code="CORRELATION_ID_MISMATCH",
            severity="BLOCKING",
            details=(
                "The report correlation_id does not match the "
                "registered source manifest."
            ),
        )

    if report["research_run_id"] != manifest["research_run_id"]:
        _append_issue(
            issues,
            issue_code="RESEARCH_RUN_ID_MISMATCH",
            severity="BLOCKING",
            details=(
                "The report research_run_id does not match the "
                "registered source manifest."
            ),
        )


def _check_required_sections(
    *,
    report: Mapping[str, object],
    issues: list[dict[str, Any]],
) -> None:
    sections = _section_map(report)

    for artifact_type in REQUIRED_ARTIFACT_TYPES:
        section_id = ARTIFACT_SECTION_MAP[artifact_type]
        section = sections.get(section_id)

        if section is None:
            _append_issue(
                issues,
                issue_code="REQUIRED_REPORT_SECTION_MISSING",
                severity="BLOCKING",
                details=(
                    "A required report section is missing for "
                    f"{artifact_type}."
                ),
                section_ids=[section_id],
            )
            continue

        items = section.get("items")

        if (
            not isinstance(items, Sequence)
            or isinstance(items, (str, bytes))
            or not items
        ):
            _append_issue(
                issues,
                issue_code="REQUIRED_REPORT_SECTION_EMPTY",
                severity="BLOCKING",
                details=(
                    "A required report section contains no preserved "
                    f"source content for {artifact_type}."
                ),
                section_ids=[section_id],
            )


def _reference_by_id(
    records: Sequence[object],
) -> dict[str, Mapping[str, object]]:
    indexed: dict[str, Mapping[str, object]] = {}

    for record in records:
        if not isinstance(record, Mapping):
            continue

        artifact_id = str(record.get("artifact_id", ""))

        if artifact_id:
            indexed[artifact_id] = record

    return indexed


def _check_source_reference_index(
    *,
    manifest: Mapping[str, object],
    report: Mapping[str, object],
    issues: list[dict[str, Any]],
) -> None:
    sources = manifest["sources"]
    source_by_id = _reference_by_id(sources)
    report_refs = report["source_reference_index"]
    reference_by_id = _reference_by_id(report_refs)

    for artifact_id, source in source_by_id.items():
        reference = reference_by_id.get(artifact_id)

        if reference is None:
            _append_issue(
                issues,
                issue_code="SOURCE_REFERENCE_MISSING",
                severity="BLOCKING",
                details=(
                    "A registered source artifact is missing from the "
                    "report source reference index."
                ),
                artifact_ids=[artifact_id],
                section_ids=["SOURCE_REFERENCE_INDEX"],
            )
            continue

        mismatched_fields = [
            field_name
            for field_name in SOURCE_REFERENCE_FIELDS
            if reference.get(field_name) != source.get(field_name)
        ]

        if mismatched_fields:
            _append_issue(
                issues,
                issue_code="SOURCE_VERSION_DRIFT",
                severity="BLOCKING",
                details=(
                    "The source reference differs from the locked "
                    "manifest fields: "
                    + ", ".join(mismatched_fields)
                ),
                artifact_ids=[artifact_id],
                section_ids=["SOURCE_REFERENCE_INDEX"],
            )

    extra_ids = sorted(set(reference_by_id) - set(source_by_id))

    for artifact_id in extra_ids:
        _append_issue(
            issues,
            issue_code="UNREGISTERED_SOURCE_REFERENCE",
            severity="BLOCKING",
            details=(
                "The report references an artifact that is not present "
                "in the version-locked source manifest."
            ),
            artifact_ids=[artifact_id],
            section_ids=["SOURCE_REFERENCE_INDEX"],
        )


def _check_evidence_index(
    *,
    manifest: Mapping[str, object],
    report: Mapping[str, object],
    issues: list[dict[str, Any]],
) -> None:
    sections = _section_map(report)
    evidence_section = sections.get("EXECUTIVE_EVIDENCE_INDEX")

    if evidence_section is None:
        return

    sources = manifest["sources"]
    source_by_id = _reference_by_id(sources)
    evidence_by_id = _reference_by_id(evidence_section["items"])

    for artifact_id, source in source_by_id.items():
        evidence = evidence_by_id.get(artifact_id)

        if evidence is None:
            _append_issue(
                issues,
                issue_code="EVIDENCE_INDEX_VERSION_DRIFT",
                severity="BLOCKING",
                details=(
                    "A registered source is missing from the executive "
                    "evidence index."
                ),
                artifact_ids=[artifact_id],
                section_ids=["EXECUTIVE_EVIDENCE_INDEX"],
            )
            continue

        mismatched_fields = [
            field_name
            for field_name in EVIDENCE_INDEX_FIELDS
            if evidence.get(field_name) != source.get(field_name)
        ]

        if mismatched_fields:
            _append_issue(
                issues,
                issue_code="EVIDENCE_INDEX_VERSION_DRIFT",
                severity="BLOCKING",
                details=(
                    "The executive evidence index differs from the "
                    "locked manifest fields: "
                    + ", ".join(mismatched_fields)
                ),
                artifact_ids=[artifact_id],
                section_ids=["EXECUTIVE_EVIDENCE_INDEX"],
            )


def _check_manifest_validation_states(
    *,
    manifest: Mapping[str, object],
    issues: list[dict[str, Any]],
) -> None:
    validation_baseline_sources = [
        source
        for source in manifest["sources"]
        if source["artifact_type"] == "VALIDATION_BASELINE"
    ]

    if not validation_baseline_sources:
        _append_issue(
            issues,
            issue_code="VALIDATION_BASELINE_GAP",
            severity="BLOCKING",
            details=(
                "The version-locked source manifest does not contain a "
                "validation baseline artifact."
            ),
            section_ids=["VALIDATION_BASELINE"],
        )

    for source in manifest["sources"]:
        if source["validation_state"] == "VALIDATED":
            continue

        _append_issue(
            issues,
            issue_code="SOURCE_VALIDATION_REVIEW_REQUIRED",
            severity="HIGH",
            details=(
                "A registered source artifact is not in the VALIDATED "
                "state."
            ),
            artifact_ids=[source["artifact_id"]],
            section_ids=[
                ARTIFACT_SECTION_MAP.get(
                    source["artifact_type"],
                    "EXECUTIVE_EVIDENCE_INDEX",
                )
            ],
        )

        if source["artifact_type"] == "VALIDATION_BASELINE":
            _append_issue(
                issues,
                issue_code="VALIDATION_BASELINE_GAP",
                severity="BLOCKING",
                details=(
                    "The registered validation baseline is not in the "
                    "VALIDATED state."
                ),
                artifact_ids=[source["artifact_id"]],
                section_ids=["VALIDATION_BASELINE"],
            )


def _check_cross_artifact_conflicts(
    *,
    entries: Sequence[Mapping[str, object]],
    issues: list[dict[str, Any]],
) -> None:
    groups: dict[
        tuple[str, str],
        list[Mapping[str, object]],
    ] = defaultdict(list)

    for entry in entries:
        item = entry["item"]
        statement_type = str(item.get("statement_type", "")).strip()
        statement_text = str(item.get("statement_text", "")).strip()

        key = (
            statement_type.casefold(),
            statement_text.casefold(),
        )
        groups[key].append(entry)

    for grouped_entries in groups.values():
        artifact_ids = {
            str(entry["artifact_id"])
            for entry in grouped_entries
        }
        conclusion_states = {
            str(entry["item"].get("conclusion_state", ""))
            for entry in grouped_entries
        }

        if len(artifact_ids) < 2 or len(conclusion_states) < 2:
            continue

        _append_issue(
            issues,
            issue_code="CROSS_ARTIFACT_CONCLUSION_CONFLICT",
            severity="HIGH",
            details=(
                "The same preserved statement has different registered "
                "conclusion states across source artifacts."
            ),
            artifact_ids=artifact_ids,
            section_ids={
                entry["section_id"]
                for entry in grouped_entries
            },
            item_ids={
                entry["item"].get("item_id", "")
                for entry in grouped_entries
            },
        )


def _check_causal_evidence(
    *,
    entries: Sequence[Mapping[str, object]],
    issues: list[dict[str, Any]],
) -> None:
    for entry in entries:
        if entry["section_id"] != "CAUSAL_REASONING":
            continue

        item = entry["item"]
        evidence_refs = item.get("evidence_refs")

        if evidence_refs:
            continue

        _append_issue(
            issues,
            issue_code="CAUSAL_EVIDENCE_GAP",
            severity="HIGH",
            details=(
                "A preserved causal reasoning item has no registered "
                "evidence reference."
            ),
            artifact_ids=[entry["artifact_id"]],
            section_ids=["CAUSAL_REASONING"],
            item_ids=[item.get("item_id", "")],
        )


def _check_scenario_coverage(
    *,
    entries: Sequence[Mapping[str, object]],
    issues: list[dict[str, Any]],
) -> None:
    scenario_entries = [
        entry
        for entry in entries
        if entry["section_id"] == "SCENARIO_SIMULATION"
    ]

    if len(scenario_entries) >= 2:
        return

    _append_issue(
        issues,
        issue_code="SCENARIO_COVERAGE_GAP",
        severity="MEDIUM",
        details=(
            "Scenario coverage contains fewer than two preserved "
            "scenario items. No preferred scenario is selected."
        ),
        artifact_ids={
            entry["artifact_id"]
            for entry in scenario_entries
        },
        section_ids=["SCENARIO_SIMULATION"],
        item_ids={
            entry["item"].get("item_id", "")
            for entry in scenario_entries
        },
    )


def _contains_drift_marker(values: Iterable[object]) -> bool:
    for raw_value in values:
        value = str(raw_value).upper()

        if value.startswith("DRIFT_"):
            return True

        if any(marker in value for marker in DRIFT_MARKERS):
            return True

    return False


def _check_evaluation_drift(
    *,
    entries: Sequence[Mapping[str, object]],
    issues: list[dict[str, Any]],
) -> None:
    for entry in entries:
        if entry["section_id"] != "AI_EVALUATION_EVIDENCE":
            continue

        item = entry["item"]
        markers = [
            *item.get("risk_flags", []),
            *item.get("reason_codes", []),
        ]

        if not _contains_drift_marker(markers):
            continue

        _append_issue(
            issues,
            issue_code="EVALUATION_DRIFT_OPEN",
            severity="HIGH",
            details=(
                "The AI evaluation evidence contains a registered open "
                "drift marker."
            ),
            artifact_ids=[entry["artifact_id"]],
            section_ids=["AI_EVALUATION_EVIDENCE"],
            item_ids=[item.get("item_id", "")],
        )


def _check_open_governance_fields(
    *,
    entries: Sequence[Mapping[str, object]],
    issues: list[dict[str, Any]],
) -> None:
    for entry in entries:
        item = entry["item"]
        artifact_id = entry["artifact_id"]
        section_id = entry["section_id"]
        item_id = item.get("item_id", "")

        if item.get("counterevidence_refs"):
            _append_issue(
                issues,
                issue_code="UNRESOLVED_COUNTEREVIDENCE",
                severity="HIGH",
                details=(
                    "The preserved source item contains registered "
                    "counterevidence requiring operator review."
                ),
                artifact_ids=[artifact_id],
                section_ids=[section_id],
                item_ids=[item_id],
            )

        if item.get("alternative_explanation_refs"):
            _append_issue(
                issues,
                issue_code="ALTERNATIVE_EXPLANATION_OPEN",
                severity="MEDIUM",
                details=(
                    "The preserved source item contains an open "
                    "alternative explanation."
                ),
                artifact_ids=[artifact_id],
                section_ids=[section_id],
                item_ids=[item_id],
            )

        if item.get("risk_flags"):
            _append_issue(
                issues,
                issue_code="RISK_FLAG_OPEN",
                severity="MEDIUM",
                details=(
                    "The preserved source item contains one or more "
                    "registered risk flags."
                ),
                artifact_ids=[artifact_id],
                section_ids=[section_id],
                item_ids=[item_id],
            )

        if item.get("conclusion_state") in {
            "UNDETERMINED",
            "REVIEW_REQUIRED",
        }:
            _append_issue(
                issues,
                issue_code="SOURCE_CONCLUSION_UNRESOLVED",
                severity="MEDIUM",
                details=(
                    "The preserved source item conclusion remains "
                    "unresolved and must not be replaced."
                ),
                artifact_ids=[artifact_id],
                section_ids=[section_id],
                item_ids=[item_id],
            )


def _governance_projection(
    entry: Mapping[str, object],
) -> dict[str, object]:
    item = entry["item"]

    return {
        "uncertainty_state": item.get("uncertainty_state"),
        "risk_flags": deepcopy(item.get("risk_flags", [])),
        "counterevidence_refs": deepcopy(
            item.get("counterevidence_refs", [])
        ),
        "alternative_explanation_refs": deepcopy(
            item.get("alternative_explanation_refs", [])
        ),
    }


def _check_risk_visibility(
    *,
    report: Mapping[str, object],
    entries: Sequence[Mapping[str, object]],
    issues: list[dict[str, Any]],
) -> None:
    sections = _section_map(report)
    risk_section = sections.get("RISK_AND_UNCERTAINTY")

    if risk_section is None:
        return

    visible: dict[
        tuple[str, str],
        Mapping[str, object],
    ] = {}

    for raw_item in risk_section["items"]:
        if not isinstance(raw_item, Mapping):
            continue

        key = (
            str(raw_item.get("artifact_id", "")),
            str(raw_item.get("item_id", "")),
        )
        visible[key] = raw_item

    for entry in entries:
        item = entry["item"]
        projection = _governance_projection(entry)

        has_governance_content = any(
            (
                projection["risk_flags"],
                projection["counterevidence_refs"],
                projection["alternative_explanation_refs"],
                projection["uncertainty_state"] != "NOT_APPLICABLE",
            )
        )

        if not has_governance_content:
            continue

        key = (
            str(entry["artifact_id"]),
            str(item.get("item_id", "")),
        )
        visible_item = visible.get(key)

        if visible_item is None:
            _append_issue(
                issues,
                issue_code="RISK_AND_UNCERTAINTY_VISIBILITY_GAP",
                severity="BLOCKING",
                details=(
                    "A source governance item is absent from the risk "
                    "and uncertainty section."
                ),
                artifact_ids=[entry["artifact_id"]],
                section_ids=[
                    entry["section_id"],
                    "RISK_AND_UNCERTAINTY",
                ],
                item_ids=[item.get("item_id", "")],
            )
            continue

        visible_projection = {
            "uncertainty_state": visible_item.get(
                "uncertainty_state"
            ),
            "risk_flags": visible_item.get("risk_flags"),
            "counterevidence_refs": visible_item.get(
                "counterevidence_refs"
            ),
            "alternative_explanation_refs": visible_item.get(
                "alternative_explanation_refs"
            ),
        }

        if visible_projection != projection:
            _append_issue(
                issues,
                issue_code="RISK_AND_UNCERTAINTY_VISIBILITY_GAP",
                severity="BLOCKING",
                details=(
                    "The risk and uncertainty section does not exactly "
                    "preserve the registered governance fields."
                ),
                artifact_ids=[entry["artifact_id"]],
                section_ids=[
                    entry["section_id"],
                    "RISK_AND_UNCERTAINTY",
                ],
                item_ids=[item.get("item_id", "")],
            )


def build_governance_assessment(
    *,
    manifest: Mapping[str, object],
    report: Mapping[str, object],
) -> dict[str, Any]:
    """Build a deterministic cross-artifact governance assessment."""

    require_valid_source_manifest(manifest)
    require_valid_report_sections(report)

    issues: list[dict[str, Any]] = []
    entries = _content_entries(report)

    _check_identity_alignment(
        manifest=manifest,
        report=report,
        issues=issues,
    )
    _check_required_sections(
        report=report,
        issues=issues,
    )
    _check_source_reference_index(
        manifest=manifest,
        report=report,
        issues=issues,
    )
    _check_evidence_index(
        manifest=manifest,
        report=report,
        issues=issues,
    )
    _check_manifest_validation_states(
        manifest=manifest,
        issues=issues,
    )
    _check_cross_artifact_conflicts(
        entries=entries,
        issues=issues,
    )
    _check_causal_evidence(
        entries=entries,
        issues=issues,
    )
    _check_scenario_coverage(
        entries=entries,
        issues=issues,
    )
    _check_evaluation_drift(
        entries=entries,
        issues=issues,
    )
    _check_open_governance_fields(
        entries=entries,
        issues=issues,
    )
    _check_risk_visibility(
        report=report,
        entries=entries,
        issues=issues,
    )

    finalized_issues = _finalize_issues(issues)
    issue_code_counts = dict(
        sorted(
            Counter(
                issue["issue_code"]
                for issue in finalized_issues
            ).items()
        )
    )
    blocking_issue_count = sum(
        issue["severity"] == "BLOCKING"
        for issue in finalized_issues
    )

    status = (
        "ASSESSMENT_BLOCKED"
        if blocking_issue_count
        else "ASSESSMENT_COMPLETE_REVIEW_REQUIRED"
    )

    assessment = {
        "assessment_type": (
            "CROSS_ARTIFACT_GOVERNANCE_ASSESSMENT"
        ),
        "schema_version": GOVERNANCE_ASSESSMENT_SCHEMA_VERSION,
        "app_id": APP_ID,
        "status": status,
        "manifest_id": manifest["manifest_id"],
        "correlation_id": manifest["correlation_id"],
        "research_run_id": manifest["research_run_id"],
        "issue_count": len(finalized_issues),
        "blocking_issue_count": blocking_issue_count,
        "unresolved_issue_count": len(finalized_issues),
        "issue_code_counts": issue_code_counts,
        "issues": finalized_issues,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "operator_review_required": True,
        "operator_decision": "PENDING",
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "report_mutated": False,
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "automatic_archive_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    require_valid_governance_assessment(assessment)
    return assessment


def _validate_string_list(
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

    normalized = [
        item
        for item in value
        if isinstance(item, str) and item.strip()
    ]

    if len(normalized) != len(value):
        errors.append(
            f"{field_name} values must be non-empty strings"
        )
        return

    if list(value) != sorted(set(normalized)):
        errors.append(
            f"{field_name} must be sorted and duplicate-free"
        )


def _validate_issue(
    issue: Mapping[str, object],
    expected_issue_id: str,
) -> tuple[str, ...]:
    errors: list[str] = []

    missing = sorted(ISSUE_KEYS - set(issue))
    unexpected = sorted(set(issue) - ISSUE_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected_scalars = {
        "issue_type": "CROSS_ARTIFACT_GOVERNANCE_ISSUE",
        "schema_version": GOVERNANCE_ASSESSMENT_SCHEMA_VERSION,
        "issue_id": expected_issue_id,
        "status": "OPEN",
        "operator_action_required": True,
        "automatic_resolution_allowed": False,
    }

    for key, expected_value in expected_scalars.items():
        if issue.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    if issue.get("issue_code") not in REGISTERED_ISSUE_CODES:
        errors.append("issue_code is not registered")

    if issue.get("severity") not in REGISTERED_SEVERITIES:
        errors.append("severity is not registered")

    details = issue.get("details")

    if not isinstance(details, str) or not details.strip():
        errors.append("details must be a non-empty string")

    for field_name in (
        "artifact_ids",
        "section_ids",
        "item_ids",
    ):
        _validate_string_list(
            field_name,
            issue.get(field_name),
            errors,
        )

    return tuple(errors)


def validate_governance_assessment(
    assessment: Mapping[str, object],
) -> tuple[str, ...]:
    """Return deterministic governance assessment validation errors."""

    errors: list[str] = []

    missing = sorted(ASSESSMENT_KEYS - set(assessment))
    unexpected = sorted(set(assessment) - ASSESSMENT_KEYS)

    for key in missing:
        errors.append(f"{key} is missing")

    for key in unexpected:
        errors.append(f"{key} is not registered")

    expected_scalars = {
        "assessment_type": (
            "CROSS_ARTIFACT_GOVERNANCE_ASSESSMENT"
        ),
        "schema_version": GOVERNANCE_ASSESSMENT_SCHEMA_VERSION,
        "app_id": APP_ID,
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "operator_review_required": True,
        "operator_decision": "PENDING",
        "causal_truth": "UNDETERMINED",
        "probability": "NOT_ASSIGNED",
        "winner": "NOT_SELECTED",
        "report_mutated": False,
        "live_model_invoked": False,
        "prompt_executed": False,
        "runtime_orchestrator_executed": False,
        "automatic_archive_executed": False,
        "trade_action_generated": False,
        "real_execution": False,
    }

    for key, expected_value in expected_scalars.items():
        if assessment.get(key) != expected_value:
            errors.append(f"{key} must be {expected_value!r}")

    for field_name in (
        "manifest_id",
        "correlation_id",
        "research_run_id",
    ):
        value = assessment.get(field_name)

        if not isinstance(value, str) or not value.strip():
            errors.append(
                f"{field_name} must be a non-empty string"
            )

    issues = assessment.get("issues")

    if not isinstance(issues, Sequence) or isinstance(
        issues,
        (str, bytes),
    ):
        errors.append("issues must be a sequence")
        return tuple(errors)

    valid_issues: list[Mapping[str, object]] = []

    for index, issue in enumerate(issues, start=1):
        if not isinstance(issue, Mapping):
            errors.append(
                f"issues[{index - 1}] must be a mapping"
            )
            continue

        valid_issues.append(issue)

        expected_id = f"GOV-{index:04d}"

        for issue_error in _validate_issue(issue, expected_id):
            errors.append(
                f"issues[{index - 1}].{issue_error}"
            )

    if assessment.get("issue_count") != len(issues):
        errors.append("issue_count does not match issues")

    unresolved_count = sum(
        issue.get("status") == "OPEN"
        for issue in valid_issues
    )

    if assessment.get("unresolved_issue_count") != unresolved_count:
        errors.append(
            "unresolved_issue_count does not match open issues"
        )

    blocking_count = sum(
        issue.get("severity") == "BLOCKING"
        for issue in valid_issues
    )

    if assessment.get("blocking_issue_count") != blocking_count:
        errors.append(
            "blocking_issue_count does not match blocking issues"
        )

    expected_status = (
        "ASSESSMENT_BLOCKED"
        if blocking_count
        else "ASSESSMENT_COMPLETE_REVIEW_REQUIRED"
    )

    if assessment.get("status") != expected_status:
        errors.append(f"status must be {expected_status!r}")

    expected_counts = dict(
        sorted(
            Counter(
                str(issue.get("issue_code"))
                for issue in valid_issues
            ).items()
        )
    )

    if assessment.get("issue_code_counts") != expected_counts:
        errors.append(
            "issue_code_counts do not match registered issues"
        )

    if list(valid_issues) != sorted(
        valid_issues,
        key=_issue_sort_key,
    ):
        errors.append("issues must use deterministic order")

    return tuple(errors)


def require_valid_governance_assessment(
    assessment: Mapping[str, object],
) -> Mapping[str, object]:
    """Require a valid D4 governance assessment."""

    errors = validate_governance_assessment(assessment)

    if errors:
        raise GovernanceAssessmentViolation("; ".join(errors))

    return assessment