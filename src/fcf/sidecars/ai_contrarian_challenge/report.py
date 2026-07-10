"""Deterministic contradiction and evidence-gap aggregation."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

from .contract import APP_ID
from .rules import apply_challenge_rules
from .schema import validate_challenge_evidence_record


REPORT_VERSION = "1.0.0"

REPORT_STATUSES = (
    "NO_CHALLENGE",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "INVALID",
)

REVIEW_CATEGORIES = (
    "UNSUPPORTED_CLAIM",
    "MISSING_EVIDENCE",
    "LOGICAL_GAP",
    "HIDDEN_RISK",
    "OVERCONFIDENCE",
    "CROSS_ARTIFACT_CONTRADICTION",
)

_SEVERITY_RANK = {
    "INFO": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
}


def _safety_fields() -> dict[str, bool]:
    return {
        "paper_only": True,
        "local_only": True,
        "read_only": True,
        "sidecar_only": True,
        "deterministic_only": True,
        "registered_artifacts_only": True,
        "operator_review_required": True,
        "original_conclusion_preserved": True,
        "core_mutation_allowed": False,
        "source_artifact_mutation_allowed": False,
        "model_invocation_allowed": False,
        "prompt_execution_allowed": False,
        "orchestrator_execution_allowed": False,
        "automatic_truth_decision_allowed": False,
        "automatic_winner_selection_allowed": False,
        "automatic_conclusion_replacement_allowed": False,
        "automatic_model_switch_allowed": False,
        "automatic_prompt_switch_allowed": False,
        "operator_review_bypass_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
    }


def _base_report(
    *,
    report_status: str,
    result_status: str,
    errors: list[str],
) -> dict[str, Any]:
    return {
        "app_id": APP_ID,
        "report_version": REPORT_VERSION,
        "report_status": report_status,
        "result_status": result_status,
        "operator_review_status": "REVIEW_REQUIRED",
        "source_record_count": 0,
        "finding_count": 0,
        "artifact_count": 0,
        "claim_count": 0,
        "highest_severity": "INFO",
        "category_counts": {},
        "severity_counts": {},
        "reason_code_counts": {},
        "risk_flag_counts": {},
        "evidence_gap_count": 0,
        "contradiction_count": 0,
        "artifact_summaries": [],
        "findings": [],
        "errors": sorted(set(errors)),
        **_safety_fields(),
    }


def _invalid_report(errors: list[str]) -> dict[str, Any]:
    return _base_report(
        report_status="INVALID",
        result_status="INVALID",
        errors=errors,
    )


def _blocked_report() -> dict[str, Any]:
    return _base_report(
        report_status="BLOCKED",
        result_status="BLOCKED",
        errors=["no_challenge_evidence_records"],
    )


def _sorted_counts(values: Sequence[str]) -> dict[str, int]:
    counter = Counter(values)

    return {
        key: counter[key]
        for key in sorted(counter)
    }


def _record_sort_key(
    record: Mapping[str, Any],
) -> tuple[str, str, str]:
    return (
        record["source_artifact_id"],
        record["claim_reference"],
        record["challenge_evidence_id"],
    )


def build_contradiction_evidence_gap_report(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Aggregate registered challenge evidence deterministically."""

    if isinstance(records, (str, bytes)):
        return _invalid_report(["records_invalid"])

    if not isinstance(records, Sequence):
        return _invalid_report(["records_invalid"])

    if not records:
        return _blocked_report()

    normalized_records: list[dict[str, Any]] = []
    errors: list[str] = []

    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"record_not_mapping:{index}")
            continue

        record_errors = validate_challenge_evidence_record(
            record
        )

        for error in record_errors:
            errors.append(f"record[{index}]:{error}")

        normalized_records.append(dict(record))

    if errors:
        return _invalid_report(errors)

    evidence_ids = [
        record["challenge_evidence_id"]
        for record in normalized_records
    ]

    duplicate_ids = sorted(
        evidence_id
        for evidence_id, count in Counter(
            evidence_ids
        ).items()
        if count > 1
    )

    if duplicate_ids:
        return _invalid_report(
            [
                f"duplicate_challenge_evidence_id:{item}"
                for item in duplicate_ids
            ]
        )

    ordered_records = sorted(
        normalized_records,
        key=_record_sort_key,
    )

    findings: list[dict[str, Any]] = []

    for record in ordered_records:
        rule_report = apply_challenge_rules(record)

        for finding in rule_report["findings"]:
            findings.append(
                {
                    "challenge_evidence_id": record[
                        "challenge_evidence_id"
                    ],
                    "source_artifact_id": record[
                        "source_artifact_id"
                    ],
                    "source_artifact_type": record[
                        "source_artifact_type"
                    ],
                    "source_artifact_reference": record[
                        "source_artifact_reference"
                    ],
                    "claim_reference": record[
                        "claim_reference"
                    ],
                    "source_conclusion": record[
                        "source_conclusion"
                    ],
                    "rule_id": finding["rule_id"],
                    "reason_code": finding["reason_code"],
                    "challenge_category": finding[
                        "challenge_category"
                    ],
                    "challenge_severity": finding[
                        "challenge_severity"
                    ],
                    "challenge_statement": finding[
                        "challenge_statement"
                    ],
                    "evidence_references": list(
                        finding["evidence_references"]
                    ),
                    "risk_flags": list(
                        finding["risk_flags"]
                    ),
                    "required_action": finding[
                        "required_action"
                    ],
                    "original_conclusion_preserved": True,
                    "automatic_truth_decision_allowed": False,
                    "automatic_conclusion_replacement_allowed": False,
                }
            )

    records_by_artifact: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    for finding in findings:
        artifact_id = finding["source_artifact_id"]
        records_by_artifact.setdefault(
            artifact_id,
            [],
        ).append(finding)

    artifact_summaries: list[dict[str, Any]] = []

    for artifact_id in sorted(records_by_artifact):
        artifact_findings = records_by_artifact[
            artifact_id
        ]

        artifact_summaries.append(
            {
                "source_artifact_id": artifact_id,
                "source_artifact_type": artifact_findings[
                    0
                ]["source_artifact_type"],
                "source_artifact_reference": (
                    artifact_findings[0][
                        "source_artifact_reference"
                    ]
                ),
                "finding_count": len(artifact_findings),
                "claim_references": sorted(
                    {
                        item["claim_reference"]
                        for item in artifact_findings
                    }
                ),
                "category_counts": _sorted_counts(
                    [
                        item["challenge_category"]
                        for item in artifact_findings
                    ]
                ),
                "highest_severity": max(
                    (
                        item["challenge_severity"]
                        for item in artifact_findings
                    ),
                    key=lambda value: _SEVERITY_RANK[value],
                ),
                "operator_review_status": (
                    "REVIEW_REQUIRED"
                ),
            }
        )

    category_counts = _sorted_counts(
        [
            finding["challenge_category"]
            for finding in findings
        ]
    )

    severity_counts = _sorted_counts(
        [
            finding["challenge_severity"]
            for finding in findings
        ]
    )

    reason_code_counts = _sorted_counts(
        [
            finding["reason_code"]
            for finding in findings
        ]
    )

    risk_flag_counts = _sorted_counts(
        [
            risk_flag
            for finding in findings
            for risk_flag in finding["risk_flags"]
        ]
    )

    if findings:
        highest_severity = max(
            (
                finding["challenge_severity"]
                for finding in findings
            ),
            key=lambda value: _SEVERITY_RANK[value],
        )
        report_status = "REVIEW_REQUIRED"
    else:
        highest_severity = "INFO"
        report_status = "NO_CHALLENGE"

    return {
        "app_id": APP_ID,
        "report_version": REPORT_VERSION,
        "report_status": report_status,
        "result_status": "RECORDED",
        "operator_review_status": "REVIEW_REQUIRED",
        "source_record_count": len(ordered_records),
        "finding_count": len(findings),
        "artifact_count": len(
            {
                record["source_artifact_id"]
                for record in ordered_records
            }
        ),
        "claim_count": len(
            {
                (
                    record["source_artifact_id"],
                    record["claim_reference"],
                )
                for record in ordered_records
            }
        ),
        "highest_severity": highest_severity,
        "category_counts": category_counts,
        "severity_counts": severity_counts,
        "reason_code_counts": reason_code_counts,
        "risk_flag_counts": risk_flag_counts,
        "evidence_gap_count": category_counts.get(
            "MISSING_EVIDENCE",
            0,
        ),
        "contradiction_count": category_counts.get(
            "CROSS_ARTIFACT_CONTRADICTION",
            0,
        ),
        "artifact_summaries": artifact_summaries,
        "findings": findings,
        "errors": [],
        **_safety_fields(),
    }