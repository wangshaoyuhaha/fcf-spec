"""Deterministic construction of registered causal chains."""

from copy import deepcopy
import re
from typing import Any, Mapping, Sequence

from .contract import (
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
)
from .schema import (
    CLAIM_RECORD_STATUSES,
    CLAIM_TYPES,
    validate_registered_causal_claim_record,
)


STAGE_ID = "AI-CAUSAL-REASONING-CHAIN-D3"
CHAIN_VERSION = "1.0.0"

CHAIN_STATUSES = (
    "READY_FOR_ASSESSMENT",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

REQUIRED_EDGE_FIELDS = (
    "edge_id",
    "claim_id",
    "cause_ref_id",
    "effect_ref_id",
    "claim_type",
    "source_claim_record_status",
    "premise_ids",
    "supporting_evidence_ref_ids",
    "counterevidence_ref_ids",
    "alternative_explanation_ref_ids",
    "causal_truth_status",
    "probability_status",
    "operator_review_status",
    "source_artifacts_preserved",
    "safety_flags",
)

REQUIRED_CHAIN_FIELDS = (
    "chain_id",
    "correlation_id",
    "research_run_id",
    "claim_records",
    "node_ids",
    "edge_records",
    "root_node_ids",
    "terminal_node_ids",
    "chain_status",
    "reason_codes",
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


class CausalChainViolation(ValueError):
    """Raised when registered claims cannot form a valid chain."""


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


def _canonical_claims(
    claim_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        [deepcopy(dict(record)) for record in claim_records],
        key=lambda item: str(item["claim_id"]),
    )


def _evidence_ids_by_role(
    claim_record: Mapping[str, Any],
    role: str,
) -> list[str]:
    return _canonical_strings(
        [
            str(reference["evidence_ref_id"])
            for reference in claim_record[
                "evidence_references"
            ]
            if reference["evidence_role"] == role
        ]
    )


def _build_edge_record(
    claim_record: Mapping[str, Any],
) -> dict[str, Any]:
    claim_id = str(claim_record["claim_id"])

    return {
        "edge_id": f"edge:{claim_id}",
        "claim_id": claim_id,
        "cause_ref_id": str(
            claim_record["cause_ref_id"]
        ),
        "effect_ref_id": str(
            claim_record["effect_ref_id"]
        ),
        "claim_type": str(
            claim_record["claim_type"]
        ),
        "source_claim_record_status": str(
            claim_record["record_status"]
        ),
        "premise_ids": _canonical_strings(
            [
                str(premise["premise_id"])
                for premise in claim_record[
                    "premise_records"
                ]
            ]
        ),
        "supporting_evidence_ref_ids": (
            _evidence_ids_by_role(
                claim_record,
                "SUPPORTING",
            )
        ),
        "counterevidence_ref_ids": (
            _evidence_ids_by_role(
                claim_record,
                "COUNTEREVIDENCE",
            )
        ),
        "alternative_explanation_ref_ids": (
            _evidence_ids_by_role(
                claim_record,
                "ALTERNATIVE_EXPLANATION",
            )
        ),
        "causal_truth_status": "UNDETERMINED",
        "probability_status": "NOT_ASSIGNED",
        "operator_review_status": "REQUIRED",
        "source_artifacts_preserved": True,
        "safety_flags": _safety_flags(),
    }


def _canonical_edges(
    edges: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        [deepcopy(dict(edge)) for edge in edges],
        key=lambda item: (
            str(item["cause_ref_id"]),
            str(item["effect_ref_id"]),
            str(item["claim_id"]),
        ),
    )


def _node_ids(
    edges: Sequence[Mapping[str, Any]],
) -> list[str]:
    values: list[str] = []

    for edge in edges:
        values.append(str(edge["cause_ref_id"]))
        values.append(str(edge["effect_ref_id"]))

    return _canonical_strings(values)


def _root_node_ids(
    edges: Sequence[Mapping[str, Any]],
) -> list[str]:
    causes = {
        str(edge["cause_ref_id"])
        for edge in edges
    }

    effects = {
        str(edge["effect_ref_id"])
        for edge in edges
    }

    return sorted(causes - effects)


def _terminal_node_ids(
    edges: Sequence[Mapping[str, Any]],
) -> list[str]:
    causes = {
        str(edge["cause_ref_id"])
        for edge in edges
    }

    effects = {
        str(edge["effect_ref_id"])
        for edge in edges
    }

    return sorted(effects - causes)


def _derive_reason_codes(
    claim_records: Sequence[Mapping[str, Any]],
) -> list[str]:
    reasons: list[str] = []

    for claim in claim_records:
        claim_id = str(claim["claim_id"])
        record_status = claim["record_status"]

        if record_status == "BLOCKED":
            reasons.append(
                f"CLAIM_BLOCKED:{claim_id}"
            )
        elif record_status == "REVIEW_REQUIRED":
            reasons.append(
                f"CLAIM_REVIEW_REQUIRED:{claim_id}"
            )

    return sorted(set(reasons))


def _derive_chain_status(
    reason_codes: Sequence[str],
) -> str:
    if any(
        reason.startswith("CLAIM_BLOCKED:")
        for reason in reason_codes
    ):
        return "BLOCKED"

    if reason_codes:
        return "REVIEW_REQUIRED"

    return "READY_FOR_ASSESSMENT"


def build_deterministic_causal_chain(
    *,
    chain_id: str,
    claim_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a deterministic chain without deciding causal truth."""
    if not claim_records:
        raise CausalChainViolation(
            "claim_records_empty"
        )

    nested_errors: list[str] = []

    for index, claim_record in enumerate(
        claim_records
    ):
        for error in (
            validate_registered_causal_claim_record(
                claim_record
            )
        ):
            nested_errors.append(
                f"claim:{index}:{error}"
            )

    if nested_errors:
        raise CausalChainViolation(
            ";".join(nested_errors)
        )

    canonical_claims = _canonical_claims(
        claim_records
    )

    claim_ids = [
        str(record["claim_id"])
        for record in canonical_claims
    ]

    if len(claim_ids) != len(set(claim_ids)):
        raise CausalChainViolation(
            "claim_ids_must_be_unique"
        )

    correlation_ids = {
        str(record["correlation_id"])
        for record in canonical_claims
    }

    if len(correlation_ids) != 1:
        raise CausalChainViolation(
            "correlation_id_mismatch"
        )

    research_run_ids = {
        str(record["research_run_id"])
        for record in canonical_claims
    }

    if len(research_run_ids) != 1:
        raise CausalChainViolation(
            "research_run_id_mismatch"
        )

    edges = _canonical_edges(
        [
            _build_edge_record(record)
            for record in canonical_claims
        ]
    )

    reason_codes = _derive_reason_codes(
        canonical_claims
    )

    return {
        "chain_id": chain_id,
        "correlation_id": next(
            iter(correlation_ids)
        ),
        "research_run_id": next(
            iter(research_run_ids)
        ),
        "claim_records": canonical_claims,
        "node_ids": _node_ids(edges),
        "edge_records": edges,
        "root_node_ids": _root_node_ids(edges),
        "terminal_node_ids": _terminal_node_ids(edges),
        "chain_status": _derive_chain_status(
            reason_codes
        ),
        "reason_codes": reason_codes,
        "causal_truth_status": "UNDETERMINED",
        "probability_status": "NOT_ASSIGNED",
        "winner_status": "NOT_SELECTED",
        "operator_review_status": "REQUIRED",
        "source_artifacts_preserved": True,
        "original_conclusions_preserved": True,
        "safety_flags": _safety_flags(),
    }


def validate_causal_chain_edge_record(
    edge: object,
) -> list[str]:
    """Return deterministic D3 edge validation errors."""
    if not isinstance(edge, Mapping):
        return ["edge_record_must_be_mapping"]

    errors: list[str] = []

    if set(edge.keys()) != set(
        REQUIRED_EDGE_FIELDS
    ):
        errors.append(
            "edge_fields_must_match_schema"
        )

    for field in (
        "edge_id",
        "claim_id",
        "cause_ref_id",
        "effect_ref_id",
    ):
        if not _valid_identifier(edge.get(field)):
            errors.append(f"{field}_invalid")

    if edge.get("cause_ref_id") == edge.get(
        "effect_ref_id"
    ):
        errors.append("cause_and_effect_must_differ")

    if edge.get("edge_id") != (
        f"edge:{edge.get('claim_id')}"
    ):
        errors.append("edge_id_mismatch")

    if edge.get("claim_type") not in CLAIM_TYPES:
        errors.append("claim_type_invalid")

    if edge.get(
        "source_claim_record_status"
    ) not in CLAIM_RECORD_STATUSES:
        errors.append(
            "source_claim_record_status_invalid"
        )

    for field in (
        "premise_ids",
        "supporting_evidence_ref_ids",
        "counterevidence_ref_ids",
        "alternative_explanation_ref_ids",
    ):
        if not _valid_canonical_string_list(
            edge.get(field)
        ):
            errors.append(f"{field}_invalid")

    if edge.get("causal_truth_status") != (
        "UNDETERMINED"
    ):
        errors.append("causal_truth_status_invalid")

    if edge.get("probability_status") != (
        "NOT_ASSIGNED"
    ):
        errors.append("probability_status_invalid")

    if edge.get("operator_review_status") != (
        "REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if edge.get(
        "source_artifacts_preserved"
    ) is not True:
        errors.append(
            "source_artifacts_preserved_must_be_true"
        )

    errors.extend(
        _validate_safety_flags(
            edge.get("safety_flags")
        )
    )

    return errors


def validate_deterministic_causal_chain(
    chain: object,
) -> list[str]:
    """Return deterministic D3 chain validation errors."""
    if not isinstance(chain, Mapping):
        return ["causal_chain_must_be_mapping"]

    errors: list[str] = []

    if set(chain.keys()) != set(
        REQUIRED_CHAIN_FIELDS
    ):
        errors.append(
            "chain_fields_must_match_schema"
        )

    for field in (
        "chain_id",
        "correlation_id",
        "research_run_id",
    ):
        if not _valid_identifier(chain.get(field)):
            errors.append(f"{field}_invalid")

    claim_records = chain.get("claim_records")

    if not isinstance(claim_records, list):
        errors.append(
            "claim_records_must_be_list"
        )
        claim_records = []
    elif not claim_records:
        errors.append("claim_records_empty")
    else:
        for index, claim_record in enumerate(
            claim_records
        ):
            for error in (
                validate_registered_causal_claim_record(
                    claim_record
                )
            ):
                errors.append(
                    f"claim:{index}:{error}"
                )

    valid_claims = [
        record
        for record in claim_records
        if isinstance(record, Mapping)
    ]

    if len(valid_claims) == len(claim_records):
        if claim_records != _canonical_claims(
            valid_claims
        ):
            errors.append(
                "claim_records_must_be_canonical"
            )

    claim_ids = [
        record.get("claim_id")
        for record in valid_claims
    ]

    if len(claim_ids) != len(set(claim_ids)):
        errors.append("claim_ids_must_be_unique")

    for index, claim_record in enumerate(
        valid_claims
    ):
        if claim_record.get("correlation_id") != (
            chain.get("correlation_id")
        ):
            errors.append(
                f"claim:{index}:correlation_id_mismatch"
            )

        if claim_record.get("research_run_id") != (
            chain.get("research_run_id")
        ):
            errors.append(
                f"claim:{index}:research_run_id_mismatch"
            )

    edge_records = chain.get("edge_records")

    if not isinstance(edge_records, list):
        errors.append("edge_records_must_be_list")
        edge_records = []
    else:
        for index, edge in enumerate(edge_records):
            for error in (
                validate_causal_chain_edge_record(
                    edge
                )
            ):
                errors.append(
                    f"edge:{index}:{error}"
                )

    valid_edges = [
        edge
        for edge in edge_records
        if isinstance(edge, Mapping)
    ]

    if len(valid_edges) == len(edge_records):
        if edge_records != _canonical_edges(
            valid_edges
        ):
            errors.append(
                "edge_records_must_be_canonical"
            )

    expected_edges = _canonical_edges(
        [
            _build_edge_record(record)
            for record in valid_claims
        ]
    )

    if edge_records != expected_edges:
        errors.append(
            "edge_records_do_not_match_claim_records"
        )

    edge_ids = [
        edge.get("edge_id")
        for edge in valid_edges
    ]

    if len(edge_ids) != len(set(edge_ids)):
        errors.append("edge_ids_must_be_unique")

    for field in (
        "node_ids",
        "root_node_ids",
        "terminal_node_ids",
    ):
        if not _valid_canonical_string_list(
            chain.get(field)
        ):
            errors.append(f"{field}_invalid")

    expected_nodes = _node_ids(valid_edges)
    expected_roots = _root_node_ids(valid_edges)
    expected_terminals = _terminal_node_ids(
        valid_edges
    )

    if chain.get("node_ids") != expected_nodes:
        errors.append("node_ids_mismatch")

    if chain.get("root_node_ids") != expected_roots:
        errors.append("root_node_ids_mismatch")

    if chain.get("terminal_node_ids") != (
        expected_terminals
    ):
        errors.append("terminal_node_ids_mismatch")

    expected_reasons = _derive_reason_codes(
        valid_claims
    )

    if chain.get("reason_codes") != expected_reasons:
        errors.append("reason_codes_mismatch")

    expected_status = _derive_chain_status(
        expected_reasons
    )

    if chain.get("chain_status") not in (
        CHAIN_STATUSES
    ):
        errors.append("chain_status_invalid")
    elif chain.get("chain_status") != expected_status:
        errors.append("chain_status_mismatch")

    if chain.get("causal_truth_status") != (
        "UNDETERMINED"
    ):
        errors.append("causal_truth_status_invalid")

    if chain.get("probability_status") != (
        "NOT_ASSIGNED"
    ):
        errors.append("probability_status_invalid")

    if chain.get("winner_status") != "NOT_SELECTED":
        errors.append("winner_status_invalid")

    if chain.get("operator_review_status") != (
        "REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if chain.get(
        "source_artifacts_preserved"
    ) is not True:
        errors.append(
            "source_artifacts_preserved_must_be_true"
        )

    if chain.get(
        "original_conclusions_preserved"
    ) is not True:
        errors.append(
            "original_conclusions_preserved_must_be_true"
        )

    errors.extend(
        _validate_safety_flags(
            chain.get("safety_flags")
        )
    )

    return errors
