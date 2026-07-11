"""Deterministic governance assessment of registered causal chains."""

from copy import deepcopy
import re
from typing import Any, Mapping, Sequence

from .chain import (
    CHAIN_STATUSES,
    validate_deterministic_causal_chain,
)
from .contract import (
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
)


STAGE_ID = "AI-CAUSAL-REASONING-CHAIN-D4"
ASSESSMENT_VERSION = "1.0.0"

ASSESSMENT_STATUSES = (
    "READY_FOR_REVIEW_PACKET",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

FINDING_SEVERITIES = (
    "INFO",
    "MEDIUM",
    "HIGH",
    "CRITICAL",
)

FINDING_TYPES = (
    "DISCONNECTED_COMPONENTS",
    "CYCLE_DETECTED",
    "DUPLICATE_DIRECTIONAL_EDGE",
    "CONFLICTING_REVERSE_EDGE",
    "MISSING_REGISTERED_PREMISE",
    "MISSING_SUPPORTING_EVIDENCE",
    "COUNTEREVIDENCE_NOT_REVIEWED",
    "COUNTEREVIDENCE_REVIEW_BLOCKED",
    "ALTERNATIVE_EXPLANATION_NOT_REVIEWED",
    "ALTERNATIVE_EXPLANATION_REVIEW_BLOCKED",
    "REGISTERED_COUNTEREVIDENCE_SIGNAL",
    "REGISTERED_ALTERNATIVE_EXPLANATION_SIGNAL",
    "SOURCE_CLAIM_REVIEW_REQUIRED",
    "BLOCKED_SOURCE_CLAIM",
)

REQUIRED_FINDING_FIELDS = (
    "finding_id",
    "finding_type",
    "severity",
    "related_claim_ids",
    "related_node_ids",
    "related_evidence_ref_ids",
    "detail_code",
    "operator_review_status",
    "source_artifacts_preserved",
)

REQUIRED_DUPLICATE_GROUP_FIELDS = (
    "cause_ref_id",
    "effect_ref_id",
    "claim_ids",
)

REQUIRED_REVERSE_PAIR_FIELDS = (
    "node_ids",
    "forward_claim_ids",
    "reverse_claim_ids",
)

REQUIRED_ASSESSMENT_FIELDS = (
    "assessment_id",
    "source_chain",
    "source_chain_id",
    "source_chain_status",
    "correlation_id",
    "research_run_id",
    "finding_records",
    "component_count",
    "cycle_paths",
    "duplicate_directional_edge_groups",
    "reverse_edge_pairs",
    "reason_codes",
    "assessment_status",
    "causal_truth_status",
    "probability_status",
    "winner_status",
    "operator_review_status",
    "source_artifacts_preserved",
    "original_conclusions_preserved",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class CausalAssessmentViolation(ValueError):
    """Raised when a causal chain cannot be assessed safely."""


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


def _canonical_strings(
    values: Sequence[str],
) -> list[str]:
    return sorted(set(values))


def _valid_canonical_string_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False

    if any(
        not isinstance(item, str)
        or not item.strip()
        or not _valid_identifier(item)
        for item in value
    ):
        return False

    return value == sorted(set(value))


def _validate_safety_flags(value: Any) -> list[str]:
    if not isinstance(value, Mapping):
        return ["safety_flags_must_be_mapping"]

    errors: list[str] = []

    expected_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )

    if set(value.keys()) != expected_names:
        errors.append(
            "safety_flag_names_must_match_contract"
        )

    for name in REQUIRED_TRUE_FLAGS:
        if value.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if value.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    return errors


def _weak_components(
    node_ids: Sequence[str],
    edge_records: Sequence[Mapping[str, Any]],
) -> list[list[str]]:
    adjacency = {
        node_id: set()
        for node_id in node_ids
    }

    for edge in edge_records:
        cause_id = str(edge["cause_ref_id"])
        effect_id = str(edge["effect_ref_id"])

        adjacency[cause_id].add(effect_id)
        adjacency[effect_id].add(cause_id)

    components: list[list[str]] = []
    visited: set[str] = set()

    for start in sorted(node_ids):
        if start in visited:
            continue

        pending = [start]
        component: list[str] = []

        while pending:
            node_id = pending.pop()

            if node_id in visited:
                continue

            visited.add(node_id)
            component.append(node_id)

            for neighbor in sorted(
                adjacency[node_id],
                reverse=True,
            ):
                if neighbor not in visited:
                    pending.append(neighbor)

        components.append(sorted(component))

    return sorted(
        components,
        key=lambda item: tuple(item),
    )


def _canonical_cycle(
    cycle_path: Sequence[str],
) -> list[str]:
    body = list(cycle_path[:-1])

    rotations = [
        body[index:] + body[:index]
        for index in range(len(body))
    ]

    canonical_body = list(
        min(tuple(rotation) for rotation in rotations)
    )

    return canonical_body + [canonical_body[0]]


def _detect_cycle_paths(
    node_ids: Sequence[str],
    edge_records: Sequence[Mapping[str, Any]],
) -> list[list[str]]:
    adjacency = {
        node_id: []
        for node_id in node_ids
    }

    for edge in edge_records:
        adjacency[str(edge["cause_ref_id"])].append(
            str(edge["effect_ref_id"])
        )

    for node_id in adjacency:
        adjacency[node_id] = sorted(
            set(adjacency[node_id])
        )

    state = {
        node_id: 0
        for node_id in node_ids
    }

    stack: list[str] = []
    discovered: set[tuple[str, ...]] = set()

    def visit(node_id: str) -> None:
        state[node_id] = 1
        stack.append(node_id)

        for neighbor in adjacency[node_id]:
            if state[neighbor] == 0:
                visit(neighbor)
            elif state[neighbor] == 1:
                start_index = stack.index(neighbor)
                raw_cycle = (
                    stack[start_index:] + [neighbor]
                )

                canonical = _canonical_cycle(raw_cycle)
                discovered.add(tuple(canonical))

        stack.pop()
        state[node_id] = 2

    for node_id in sorted(node_ids):
        if state[node_id] == 0:
            visit(node_id)

    return [
        list(path)
        for path in sorted(discovered)
    ]


def _duplicate_directional_edge_groups(
    edge_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[str]] = {}

    for edge in edge_records:
        key = (
            str(edge["cause_ref_id"]),
            str(edge["effect_ref_id"]),
        )

        grouped.setdefault(key, []).append(
            str(edge["claim_id"])
        )

    groups: list[dict[str, Any]] = []

    for (cause_id, effect_id), claim_ids in sorted(
        grouped.items()
    ):
        canonical_claim_ids = _canonical_strings(
            claim_ids
        )

        if len(canonical_claim_ids) > 1:
            groups.append(
                {
                    "cause_ref_id": cause_id,
                    "effect_ref_id": effect_id,
                    "claim_ids": canonical_claim_ids,
                }
            )

    return groups


def _reverse_edge_pairs(
    edge_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[str]] = {}

    for edge in edge_records:
        key = (
            str(edge["cause_ref_id"]),
            str(edge["effect_ref_id"]),
        )

        grouped.setdefault(key, []).append(
            str(edge["claim_id"])
        )

    pairs: list[dict[str, Any]] = []

    for key in sorted(grouped):
        reverse_key = (key[1], key[0])

        if reverse_key not in grouped:
            continue

        if key >= reverse_key:
            continue

        pairs.append(
            {
                "node_ids": sorted(
                    [key[0], key[1]]
                ),
                "forward_claim_ids": _canonical_strings(
                    grouped[key]
                ),
                "reverse_claim_ids": _canonical_strings(
                    grouped[reverse_key]
                ),
            }
        )

    return pairs


def _raw_finding(
    *,
    finding_type: str,
    severity: str,
    related_claim_ids: Sequence[str] = (),
    related_node_ids: Sequence[str] = (),
    related_evidence_ref_ids: Sequence[str] = (),
    detail_code: str,
) -> dict[str, Any]:
    return {
        "finding_type": finding_type,
        "severity": severity,
        "related_claim_ids": _canonical_strings(
            related_claim_ids
        ),
        "related_node_ids": _canonical_strings(
            related_node_ids
        ),
        "related_evidence_ref_ids": _canonical_strings(
            related_evidence_ref_ids
        ),
        "detail_code": detail_code,
        "operator_review_status": "REQUIRED",
        "source_artifacts_preserved": True,
    }


def _canonical_findings(
    findings: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    ordered = sorted(
        [dict(finding) for finding in findings],
        key=lambda item: (
            str(item["finding_type"]),
            tuple(item["related_claim_ids"]),
            tuple(item["related_node_ids"]),
            tuple(item["related_evidence_ref_ids"]),
            str(item["detail_code"]),
        ),
    )

    result: list[dict[str, Any]] = []

    for index, finding in enumerate(
        ordered,
        start=1,
    ):
        record = {
            "finding_id": (
                f"finding-{index:03d}"
            ),
            **finding,
        }

        result.append(record)

    return result


def _collect_findings(
    source_chain: Mapping[str, Any],
    components: Sequence[Sequence[str]],
    cycle_paths: Sequence[Sequence[str]],
    duplicate_groups: Sequence[Mapping[str, Any]],
    reverse_pairs: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    if len(components) > 1:
        findings.append(
            _raw_finding(
                finding_type="DISCONNECTED_COMPONENTS",
                severity="HIGH",
                related_node_ids=source_chain["node_ids"],
                detail_code=(
                    f"COMPONENT_COUNT:{len(components)}"
                ),
            )
        )

    for cycle_path in cycle_paths:
        findings.append(
            _raw_finding(
                finding_type="CYCLE_DETECTED",
                severity="CRITICAL",
                related_node_ids=cycle_path[:-1],
                detail_code=(
                    "CYCLE:"
                    + "->".join(cycle_path)
                ),
            )
        )

    for group in duplicate_groups:
        findings.append(
            _raw_finding(
                finding_type="DUPLICATE_DIRECTIONAL_EDGE",
                severity="HIGH",
                related_claim_ids=group["claim_ids"],
                related_node_ids=[
                    group["cause_ref_id"],
                    group["effect_ref_id"],
                ],
                detail_code=(
                    "DUPLICATE_EDGE:"
                    + group["cause_ref_id"]
                    + "->"
                    + group["effect_ref_id"]
                ),
            )
        )

    for pair in reverse_pairs:
        findings.append(
            _raw_finding(
                finding_type="CONFLICTING_REVERSE_EDGE",
                severity="HIGH",
                related_claim_ids=(
                    list(pair["forward_claim_ids"])
                    + list(pair["reverse_claim_ids"])
                ),
                related_node_ids=pair["node_ids"],
                detail_code=(
                    "REVERSE_EDGE_PAIR:"
                    + "<->".join(pair["node_ids"])
                ),
            )
        )

    claim_by_id = {
        str(record["claim_id"]): record
        for record in source_chain["claim_records"]
    }

    for edge in source_chain["edge_records"]:
        claim_id = str(edge["claim_id"])

        if not edge["premise_ids"]:
            findings.append(
                _raw_finding(
                    finding_type=(
                        "MISSING_REGISTERED_PREMISE"
                    ),
                    severity="HIGH",
                    related_claim_ids=[claim_id],
                    related_node_ids=[
                        edge["cause_ref_id"],
                        edge["effect_ref_id"],
                    ],
                    detail_code=(
                        f"MISSING_PREMISE:{claim_id}"
                    ),
                )
            )

        if not edge["supporting_evidence_ref_ids"]:
            findings.append(
                _raw_finding(
                    finding_type=(
                        "MISSING_SUPPORTING_EVIDENCE"
                    ),
                    severity="HIGH",
                    related_claim_ids=[claim_id],
                    related_node_ids=[
                        edge["cause_ref_id"],
                        edge["effect_ref_id"],
                    ],
                    detail_code=(
                        f"MISSING_SUPPORT:{claim_id}"
                    ),
                )
            )

        if edge["source_claim_record_status"] == "BLOCKED":
            findings.append(
                _raw_finding(
                    finding_type="BLOCKED_SOURCE_CLAIM",
                    severity="CRITICAL",
                    related_claim_ids=[claim_id],
                    detail_code=(
                        f"BLOCKED_CLAIM:{claim_id}"
                    ),
                )
            )
        elif edge["source_claim_record_status"] == (
            "REVIEW_REQUIRED"
        ):
            findings.append(
                _raw_finding(
                    finding_type=(
                        "SOURCE_CLAIM_REVIEW_REQUIRED"
                    ),
                    severity="HIGH",
                    related_claim_ids=[claim_id],
                    detail_code=(
                        f"CLAIM_REVIEW_REQUIRED:{claim_id}"
                    ),
                )
            )

        if edge["counterevidence_ref_ids"]:
            findings.append(
                _raw_finding(
                    finding_type=(
                        "REGISTERED_COUNTEREVIDENCE_SIGNAL"
                    ),
                    severity="INFO",
                    related_claim_ids=[claim_id],
                    related_evidence_ref_ids=(
                        edge["counterevidence_ref_ids"]
                    ),
                    detail_code=(
                        f"COUNTEREVIDENCE_PRESENT:{claim_id}"
                    ),
                )
            )

        if edge["alternative_explanation_ref_ids"]:
            findings.append(
                _raw_finding(
                    finding_type=(
                        "REGISTERED_ALTERNATIVE_EXPLANATION_SIGNAL"
                    ),
                    severity="INFO",
                    related_claim_ids=[claim_id],
                    related_evidence_ref_ids=(
                        edge[
                            "alternative_explanation_ref_ids"
                        ]
                    ),
                    detail_code=(
                        f"ALTERNATIVE_PRESENT:{claim_id}"
                    ),
                )
            )

        claim_record = claim_by_id[claim_id]

        counter_status = claim_record[
            "counterevidence_review_status"
        ]

        if counter_status == "NOT_REVIEWED":
            findings.append(
                _raw_finding(
                    finding_type=(
                        "COUNTEREVIDENCE_NOT_REVIEWED"
                    ),
                    severity="HIGH",
                    related_claim_ids=[claim_id],
                    detail_code=(
                        f"COUNTEREVIDENCE_NOT_REVIEWED:{claim_id}"
                    ),
                )
            )
        elif counter_status == "BLOCKED":
            findings.append(
                _raw_finding(
                    finding_type=(
                        "COUNTEREVIDENCE_REVIEW_BLOCKED"
                    ),
                    severity="CRITICAL",
                    related_claim_ids=[claim_id],
                    detail_code=(
                        f"COUNTEREVIDENCE_BLOCKED:{claim_id}"
                    ),
                )
            )

        alternative_status = claim_record[
            "alternative_explanation_review_status"
        ]

        if alternative_status == "NOT_REVIEWED":
            findings.append(
                _raw_finding(
                    finding_type=(
                        "ALTERNATIVE_EXPLANATION_NOT_REVIEWED"
                    ),
                    severity="HIGH",
                    related_claim_ids=[claim_id],
                    detail_code=(
                        f"ALTERNATIVE_NOT_REVIEWED:{claim_id}"
                    ),
                )
            )
        elif alternative_status == "BLOCKED":
            findings.append(
                _raw_finding(
                    finding_type=(
                        "ALTERNATIVE_EXPLANATION_REVIEW_BLOCKED"
                    ),
                    severity="CRITICAL",
                    related_claim_ids=[claim_id],
                    detail_code=(
                        f"ALTERNATIVE_BLOCKED:{claim_id}"
                    ),
                )
            )

    return _canonical_findings(findings)


def _reason_codes(
    finding_records: Sequence[Mapping[str, Any]],
) -> list[str]:
    return sorted(
        {
            (
                str(finding["finding_type"])
                + ":"
                + str(finding["detail_code"])
            )
            for finding in finding_records
            if finding["severity"] != "INFO"
        }
    )


def _assessment_status(
    source_chain_status: str,
    finding_records: Sequence[Mapping[str, Any]],
) -> str:
    if source_chain_status == "BLOCKED":
        return "BLOCKED"

    if any(
        finding["severity"] == "CRITICAL"
        for finding in finding_records
    ):
        return "BLOCKED"

    if any(
        finding["severity"] in (
            "MEDIUM",
            "HIGH",
        )
        for finding in finding_records
    ):
        return "REVIEW_REQUIRED"

    return "READY_FOR_REVIEW_PACKET"


def _build_from_valid_chain(
    *,
    assessment_id: str,
    source_chain: Mapping[str, Any],
) -> dict[str, Any]:
    edge_records = source_chain["edge_records"]
    node_ids = source_chain["node_ids"]

    components = _weak_components(
        node_ids,
        edge_records,
    )

    cycle_paths = _detect_cycle_paths(
        node_ids,
        edge_records,
    )

    duplicate_groups = (
        _duplicate_directional_edge_groups(
            edge_records
        )
    )

    reverse_pairs = _reverse_edge_pairs(
        edge_records
    )

    findings = _collect_findings(
        source_chain,
        components,
        cycle_paths,
        duplicate_groups,
        reverse_pairs,
    )

    reasons = _reason_codes(findings)

    return {
        "assessment_id": assessment_id,
        "source_chain": deepcopy(dict(source_chain)),
        "source_chain_id": source_chain["chain_id"],
        "source_chain_status": source_chain[
            "chain_status"
        ],
        "correlation_id": source_chain[
            "correlation_id"
        ],
        "research_run_id": source_chain[
            "research_run_id"
        ],
        "finding_records": findings,
        "component_count": len(components),
        "cycle_paths": [
            list(path)
            for path in cycle_paths
        ],
        "duplicate_directional_edge_groups": (
            deepcopy(duplicate_groups)
        ),
        "reverse_edge_pairs": deepcopy(
            reverse_pairs
        ),
        "reason_codes": reasons,
        "assessment_status": _assessment_status(
            str(source_chain["chain_status"]),
            findings,
        ),
        "causal_truth_status": "UNDETERMINED",
        "probability_status": "NOT_ASSIGNED",
        "winner_status": "NOT_SELECTED",
        "operator_review_status": "REQUIRED",
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "safety_flags": _safety_flags(),
    }


def build_causal_reasoning_assessment(
    *,
    assessment_id: str,
    source_chain: Mapping[str, Any],
) -> dict[str, Any]:
    """Assess registered chain structure without deciding truth."""
    chain_errors = validate_deterministic_causal_chain(
        source_chain
    )

    if chain_errors:
        raise CausalAssessmentViolation(
            ";".join(chain_errors)
        )

    return _build_from_valid_chain(
        assessment_id=assessment_id,
        source_chain=source_chain,
    )


def _validate_finding_record(
    finding: object,
) -> list[str]:
    if not isinstance(finding, Mapping):
        return ["finding_record_must_be_mapping"]

    errors: list[str] = []

    if set(finding.keys()) != set(
        REQUIRED_FINDING_FIELDS
    ):
        errors.append(
            "finding_fields_must_match_schema"
        )

    if not _valid_identifier(
        finding.get("finding_id")
    ):
        errors.append("finding_id_invalid")

    if finding.get("finding_type") not in (
        FINDING_TYPES
    ):
        errors.append("finding_type_invalid")

    if finding.get("severity") not in (
        FINDING_SEVERITIES
    ):
        errors.append("severity_invalid")

    for field in (
        "related_claim_ids",
        "related_node_ids",
        "related_evidence_ref_ids",
    ):
        if not _valid_canonical_string_list(
            finding.get(field)
        ):
            errors.append(f"{field}_invalid")

    detail_code = finding.get("detail_code")

    if (
        not isinstance(detail_code, str)
        or not detail_code.strip()
    ):
        errors.append("detail_code_invalid")

    if finding.get("operator_review_status") != (
        "REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if finding.get(
        "source_artifacts_preserved"
    ) is not True:
        errors.append(
            "source_artifacts_preserved_must_be_true"
        )

    return errors


def validate_causal_reasoning_assessment(
    assessment: object,
) -> list[str]:
    """Return deterministic D4 assessment validation errors."""
    if not isinstance(assessment, Mapping):
        return ["assessment_must_be_mapping"]

    errors: list[str] = []

    if set(assessment.keys()) != set(
        REQUIRED_ASSESSMENT_FIELDS
    ):
        errors.append(
            "assessment_fields_must_match_schema"
        )

    if not _valid_identifier(
        assessment.get("assessment_id")
    ):
        errors.append("assessment_id_invalid")

    source_chain = assessment.get("source_chain")

    if not isinstance(source_chain, Mapping):
        errors.append("source_chain_must_be_mapping")
        source_chain_errors = [
            "source_chain_must_be_mapping"
        ]
    else:
        source_chain_errors = (
            validate_deterministic_causal_chain(
                source_chain
            )
        )

        for chain_error in source_chain_errors:
            errors.append(
                f"source_chain:{chain_error}"
            )

    if assessment.get("source_chain_status") not in (
        CHAIN_STATUSES
    ):
        errors.append("source_chain_status_invalid")

    findings = assessment.get("finding_records")

    if not isinstance(findings, list):
        errors.append("finding_records_must_be_list")
        findings = []
    else:
        for index, finding in enumerate(findings):
            for finding_error in (
                _validate_finding_record(finding)
            ):
                errors.append(
                    f"finding:{index}:{finding_error}"
                )

    finding_ids = [
        finding.get("finding_id")
        for finding in findings
        if isinstance(finding, Mapping)
    ]

    if len(finding_ids) != len(set(finding_ids)):
        errors.append("finding_ids_must_be_unique")

    component_count = assessment.get(
        "component_count"
    )

    if (
        not isinstance(component_count, int)
        or isinstance(component_count, bool)
        or component_count < 1
    ):
        errors.append("component_count_invalid")

    cycle_paths = assessment.get("cycle_paths")

    if not isinstance(cycle_paths, list):
        errors.append("cycle_paths_must_be_list")

    duplicate_groups = assessment.get(
        "duplicate_directional_edge_groups"
    )

    if not isinstance(duplicate_groups, list):
        errors.append(
            "duplicate_directional_edge_groups_must_be_list"
        )
    else:
        for index, group in enumerate(
            duplicate_groups
        ):
            if not isinstance(group, Mapping):
                errors.append(
                    f"duplicate_group:{index}:must_be_mapping"
                )
                continue

            if set(group.keys()) != set(
                REQUIRED_DUPLICATE_GROUP_FIELDS
            ):
                errors.append(
                    f"duplicate_group:{index}:fields_invalid"
                )

    reverse_pairs = assessment.get(
        "reverse_edge_pairs"
    )

    if not isinstance(reverse_pairs, list):
        errors.append(
            "reverse_edge_pairs_must_be_list"
        )
    else:
        for index, pair in enumerate(reverse_pairs):
            if not isinstance(pair, Mapping):
                errors.append(
                    f"reverse_pair:{index}:must_be_mapping"
                )
                continue

            if set(pair.keys()) != set(
                REQUIRED_REVERSE_PAIR_FIELDS
            ):
                errors.append(
                    f"reverse_pair:{index}:fields_invalid"
                )

    if assessment.get("assessment_status") not in (
        ASSESSMENT_STATUSES
    ):
        errors.append("assessment_status_invalid")

    if assessment.get("causal_truth_status") != (
        "UNDETERMINED"
    ):
        errors.append("causal_truth_status_invalid")

    if assessment.get("probability_status") != (
        "NOT_ASSIGNED"
    ):
        errors.append("probability_status_invalid")

    if assessment.get("winner_status") != (
        "NOT_SELECTED"
    ):
        errors.append("winner_status_invalid")

    if assessment.get("operator_review_status") != (
        "REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if assessment.get(
        "source_artifacts_preserved"
    ) is not True:
        errors.append(
            "source_artifacts_preserved_must_be_true"
        )

    if assessment.get(
        "original_conclusions_preserved"
    ) is not True:
        errors.append(
            "original_conclusions_preserved_must_be_true"
        )

    errors.extend(
        _validate_safety_flags(
            assessment.get("safety_flags")
        )
    )

    if (
        isinstance(source_chain, Mapping)
        and not source_chain_errors
        and _valid_identifier(
            assessment.get("assessment_id")
        )
    ):
        expected = _build_from_valid_chain(
            assessment_id=str(
                assessment["assessment_id"]
            ),
            source_chain=source_chain,
        )

        comparison_fields = (
            "source_chain_id",
            "source_chain_status",
            "correlation_id",
            "research_run_id",
            "finding_records",
            "component_count",
            "cycle_paths",
            "duplicate_directional_edge_groups",
            "reverse_edge_pairs",
            "reason_codes",
            "assessment_status",
        )

        for field in comparison_fields:
            if assessment.get(field) != expected[field]:
                errors.append(f"{field}_mismatch")

    return sorted(set(errors))
