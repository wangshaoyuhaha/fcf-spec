"""Planning-only operator gate and failure-control roadmap."""

import re
from typing import Any, Mapping

from .contract import (
    REQUIRED_FALSE_FLAGS,
    REQUIRED_TRUE_FLAGS,
    ROADMAP_MODE,
)
from .dag_plan import (
    DAG_STATUSES,
    validate_deterministic_governance_dag_plan,
)


STAGE_ID = "AI-ORCHESTRATION-ROADMAP-D4"
GATE_PLAN_VERSION = "1.0.0"

GATE_TYPE_BY_EDGE_TYPE = {
    "DATA_DEPENDENCY": "ARTIFACT_REVIEW",
    "GOVERNANCE_EVIDENCE": "GOVERNANCE_REVIEW",
    "VERSION_GUARD": "VERSION_REVIEW",
    "VALIDATION_GATE": "VALIDATION_REVIEW",
    "TRACEABILITY": "TRACEABILITY_REVIEW",
    "OPERATOR_GATE": "FINAL_OPERATOR_REVIEW",
}

FAILURE_STATES = (
    "NONE",
    "INPUT_MISSING",
    "VERSION_MISMATCH",
    "VALIDATION_FAILED",
    "TIMEOUT_RECORDED",
    "DEPENDENCY_BLOCKED",
    "OPERATOR_REJECTED",
)

GATE_STATUSES = (
    "PLANNED",
    "REVIEW_REQUIRED",
    "BLOCKED",
)

TIMEOUT_POLICY = (
    "REGISTERED_TIMEOUT_REQUIRES_MANUAL_REVIEW"
)
RETRY_POLICY = "NO_AUTOMATIC_RETRY"

DEGRADATION_POLICIES = (
    "NO_DEGRADATION",
    "READ_ONLY_REVIEW_HOLD",
    "STOP_AND_HOLD",
)

GATE_PLAN_STATUSES = (
    "READY_FOR_ROLE_PLANNING",
    "REVIEW_REQUIRED",
    "BLOCKED",
    "INVALID",
)

REQUIRED_GATE_FIELDS = (
    "gate_id",
    "edge_id",
    "edge_type",
    "gate_type",
    "source_node_id",
    "target_node_id",
    "blocking",
    "gate_status",
    "failure_state",
    "timeout_policy",
    "retry_policy",
    "degradation_policy",
    "operator_review_status",
    "runtime_execution_status",
    "safety_flags",
)

REQUIRED_GATE_PLAN_FIELDS = (
    "gate_plan_id",
    "source_dag_plan_id",
    "source_dag_status",
    "gates",
    "failure_summary",
    "reason_codes",
    "gate_plan_status",
    "operator_review_status",
    "roadmap_mode",
    "runtime_execution_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class GatePlanViolation(ValueError):
    """Raised when a planning-only gate plan is invalid."""


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
        errors.append("safety_flag_names_must_match_contract")

    return errors


def _degradation_policy(failure_state: str) -> str:
    if failure_state == "NONE":
        return "NO_DEGRADATION"

    if failure_state in (
        "INPUT_MISSING",
        "TIMEOUT_RECORDED",
    ):
        return "READ_ONLY_REVIEW_HOLD"

    return "STOP_AND_HOLD"


def _gate_status(failure_state: str) -> str:
    if failure_state == "NONE":
        return "PLANNED"

    if failure_state in (
        "INPUT_MISSING",
        "TIMEOUT_RECORDED",
    ):
        return "REVIEW_REQUIRED"

    return "BLOCKED"


def _build_gate(
    *,
    edge: Mapping[str, Any],
    failure_state: str,
) -> dict[str, Any]:
    if failure_state not in FAILURE_STATES:
        raise GatePlanViolation(
            f"failure_state_invalid:{failure_state}"
        )

    edge_type = str(edge["edge_type"])

    if edge_type not in GATE_TYPE_BY_EDGE_TYPE:
        raise GatePlanViolation(
            f"edge_type_invalid:{edge_type}"
        )

    edge_id = str(edge["edge_id"])

    return {
        "gate_id": f"gate:{edge_id}",
        "edge_id": edge_id,
        "edge_type": edge_type,
        "gate_type": GATE_TYPE_BY_EDGE_TYPE[edge_type],
        "source_node_id": str(edge["source_node_id"]),
        "target_node_id": str(edge["target_node_id"]),
        "blocking": True,
        "gate_status": _gate_status(failure_state),
        "failure_state": failure_state,
        "timeout_policy": TIMEOUT_POLICY,
        "retry_policy": RETRY_POLICY,
        "degradation_policy": _degradation_policy(
            failure_state
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "runtime_execution_status": "NOT_ALLOWED",
        "safety_flags": _safety_flags(),
    }


def _canonical_gates(
    gates: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    cloned: list[dict[str, Any]] = []

    for gate in gates:
        item = dict(gate)
        item["safety_flags"] = dict(gate["safety_flags"])
        cloned.append(item)

    return sorted(
        cloned,
        key=lambda item: (
            str(item["edge_id"]),
            str(item["gate_id"]),
        ),
    )


def _failure_summary(
    gates: list[Mapping[str, Any]],
) -> dict[str, int]:
    summary = {
        failure_state: 0
        for failure_state in FAILURE_STATES
    }

    for gate in gates:
        summary[str(gate["failure_state"])] += 1

    return summary


def _reason_codes(
    *,
    source_dag_status: str,
    gates: list[Mapping[str, Any]],
) -> list[str]:
    reasons: set[str] = set()

    if source_dag_status == "BLOCKED":
        reasons.add("SOURCE_DAG_BLOCKED")
    elif source_dag_status == "INVALID":
        reasons.add("SOURCE_DAG_INVALID")
    elif source_dag_status != "READY_FOR_GATE_PLANNING":
        reasons.add("SOURCE_DAG_REVIEW_REQUIRED")

    failure_states = {
        str(gate["failure_state"])
        for gate in gates
        if gate["failure_state"] != "NONE"
    }

    if failure_states:
        reasons.add("REGISTERED_FAILURE_PRESENT")

        for failure_state in failure_states:
            reasons.add(
                f"REGISTERED_FAILURE_{failure_state}"
            )
    else:
        reasons.add("NO_REGISTERED_FAILURE")

    return sorted(reasons)


def _derive_plan_status(
    *,
    source_dag_status: str,
    gates: list[Mapping[str, Any]],
) -> str:
    if source_dag_status == "BLOCKED":
        return "BLOCKED"

    if source_dag_status == "INVALID":
        return "INVALID"

    if source_dag_status != "READY_FOR_GATE_PLANNING":
        return "REVIEW_REQUIRED"

    if any(
        gate["failure_state"] != "NONE"
        for gate in gates
    ):
        return "REVIEW_REQUIRED"

    return "READY_FOR_ROLE_PLANNING"


def build_governance_gate_plan(
    *,
    gate_plan_id: str,
    dag_plan: Mapping[str, Any],
    registered_failure_states: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """Build non-executable gate and failure-control planning."""
    dag_errors = validate_deterministic_governance_dag_plan(
        dag_plan
    )

    if dag_errors:
        raise GatePlanViolation(";".join(dag_errors))

    failures = dict(registered_failure_states or {})
    edge_ids = {
        str(edge["edge_id"])
        for edge in dag_plan["edges"]
    }

    unknown_edge_ids = sorted(set(failures) - edge_ids)

    if unknown_edge_ids:
        raise GatePlanViolation(
            "unknown_failure_edge_ids:"
            + ",".join(unknown_edge_ids)
        )

    gates = [
        _build_gate(
            edge=edge,
            failure_state=failures.get(
                str(edge["edge_id"]),
                "NONE",
            ),
        )
        for edge in dag_plan["edges"]
    ]

    canonical_gates = _canonical_gates(gates)
    source_dag_status = str(dag_plan["dag_status"])

    return {
        "gate_plan_id": gate_plan_id,
        "source_dag_plan_id": dag_plan["dag_plan_id"],
        "source_dag_status": source_dag_status,
        "gates": canonical_gates,
        "failure_summary": _failure_summary(
            canonical_gates
        ),
        "reason_codes": _reason_codes(
            source_dag_status=source_dag_status,
            gates=canonical_gates,
        ),
        "gate_plan_status": _derive_plan_status(
            source_dag_status=source_dag_status,
            gates=canonical_gates,
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "roadmap_mode": ROADMAP_MODE,
        "runtime_execution_status": "NOT_ALLOWED",
        "safety_flags": _safety_flags(),
    }


def _validate_gate(gate: object) -> list[str]:
    if not isinstance(gate, Mapping):
        return ["gate_must_be_mapping"]

    errors: list[str] = []

    if set(gate.keys()) != set(REQUIRED_GATE_FIELDS):
        errors.append("gate_fields_must_match_schema")

    for field in (
        "gate_id",
        "edge_id",
        "source_node_id",
        "target_node_id",
    ):
        if not _valid_identifier(gate.get(field)):
            errors.append(f"{field}_invalid")

    edge_type = gate.get("edge_type")

    if edge_type not in GATE_TYPE_BY_EDGE_TYPE:
        errors.append("edge_type_invalid")
    elif gate.get("gate_type") != (
        GATE_TYPE_BY_EDGE_TYPE[edge_type]
    ):
        errors.append("gate_type_mismatch")

    if gate.get("blocking") is not True:
        errors.append("blocking_must_be_true")

    failure_state = gate.get("failure_state")

    if failure_state not in FAILURE_STATES:
        errors.append("failure_state_invalid")
    else:
        if gate.get("gate_status") != _gate_status(
            failure_state
        ):
            errors.append("gate_status_mismatch")

        if gate.get("degradation_policy") != (
            _degradation_policy(failure_state)
        ):
            errors.append("degradation_policy_mismatch")

    if gate.get("gate_status") not in GATE_STATUSES:
        errors.append("gate_status_invalid")

    if gate.get("timeout_policy") != TIMEOUT_POLICY:
        errors.append("timeout_policy_invalid")

    if gate.get("retry_policy") != RETRY_POLICY:
        errors.append("automatic_retry_must_not_be_allowed")

    if gate.get("degradation_policy") not in (
        DEGRADATION_POLICIES
    ):
        errors.append("degradation_policy_invalid")

    if gate.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if gate.get("runtime_execution_status") != "NOT_ALLOWED":
        errors.append("runtime_execution_must_not_be_allowed")

    errors.extend(
        _validate_safety_flags(gate.get("safety_flags"))
    )

    return errors


def validate_governance_gate_plan(
    plan: object,
) -> list[str]:
    """Return deterministic D4 gate-plan validation errors."""
    if not isinstance(plan, Mapping):
        return ["gate_plan_must_be_mapping"]

    errors: list[str] = []

    if set(plan.keys()) != set(REQUIRED_GATE_PLAN_FIELDS):
        errors.append("gate_plan_fields_must_match_schema")

    for field in (
        "gate_plan_id",
        "source_dag_plan_id",
    ):
        if not _valid_identifier(plan.get(field)):
            errors.append(f"{field}_invalid")

    source_dag_status = plan.get("source_dag_status")

    if source_dag_status not in DAG_STATUSES:
        errors.append("source_dag_status_invalid")

    gates = plan.get("gates")

    if not isinstance(gates, list):
        errors.append("gates_must_be_list")
        gates = []
    else:
        for index, gate in enumerate(gates):
            for gate_error in _validate_gate(gate):
                errors.append(
                    f"gate:{index}:{gate_error}"
                )

    valid_gates = [
        gate
        for gate in gates
        if isinstance(gate, Mapping)
    ]

    if gates != _canonical_gates(valid_gates):
        errors.append("gates_must_be_canonical")

    gate_ids = [
        str(gate.get("gate_id"))
        for gate in valid_gates
    ]
    edge_ids = [
        str(gate.get("edge_id"))
        for gate in valid_gates
    ]

    if len(gate_ids) != len(set(gate_ids)):
        errors.append("gate_ids_must_be_unique")

    if len(edge_ids) != len(set(edge_ids)):
        errors.append("edge_ids_must_be_unique")

    summary = plan.get("failure_summary")
    expected_summary = _failure_summary(valid_gates)

    if not isinstance(summary, Mapping):
        errors.append("failure_summary_must_be_mapping")
    else:
        if set(summary.keys()) != set(FAILURE_STATES):
            errors.append(
                "failure_summary_fields_must_match_schema"
            )

        for state in FAILURE_STATES:
            value = summary.get(state)

            if (
                not isinstance(value, int)
                or isinstance(value, bool)
                or value < 0
            ):
                errors.append(
                    f"failure_summary_{state}_invalid"
                )

        if dict(summary) != expected_summary:
            errors.append("failure_summary_mismatch")

    expected_reasons = _reason_codes(
        source_dag_status=str(source_dag_status),
        gates=valid_gates,
    )

    if plan.get("reason_codes") != expected_reasons:
        errors.append("reason_codes_mismatch")

    expected_status = _derive_plan_status(
        source_dag_status=str(source_dag_status),
        gates=valid_gates,
    )

    if plan.get("gate_plan_status") not in (
        GATE_PLAN_STATUSES
    ):
        errors.append("gate_plan_status_invalid")
    elif plan.get("gate_plan_status") != expected_status:
        errors.append("gate_plan_status_mismatch")

    if plan.get("operator_review_status") != (
        "REVIEW_REQUIRED"
    ):
        errors.append("operator_review_status_invalid")

    if plan.get("roadmap_mode") != ROADMAP_MODE:
        errors.append("roadmap_mode_invalid")

    if plan.get("runtime_execution_status") != "NOT_ALLOWED":
        errors.append("runtime_execution_must_not_be_allowed")

    errors.extend(
        _validate_safety_flags(plan.get("safety_flags"))
    )

    return errors
