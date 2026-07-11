"""Registered evidence schemas for deterministic causal reasoning."""

import re
from typing import Any, Mapping, Sequence

from .contract import (
    ALLOWED_INPUT_ARTIFACT_TYPES,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
)


STAGE_ID = "AI-CAUSAL-REASONING-CHAIN-D2"
SCHEMA_VERSION = "1.0.0"

REGISTRATION_STATUSES = (
    "REGISTERED",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

CLAIM_TYPES = (
    "DIRECT_CAUSAL_CLAIM",
    "CONTRIBUTORY_CAUSAL_CLAIM",
    "MEDIATED_CAUSAL_CLAIM",
    "PRECONDITION_CLAIM",
    "INHIBITORY_CAUSAL_CLAIM",
)

EVIDENCE_ROLES = (
    "SUPPORTING",
    "COUNTEREVIDENCE",
    "ALTERNATIVE_EXPLANATION",
)

RELATION_TYPE_BY_EVIDENCE_ROLE = {
    "SUPPORTING": "SUPPORTS",
    "COUNTEREVIDENCE": "CONTRADICTS",
    "ALTERNATIVE_EXPLANATION": "OFFERS_ALTERNATIVE",
}

EVIDENCE_REVIEW_STATUSES = (
    "REGISTERED_PRESENT",
    "REVIEWED_NONE_REGISTERED",
    "NOT_REVIEWED",
    "BLOCKED",
)

CLAIM_RECORD_STATUSES = (
    "RECORDED",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

REQUIRED_PREMISE_FIELDS = (
    "premise_id",
    "claim_id",
    "premise_text",
    "registration_status",
    "source_artifact_ids",
    "correlation_id",
    "research_run_id",
    "operator_review_status",
    "source_artifacts_preserved",
    "safety_flags",
)

REQUIRED_EVIDENCE_REFERENCE_FIELDS = (
    "evidence_ref_id",
    "claim_id",
    "artifact_id",
    "artifact_type",
    "evidence_role",
    "relation_type",
    "registration_status",
    "correlation_id",
    "research_run_id",
    "operator_review_status",
    "source_artifact_preserved",
    "safety_flags",
)

REQUIRED_CLAIM_RECORD_FIELDS = (
    "claim_id",
    "claim_text",
    "cause_ref_id",
    "effect_ref_id",
    "claim_type",
    "claim_registration_status",
    "premise_records",
    "evidence_references",
    "counterevidence_review_status",
    "alternative_explanation_review_status",
    "correlation_id",
    "research_run_id",
    "record_status",
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


class CausalSchemaViolation(ValueError):
    """Raised when a registered causal schema is invalid."""


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


def _valid_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _canonical_strings(
    values: Sequence[str],
) -> list[str]:
    return sorted(set(values))


def _valid_canonical_string_list(value: Any) -> bool:
    if not isinstance(value, list):
        return False

    if any(
        not isinstance(item, str) or not item.strip()
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


def build_registered_causal_premise_record(
    *,
    premise_id: str,
    claim_id: str,
    premise_text: str,
    registration_status: str,
    source_artifact_ids: Sequence[str],
    correlation_id: str,
    research_run_id: str,
) -> dict[str, Any]:
    """Build a registered premise without creating missing evidence."""
    return {
        "premise_id": premise_id,
        "claim_id": claim_id,
        "premise_text": premise_text,
        "registration_status": registration_status,
        "source_artifact_ids": _canonical_strings(
            source_artifact_ids
        ),
        "correlation_id": correlation_id,
        "research_run_id": research_run_id,
        "operator_review_status": "REQUIRED",
        "source_artifacts_preserved": True,
        "safety_flags": _safety_flags(),
    }


def validate_registered_causal_premise_record(
    record: object,
) -> list[str]:
    """Return deterministic premise validation errors."""
    if not isinstance(record, Mapping):
        return ["premise_record_must_be_mapping"]

    errors: list[str] = []

    if set(record.keys()) != set(REQUIRED_PREMISE_FIELDS):
        errors.append(
            "premise_fields_must_match_schema"
        )

    for field in (
        "premise_id",
        "claim_id",
        "correlation_id",
        "research_run_id",
    ):
        if not _valid_identifier(record.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_non_empty_string(
        record.get("premise_text")
    ):
        errors.append("premise_text_invalid")

    if record.get("registration_status") not in (
        REGISTRATION_STATUSES
    ):
        errors.append("registration_status_invalid")

    source_ids = record.get("source_artifact_ids")

    if not _valid_canonical_string_list(source_ids):
        errors.append("source_artifact_ids_invalid")
    elif not source_ids:
        errors.append("source_artifact_ids_empty")
    elif any(
        not _valid_identifier(source_id)
        for source_id in source_ids
    ):
        errors.append("source_artifact_id_invalid")

    if record.get("operator_review_status") != "REQUIRED":
        errors.append("operator_review_status_invalid")

    if record.get("source_artifacts_preserved") is not True:
        errors.append(
            "source_artifacts_preserved_must_be_true"
        )

    errors.extend(
        _validate_safety_flags(record.get("safety_flags"))
    )

    return errors


def build_registered_causal_evidence_reference(
    *,
    evidence_ref_id: str,
    claim_id: str,
    artifact_id: str,
    artifact_type: str,
    evidence_role: str,
    registration_status: str,
    correlation_id: str,
    research_run_id: str,
) -> dict[str, Any]:
    """Build a reference to registered evidence."""
    relation_type = RELATION_TYPE_BY_EVIDENCE_ROLE.get(
        evidence_role,
        "INVALID",
    )

    return {
        "evidence_ref_id": evidence_ref_id,
        "claim_id": claim_id,
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "evidence_role": evidence_role,
        "relation_type": relation_type,
        "registration_status": registration_status,
        "correlation_id": correlation_id,
        "research_run_id": research_run_id,
        "operator_review_status": "REQUIRED",
        "source_artifact_preserved": True,
        "safety_flags": _safety_flags(),
    }


def validate_registered_causal_evidence_reference(
    reference: object,
) -> list[str]:
    """Return deterministic evidence-reference validation errors."""
    if not isinstance(reference, Mapping):
        return ["evidence_reference_must_be_mapping"]

    errors: list[str] = []

    if set(reference.keys()) != set(
        REQUIRED_EVIDENCE_REFERENCE_FIELDS
    ):
        errors.append(
            "evidence_reference_fields_must_match_schema"
        )

    for field in (
        "evidence_ref_id",
        "claim_id",
        "artifact_id",
        "correlation_id",
        "research_run_id",
    ):
        if not _valid_identifier(reference.get(field)):
            errors.append(f"{field}_invalid")

    artifact_type = reference.get("artifact_type")

    if artifact_type not in ALLOWED_INPUT_ARTIFACT_TYPES:
        errors.append("artifact_type_not_registered")

    evidence_role = reference.get("evidence_role")

    if evidence_role not in EVIDENCE_ROLES:
        errors.append("evidence_role_invalid")
    else:
        expected_relation = (
            RELATION_TYPE_BY_EVIDENCE_ROLE[evidence_role]
        )

        if reference.get("relation_type") != expected_relation:
            errors.append("relation_type_mismatch")

    if reference.get("registration_status") not in (
        REGISTRATION_STATUSES
    ):
        errors.append("registration_status_invalid")

    if reference.get("operator_review_status") != "REQUIRED":
        errors.append("operator_review_status_invalid")

    if reference.get("source_artifact_preserved") is not True:
        errors.append(
            "source_artifact_preserved_must_be_true"
        )

    errors.extend(
        _validate_safety_flags(reference.get("safety_flags"))
    )

    return errors


def _clone_premise(
    premise: Mapping[str, Any],
) -> dict[str, Any]:
    cloned = dict(premise)
    cloned["source_artifact_ids"] = list(
        premise["source_artifact_ids"]
    )
    cloned["safety_flags"] = dict(premise["safety_flags"])
    return cloned


def _clone_evidence_reference(
    reference: Mapping[str, Any],
) -> dict[str, Any]:
    cloned = dict(reference)
    cloned["safety_flags"] = dict(
        reference["safety_flags"]
    )
    return cloned


def _canonical_premises(
    premise_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        [_clone_premise(item) for item in premise_records],
        key=lambda item: item["premise_id"],
    )


def _canonical_evidence_references(
    references: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    return sorted(
        [
            _clone_evidence_reference(item)
            for item in references
        ],
        key=lambda item: item["evidence_ref_id"],
    )


def _role_count(
    references: Sequence[Mapping[str, Any]],
    role: str,
) -> int:
    return sum(
        1
        for reference in references
        if reference.get("evidence_role") == role
    )


def _derive_reason_codes(
    *,
    claim_registration_status: str,
    premise_records: Sequence[Mapping[str, Any]],
    evidence_references: Sequence[Mapping[str, Any]],
    counterevidence_review_status: str,
    alternative_explanation_review_status: str,
) -> list[str]:
    reasons: list[str] = []

    if claim_registration_status == "BLOCKED":
        reasons.append("CLAIM_REGISTRATION_BLOCKED")
    elif claim_registration_status == "REVIEW_REQUIRED":
        reasons.append("CLAIM_REGISTRATION_REVIEW_REQUIRED")

    if not premise_records:
        reasons.append("MISSING_REGISTERED_PREMISES")

    premise_statuses = {
        premise.get("registration_status")
        for premise in premise_records
    }

    if "BLOCKED" in premise_statuses:
        reasons.append("PREMISE_REGISTRATION_BLOCKED")
    elif "REVIEW_REQUIRED" in premise_statuses:
        reasons.append("PREMISE_REVIEW_REQUIRED")

    supporting_count = _role_count(
        evidence_references,
        "SUPPORTING",
    )

    if supporting_count == 0:
        reasons.append("MISSING_SUPPORTING_EVIDENCE")

    evidence_statuses = {
        reference.get("registration_status")
        for reference in evidence_references
    }

    if "BLOCKED" in evidence_statuses:
        reasons.append("EVIDENCE_REGISTRATION_BLOCKED")
    elif "REVIEW_REQUIRED" in evidence_statuses:
        reasons.append("EVIDENCE_REVIEW_REQUIRED")

    if counterevidence_review_status == "NOT_REVIEWED":
        reasons.append("COUNTEREVIDENCE_NOT_REVIEWED")
    elif counterevidence_review_status == "BLOCKED":
        reasons.append("COUNTEREVIDENCE_REVIEW_BLOCKED")

    if alternative_explanation_review_status == "NOT_REVIEWED":
        reasons.append(
            "ALTERNATIVE_EXPLANATION_NOT_REVIEWED"
        )
    elif alternative_explanation_review_status == "BLOCKED":
        reasons.append(
            "ALTERNATIVE_EXPLANATION_REVIEW_BLOCKED"
        )

    return sorted(set(reasons))


def _derive_record_status(
    reason_codes: Sequence[str],
) -> str:
    blocked_codes = {
        "CLAIM_REGISTRATION_BLOCKED",
        "PREMISE_REGISTRATION_BLOCKED",
        "EVIDENCE_REGISTRATION_BLOCKED",
        "COUNTEREVIDENCE_REVIEW_BLOCKED",
        "ALTERNATIVE_EXPLANATION_REVIEW_BLOCKED",
    }

    if any(code in blocked_codes for code in reason_codes):
        return "BLOCKED"

    if reason_codes:
        return "REVIEW_REQUIRED"

    return "RECORDED"


def build_registered_causal_claim_record(
    *,
    claim_id: str,
    claim_text: str,
    cause_ref_id: str,
    effect_ref_id: str,
    claim_type: str,
    claim_registration_status: str,
    premise_records: Sequence[Mapping[str, Any]],
    evidence_references: Sequence[Mapping[str, Any]],
    counterevidence_review_status: str,
    alternative_explanation_review_status: str,
    correlation_id: str,
    research_run_id: str,
) -> dict[str, Any]:
    """Build a registered claim without deciding causal truth."""
    premise_errors: list[str] = []

    for index, premise in enumerate(premise_records):
        for error in validate_registered_causal_premise_record(
            premise
        ):
            premise_errors.append(
                f"premise:{index}:{error}"
            )

    evidence_errors: list[str] = []

    for index, reference in enumerate(evidence_references):
        for error in (
            validate_registered_causal_evidence_reference(
                reference
            )
        ):
            evidence_errors.append(
                f"evidence:{index}:{error}"
            )

    nested_errors = premise_errors + evidence_errors

    if nested_errors:
        raise CausalSchemaViolation(
            ";".join(nested_errors)
        )

    canonical_premises = _canonical_premises(
        premise_records
    )

    canonical_evidence = _canonical_evidence_references(
        evidence_references
    )

    reason_codes = _derive_reason_codes(
        claim_registration_status=(
            claim_registration_status
        ),
        premise_records=canonical_premises,
        evidence_references=canonical_evidence,
        counterevidence_review_status=(
            counterevidence_review_status
        ),
        alternative_explanation_review_status=(
            alternative_explanation_review_status
        ),
    )

    return {
        "claim_id": claim_id,
        "claim_text": claim_text,
        "cause_ref_id": cause_ref_id,
        "effect_ref_id": effect_ref_id,
        "claim_type": claim_type,
        "claim_registration_status": (
            claim_registration_status
        ),
        "premise_records": canonical_premises,
        "evidence_references": canonical_evidence,
        "counterevidence_review_status": (
            counterevidence_review_status
        ),
        "alternative_explanation_review_status": (
            alternative_explanation_review_status
        ),
        "correlation_id": correlation_id,
        "research_run_id": research_run_id,
        "record_status": _derive_record_status(
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


def _validate_nested_linkage(
    *,
    claim_id: Any,
    correlation_id: Any,
    research_run_id: Any,
    premise_records: Sequence[Mapping[str, Any]],
    evidence_references: Sequence[Mapping[str, Any]],
) -> list[str]:
    errors: list[str] = []

    for index, premise in enumerate(premise_records):
        if premise.get("claim_id") != claim_id:
            errors.append(
                f"premise:{index}:claim_id_mismatch"
            )

        if premise.get("correlation_id") != correlation_id:
            errors.append(
                f"premise:{index}:correlation_id_mismatch"
            )

        if premise.get("research_run_id") != research_run_id:
            errors.append(
                f"premise:{index}:research_run_id_mismatch"
            )

    for index, reference in enumerate(evidence_references):
        if reference.get("claim_id") != claim_id:
            errors.append(
                f"evidence:{index}:claim_id_mismatch"
            )

        if reference.get("correlation_id") != correlation_id:
            errors.append(
                f"evidence:{index}:correlation_id_mismatch"
            )

        if reference.get("research_run_id") != research_run_id:
            errors.append(
                f"evidence:{index}:research_run_id_mismatch"
            )

    return errors


def _validate_review_status_consistency(
    *,
    evidence_references: Sequence[Mapping[str, Any]],
    counterevidence_review_status: Any,
    alternative_explanation_review_status: Any,
) -> list[str]:
    errors: list[str] = []

    counter_count = _role_count(
        evidence_references,
        "COUNTEREVIDENCE",
    )

    alternative_count = _role_count(
        evidence_references,
        "ALTERNATIVE_EXPLANATION",
    )

    if counterevidence_review_status == "REGISTERED_PRESENT":
        if counter_count == 0:
            errors.append(
                "counterevidence_status_requires_reference"
            )
    elif counterevidence_review_status == (
        "REVIEWED_NONE_REGISTERED"
    ):
        if counter_count != 0:
            errors.append(
                "counterevidence_none_status_conflicts_with_reference"
            )
    elif counter_count != 0:
        errors.append(
            "counterevidence_reference_requires_present_status"
        )

    if alternative_explanation_review_status == (
        "REGISTERED_PRESENT"
    ):
        if alternative_count == 0:
            errors.append(
                "alternative_status_requires_reference"
            )
    elif alternative_explanation_review_status == (
        "REVIEWED_NONE_REGISTERED"
    ):
        if alternative_count != 0:
            errors.append(
                "alternative_none_status_conflicts_with_reference"
            )
    elif alternative_count != 0:
        errors.append(
            "alternative_reference_requires_present_status"
        )

    return errors


def validate_registered_causal_claim_record(
    record: object,
) -> list[str]:
    """Return deterministic registered-claim validation errors."""
    if not isinstance(record, Mapping):
        return ["claim_record_must_be_mapping"]

    errors: list[str] = []

    if set(record.keys()) != set(
        REQUIRED_CLAIM_RECORD_FIELDS
    ):
        errors.append(
            "claim_record_fields_must_match_schema"
        )

    for field in (
        "claim_id",
        "cause_ref_id",
        "effect_ref_id",
        "correlation_id",
        "research_run_id",
    ):
        if not _valid_identifier(record.get(field)):
            errors.append(f"{field}_invalid")

    if not _valid_non_empty_string(record.get("claim_text")):
        errors.append("claim_text_invalid")

    if record.get("cause_ref_id") == record.get(
        "effect_ref_id"
    ):
        errors.append("cause_and_effect_must_differ")

    if record.get("claim_type") not in CLAIM_TYPES:
        errors.append("claim_type_invalid")

    claim_registration_status = record.get(
        "claim_registration_status"
    )

    if claim_registration_status not in (
        REGISTRATION_STATUSES
    ):
        errors.append(
            "claim_registration_status_invalid"
        )

    counter_status = record.get(
        "counterevidence_review_status"
    )

    if counter_status not in EVIDENCE_REVIEW_STATUSES:
        errors.append(
            "counterevidence_review_status_invalid"
        )

    alternative_status = record.get(
        "alternative_explanation_review_status"
    )

    if alternative_status not in EVIDENCE_REVIEW_STATUSES:
        errors.append(
            "alternative_explanation_review_status_invalid"
        )

    premise_records = record.get("premise_records")

    if not isinstance(premise_records, list):
        errors.append("premise_records_must_be_list")
        premise_records = []
    else:
        for index, premise in enumerate(premise_records):
            for error in (
                validate_registered_causal_premise_record(
                    premise
                )
            ):
                errors.append(
                    f"premise:{index}:{error}"
                )

    evidence_references = record.get(
        "evidence_references"
    )

    if not isinstance(evidence_references, list):
        errors.append(
            "evidence_references_must_be_list"
        )
        evidence_references = []
    else:
        for index, reference in enumerate(
            evidence_references
        ):
            for error in (
                validate_registered_causal_evidence_reference(
                    reference
                )
            ):
                errors.append(
                    f"evidence:{index}:{error}"
                )

    valid_premises = [
        premise
        for premise in premise_records
        if isinstance(premise, Mapping)
    ]

    valid_evidence = [
        reference
        for reference in evidence_references
        if isinstance(reference, Mapping)
    ]

    if len(valid_premises) == len(premise_records):
        if premise_records != _canonical_premises(
            valid_premises
        ):
            errors.append(
                "premise_records_must_be_canonical"
            )

    if len(valid_evidence) == len(evidence_references):
        if evidence_references != (
            _canonical_evidence_references(
                valid_evidence
            )
        ):
            errors.append(
                "evidence_references_must_be_canonical"
            )

    premise_ids = [
        premise.get("premise_id")
        for premise in valid_premises
    ]

    if len(premise_ids) != len(set(premise_ids)):
        errors.append("premise_ids_must_be_unique")

    evidence_ids = [
        reference.get("evidence_ref_id")
        for reference in valid_evidence
    ]

    if len(evidence_ids) != len(set(evidence_ids)):
        errors.append(
            "evidence_ref_ids_must_be_unique"
        )

    errors.extend(
        _validate_nested_linkage(
            claim_id=record.get("claim_id"),
            correlation_id=record.get("correlation_id"),
            research_run_id=record.get("research_run_id"),
            premise_records=valid_premises,
            evidence_references=valid_evidence,
        )
    )

    if (
        counter_status in EVIDENCE_REVIEW_STATUSES
        and alternative_status in EVIDENCE_REVIEW_STATUSES
    ):
        errors.extend(
            _validate_review_status_consistency(
                evidence_references=valid_evidence,
                counterevidence_review_status=counter_status,
                alternative_explanation_review_status=(
                    alternative_status
                ),
            )
        )

    if claim_registration_status in REGISTRATION_STATUSES:
        expected_reasons = _derive_reason_codes(
            claim_registration_status=(
                claim_registration_status
            ),
            premise_records=valid_premises,
            evidence_references=valid_evidence,
            counterevidence_review_status=counter_status,
            alternative_explanation_review_status=(
                alternative_status
            ),
        )

        expected_record_status = _derive_record_status(
            expected_reasons
        )

        if record.get("reason_codes") != expected_reasons:
            errors.append("reason_codes_mismatch")

        if record.get("record_status") not in (
            CLAIM_RECORD_STATUSES
        ):
            errors.append("record_status_invalid")
        elif record.get("record_status") != (
            expected_record_status
        ):
            errors.append("record_status_mismatch")

    if record.get("causal_truth_status") != "UNDETERMINED":
        errors.append("causal_truth_status_invalid")

    if record.get("probability_status") != "NOT_ASSIGNED":
        errors.append("probability_status_invalid")

    if record.get("winner_status") != "NOT_SELECTED":
        errors.append("winner_status_invalid")

    if record.get("operator_review_status") != "REQUIRED":
        errors.append("operator_review_status_invalid")

    if record.get("source_artifacts_preserved") is not True:
        errors.append(
            "source_artifacts_preserved_must_be_true"
        )

    if record.get("original_conclusions_preserved") is not True:
        errors.append(
            "original_conclusions_preserved_must_be_true"
        )

    errors.extend(
        _validate_safety_flags(record.get("safety_flags"))
    )

    return errors
