"""Readiness-only timeout, retry, fallback, and cost contracts."""

import re
from typing import Any, Mapping, Sequence

from .contract import (
    APP_ID,
    READINESS_MODE,
    REQUIRED_FALSE_FLAGS,
    REQUIRED_POLICY_IDENTIFIERS,
    REQUIRED_TRUE_FLAGS,
)
from .routing_eligibility import (
    validate_routing_eligibility_contract,
)


STAGE_ID = "AI-ORCHESTRATION-RUNTIME-READINESS-D4"
RUNTIME_LIMIT_BUNDLE_VERSION = "1.0.0"

RUNTIME_LIMIT_STATUSES = (
    "READY_FOR_POLICY_CONFIG_LINKAGE",
    "BLOCKED",
    "DEGRADED",
)

TIMEOUT_CONTRACT_VERSION = "1.0.0"
RETRY_CONTRACT_VERSION = "1.0.0"
FALLBACK_CONTRACT_VERSION = "1.0.0"
COST_CONTRACT_VERSION = "1.0.0"

RUNTIME_LIMIT_POLICY_IDENTIFIERS = (
    "FCF.POLICY.RUNTIME.COST.HARD_LIMIT_REQUIRED",
    "FCF.POLICY.RUNTIME.COST.NO_AUTOMATIC_OVERRIDE",
    "FCF.POLICY.RUNTIME.FALLBACK.NO_AUTOMATIC_SWITCH",
    "FCF.POLICY.RUNTIME.FALLBACK.OPERATOR_REVIEW_REQUIRED",
    "FCF.POLICY.RUNTIME.RETRY.BOUNDED_ATTEMPTS_REQUIRED",
    "FCF.POLICY.RUNTIME.RETRY.NO_AUTOMATIC_EXECUTION",
    "FCF.POLICY.RUNTIME.TIMEOUT.FAIL_CLOSED_REQUIRED",
    "FCF.POLICY.RUNTIME.TIMEOUT.TOTAL_LIMIT_REQUIRED",
)

REQUIRED_TIMEOUT_FIELDS = (
    "contract_type",
    "contract_version",
    "connect_timeout_ms",
    "response_timeout_ms",
    "total_timeout_ms",
    "timeout_action",
    "automatic_timeout_recovery_status",
    "runtime_enforcement_status",
)

REQUIRED_RETRY_FIELDS = (
    "contract_type",
    "contract_version",
    "max_attempts",
    "backoff_ms",
    "retryable_failure_classes",
    "retry_action",
    "automatic_retry_status",
    "runtime_enforcement_status",
)

REQUIRED_FALLBACK_FIELDS = (
    "contract_type",
    "contract_version",
    "fallback_candidate_ids",
    "fallback_action",
    "operator_review_required",
    "automatic_fallback_status",
    "automatic_switching_status",
    "runtime_enforcement_status",
)

REQUIRED_COST_FIELDS = (
    "contract_type",
    "contract_version",
    "currency",
    "per_request_limit_microunits",
    "workflow_limit_microunits",
    "daily_limit_microunits",
    "unknown_cost_action",
    "limit_exceeded_action",
    "automatic_cost_override_status",
    "runtime_enforcement_status",
)

REQUIRED_BUNDLE_FIELDS = (
    "runtime_limit_bundle_id",
    "app_id",
    "stage_id",
    "runtime_limit_bundle_version",
    "readiness_mode",
    "source_routing_contract_id",
    "policy_identifiers",
    "config_snapshot_linkage_status",
    "timeout_contract",
    "retry_contract",
    "fallback_contract",
    "cost_contract",
    "model_invocation_status",
    "prompt_execution_status",
    "automatic_routing_status",
    "automatic_fallback_status",
    "automatic_retry_status",
    "runtime_execution_status",
    "bundle_status",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)

_CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")


class RuntimeLimitContractViolation(ValueError):
    """Raised when readiness-only runtime limit contracts are invalid."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def _canonical_strings(values: Sequence[str]) -> list[str]:
    return sorted(set(values))


def _valid_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and _IDENTIFIER_PATTERN.fullmatch(value) is not None
    )


def _valid_non_negative_int(value: Any) -> bool:
    return (
        isinstance(value, int)
        and not isinstance(value, bool)
        and value >= 0
    )


def _valid_positive_int(value: Any) -> bool:
    return _valid_non_negative_int(value) and value > 0


def _valid_canonical_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and all(
            isinstance(item, str) and item.strip()
            for item in value
        )
        and value == sorted(set(value))
    )


def _runtime_limit_policy_identifiers() -> list[str]:
    return _canonical_strings(
        REQUIRED_POLICY_IDENTIFIERS
        + RUNTIME_LIMIT_POLICY_IDENTIFIERS
    )


def build_timeout_contract(
    *,
    connect_timeout_ms: int,
    response_timeout_ms: int,
    total_timeout_ms: int,
) -> dict[str, Any]:
    """Build a non-executable timeout contract."""
    values = (
        connect_timeout_ms,
        response_timeout_ms,
        total_timeout_ms,
    )
    if not all(_valid_positive_int(value) for value in values):
        raise RuntimeLimitContractViolation(
            "timeout_values_must_be_positive_integers"
        )

    if total_timeout_ms < (
        connect_timeout_ms + response_timeout_ms
    ):
        raise RuntimeLimitContractViolation(
            "total_timeout_ms_too_small"
        )

    return {
        "contract_type": "TIMEOUT_CONTRACT",
        "contract_version": TIMEOUT_CONTRACT_VERSION,
        "connect_timeout_ms": connect_timeout_ms,
        "response_timeout_ms": response_timeout_ms,
        "total_timeout_ms": total_timeout_ms,
        "timeout_action": "BLOCK_AND_REQUIRE_OPERATOR_REVIEW",
        "automatic_timeout_recovery_status": "NOT_ALLOWED",
        "runtime_enforcement_status": "NOT_ACTIVE",
    }


def build_retry_contract(
    *,
    max_attempts: int,
    backoff_ms: Sequence[int],
    retryable_failure_classes: Sequence[str],
) -> dict[str, Any]:
    """Build a non-executable bounded retry contract."""
    if (
        not _valid_non_negative_int(max_attempts)
        or max_attempts > 3
    ):
        raise RuntimeLimitContractViolation(
            "max_attempts_must_be_between_0_and_3"
        )

    if not isinstance(backoff_ms, Sequence) or isinstance(
        backoff_ms,
        (str, bytes),
    ):
        raise RuntimeLimitContractViolation(
            "backoff_ms_must_be_sequence"
        )

    canonical_backoff = list(backoff_ms)
    if (
        len(canonical_backoff) != max_attempts
        or not all(
            _valid_positive_int(value)
            for value in canonical_backoff
        )
        or canonical_backoff != sorted(canonical_backoff)
    ):
        raise RuntimeLimitContractViolation(
            "backoff_ms_invalid"
        )

    if not isinstance(
        retryable_failure_classes,
        Sequence,
    ) or isinstance(
        retryable_failure_classes,
        (str, bytes),
    ):
        raise RuntimeLimitContractViolation(
            "retryable_failure_classes_must_be_sequence"
        )

    canonical_failures = _canonical_strings(
        list(retryable_failure_classes)
    )
    if any(
        not _valid_identifier(value)
        for value in canonical_failures
    ):
        raise RuntimeLimitContractViolation(
            "retryable_failure_classes_invalid"
        )

    return {
        "contract_type": "RETRY_CONTRACT",
        "contract_version": RETRY_CONTRACT_VERSION,
        "max_attempts": max_attempts,
        "backoff_ms": canonical_backoff,
        "retryable_failure_classes": canonical_failures,
        "retry_action": "REQUIRE_OPERATOR_REVIEW_BEFORE_EXECUTION",
        "automatic_retry_status": "NOT_ALLOWED",
        "runtime_enforcement_status": "NOT_ACTIVE",
    }


def build_fallback_contract(
    *,
    fallback_candidate_ids: Sequence[str],
) -> dict[str, Any]:
    """Build a non-executable fallback review contract."""
    if not isinstance(
        fallback_candidate_ids,
        Sequence,
    ) or isinstance(
        fallback_candidate_ids,
        (str, bytes),
    ):
        raise RuntimeLimitContractViolation(
            "fallback_candidate_ids_must_be_sequence"
        )

    canonical_ids = _canonical_strings(
        list(fallback_candidate_ids)
    )
    if any(
        not _valid_identifier(value)
        for value in canonical_ids
    ):
        raise RuntimeLimitContractViolation(
            "fallback_candidate_ids_invalid"
        )

    return {
        "contract_type": "FALLBACK_CONTRACT",
        "contract_version": FALLBACK_CONTRACT_VERSION,
        "fallback_candidate_ids": canonical_ids,
        "fallback_action": "PRESENT_OPTIONS_TO_OPERATOR",
        "operator_review_required": True,
        "automatic_fallback_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "runtime_enforcement_status": "NOT_ACTIVE",
    }


def build_cost_contract(
    *,
    currency: str,
    per_request_limit_microunits: int,
    workflow_limit_microunits: int,
    daily_limit_microunits: int,
) -> dict[str, Any]:
    """Build a non-executable deterministic cost contract."""
    if (
        not isinstance(currency, str)
        or _CURRENCY_PATTERN.fullmatch(currency) is None
    ):
        raise RuntimeLimitContractViolation(
            "currency_must_be_iso_4217_code"
        )

    limits = (
        per_request_limit_microunits,
        workflow_limit_microunits,
        daily_limit_microunits,
    )
    if not all(_valid_positive_int(value) for value in limits):
        raise RuntimeLimitContractViolation(
            "cost_limits_must_be_positive_integers"
        )

    if not (
        per_request_limit_microunits
        <= workflow_limit_microunits
        <= daily_limit_microunits
    ):
        raise RuntimeLimitContractViolation(
            "cost_limit_order_invalid"
        )

    return {
        "contract_type": "COST_CONTRACT",
        "contract_version": COST_CONTRACT_VERSION,
        "currency": currency,
        "per_request_limit_microunits": (
            per_request_limit_microunits
        ),
        "workflow_limit_microunits": (
            workflow_limit_microunits
        ),
        "daily_limit_microunits": (
            daily_limit_microunits
        ),
        "unknown_cost_action": "BLOCK",
        "limit_exceeded_action": "BLOCK",
        "automatic_cost_override_status": "NOT_ALLOWED",
        "runtime_enforcement_status": "NOT_ACTIVE",
    }


def _clone_contract(
    contract: Mapping[str, Any],
) -> dict[str, Any]:
    cloned = dict(contract)

    if "backoff_ms" in cloned:
        cloned["backoff_ms"] = list(cloned["backoff_ms"])

    if "retryable_failure_classes" in cloned:
        cloned["retryable_failure_classes"] = list(
            cloned["retryable_failure_classes"]
        )

    if "fallback_candidate_ids" in cloned:
        cloned["fallback_candidate_ids"] = list(
            cloned["fallback_candidate_ids"]
        )

    return cloned


def _derive_bundle_status(
    routing_status: str,
) -> str:
    if routing_status == "BLOCKED":
        return "BLOCKED"

    if routing_status == "DEGRADED":
        return "DEGRADED"

    return "READY_FOR_POLICY_CONFIG_LINKAGE"


def build_runtime_limit_contract_bundle(
    *,
    runtime_limit_bundle_id: str,
    routing_contract: Mapping[str, Any],
    timeout_contract: Mapping[str, Any],
    retry_contract: Mapping[str, Any],
    fallback_contract: Mapping[str, Any],
    cost_contract: Mapping[str, Any],
) -> dict[str, Any]:
    """Build deterministic non-executable D4 limit contracts."""
    routing_errors = validate_routing_eligibility_contract(
        routing_contract
    )
    if routing_errors:
        raise RuntimeLimitContractViolation(
            ";".join(routing_errors)
        )

    if not _valid_identifier(runtime_limit_bundle_id):
        raise RuntimeLimitContractViolation(
            "runtime_limit_bundle_id_invalid"
        )

    validators = (
        validate_timeout_contract,
        validate_retry_contract,
        validate_fallback_contract,
        validate_cost_contract,
    )
    contracts = (
        timeout_contract,
        retry_contract,
        fallback_contract,
        cost_contract,
    )

    for validator, contract in zip(validators, contracts):
        errors = validator(contract)
        if errors:
            raise RuntimeLimitContractViolation(
                ";".join(errors)
            )

    candidate_ids = {
        str(candidate["candidate_id"])
        for candidate in routing_contract["candidates"]
    }
    fallback_ids = set(
        fallback_contract["fallback_candidate_ids"]
    )
    if not fallback_ids.issubset(candidate_ids):
        raise RuntimeLimitContractViolation(
            "fallback_candidate_not_in_routing_contract"
        )

    routing_status = str(
        routing_contract["routing_contract_status"]
    )

    return {
        "runtime_limit_bundle_id": runtime_limit_bundle_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "runtime_limit_bundle_version": (
            RUNTIME_LIMIT_BUNDLE_VERSION
        ),
        "readiness_mode": READINESS_MODE,
        "source_routing_contract_id": (
            routing_contract["routing_contract_id"]
        ),
        "policy_identifiers": (
            _runtime_limit_policy_identifiers()
        ),
        "config_snapshot_linkage_status": (
            "REQUIRED_NOT_ACTIVE"
        ),
        "timeout_contract": _clone_contract(
            timeout_contract
        ),
        "retry_contract": _clone_contract(retry_contract),
        "fallback_contract": _clone_contract(
            fallback_contract
        ),
        "cost_contract": _clone_contract(cost_contract),
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_fallback_status": "NOT_ALLOWED",
        "automatic_retry_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "bundle_status": _derive_bundle_status(
            routing_status
        ),
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


def validate_timeout_contract(
    contract: object,
) -> list[str]:
    """Return deterministic timeout contract errors."""
    if not isinstance(contract, Mapping):
        return ["timeout_contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(REQUIRED_TIMEOUT_FIELDS):
        errors.append(
            "timeout_contract_fields_must_match_schema"
        )

    expected_scalars = {
        "contract_type": "TIMEOUT_CONTRACT",
        "contract_version": TIMEOUT_CONTRACT_VERSION,
        "timeout_action": (
            "BLOCK_AND_REQUIRE_OPERATOR_REVIEW"
        ),
        "automatic_timeout_recovery_status": (
            "NOT_ALLOWED"
        ),
        "runtime_enforcement_status": "NOT_ACTIVE",
    }
    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    values = (
        contract.get("connect_timeout_ms"),
        contract.get("response_timeout_ms"),
        contract.get("total_timeout_ms"),
    )
    if not all(_valid_positive_int(value) for value in values):
        errors.append(
            "timeout_values_must_be_positive_integers"
        )
    elif contract["total_timeout_ms"] < (
        contract["connect_timeout_ms"]
        + contract["response_timeout_ms"]
    ):
        errors.append("total_timeout_ms_too_small")

    return errors


def validate_retry_contract(
    contract: object,
) -> list[str]:
    """Return deterministic retry contract errors."""
    if not isinstance(contract, Mapping):
        return ["retry_contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(REQUIRED_RETRY_FIELDS):
        errors.append(
            "retry_contract_fields_must_match_schema"
        )

    expected_scalars = {
        "contract_type": "RETRY_CONTRACT",
        "contract_version": RETRY_CONTRACT_VERSION,
        "retry_action": (
            "REQUIRE_OPERATOR_REVIEW_BEFORE_EXECUTION"
        ),
        "automatic_retry_status": "NOT_ALLOWED",
        "runtime_enforcement_status": "NOT_ACTIVE",
    }
    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    max_attempts = contract.get("max_attempts")
    if (
        not _valid_non_negative_int(max_attempts)
        or max_attempts > 3
    ):
        errors.append(
            "max_attempts_must_be_between_0_and_3"
        )

    backoff = contract.get("backoff_ms")
    if (
        not isinstance(backoff, list)
        or not _valid_non_negative_int(max_attempts)
        or len(backoff) != max_attempts
        or not all(
            _valid_positive_int(value)
            for value in backoff
        )
        or backoff != sorted(backoff)
    ):
        errors.append("backoff_ms_invalid")

    if not _valid_canonical_string_list(
        contract.get("retryable_failure_classes")
    ):
        errors.append(
            "retryable_failure_classes_invalid"
        )

    return errors


def validate_fallback_contract(
    contract: object,
) -> list[str]:
    """Return deterministic fallback contract errors."""
    if not isinstance(contract, Mapping):
        return ["fallback_contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(
        REQUIRED_FALLBACK_FIELDS
    ):
        errors.append(
            "fallback_contract_fields_must_match_schema"
        )

    expected_scalars = {
        "contract_type": "FALLBACK_CONTRACT",
        "contract_version": FALLBACK_CONTRACT_VERSION,
        "fallback_action": "PRESENT_OPTIONS_TO_OPERATOR",
        "operator_review_required": True,
        "automatic_fallback_status": "NOT_ALLOWED",
        "automatic_switching_status": "NOT_ALLOWED",
        "runtime_enforcement_status": "NOT_ACTIVE",
    }
    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    fallback_ids = contract.get(
        "fallback_candidate_ids"
    )
    if (
        not _valid_canonical_string_list(fallback_ids)
        or any(
            not _valid_identifier(value)
            for value in fallback_ids
        )
    ):
        errors.append("fallback_candidate_ids_invalid")

    return errors


def validate_cost_contract(
    contract: object,
) -> list[str]:
    """Return deterministic cost contract errors."""
    if not isinstance(contract, Mapping):
        return ["cost_contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(REQUIRED_COST_FIELDS):
        errors.append(
            "cost_contract_fields_must_match_schema"
        )

    expected_scalars = {
        "contract_type": "COST_CONTRACT",
        "contract_version": COST_CONTRACT_VERSION,
        "unknown_cost_action": "BLOCK",
        "limit_exceeded_action": "BLOCK",
        "automatic_cost_override_status": (
            "NOT_ALLOWED"
        ),
        "runtime_enforcement_status": "NOT_ACTIVE",
    }
    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    currency = contract.get("currency")
    if (
        not isinstance(currency, str)
        or _CURRENCY_PATTERN.fullmatch(currency) is None
    ):
        errors.append("currency_invalid")

    limits = (
        contract.get("per_request_limit_microunits"),
        contract.get("workflow_limit_microunits"),
        contract.get("daily_limit_microunits"),
    )
    if not all(_valid_positive_int(value) for value in limits):
        errors.append(
            "cost_limits_must_be_positive_integers"
        )
    elif not (
        contract["per_request_limit_microunits"]
        <= contract["workflow_limit_microunits"]
        <= contract["daily_limit_microunits"]
    ):
        errors.append("cost_limit_order_invalid")

    return errors


def validate_runtime_limit_contract_bundle(
    bundle: object,
) -> list[str]:
    """Return deterministic D4 bundle errors."""
    if not isinstance(bundle, Mapping):
        return ["runtime_limit_bundle_must_be_mapping"]

    errors: list[str] = []

    if set(bundle.keys()) != set(REQUIRED_BUNDLE_FIELDS):
        errors.append(
            "runtime_limit_bundle_fields_must_match_schema"
        )

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "runtime_limit_bundle_version": (
            RUNTIME_LIMIT_BUNDLE_VERSION
        ),
        "readiness_mode": READINESS_MODE,
        "config_snapshot_linkage_status": (
            "REQUIRED_NOT_ACTIVE"
        ),
        "model_invocation_status": "NOT_ALLOWED",
        "prompt_execution_status": "NOT_ALLOWED",
        "automatic_routing_status": "NOT_ALLOWED",
        "automatic_fallback_status": "NOT_ALLOWED",
        "automatic_retry_status": "NOT_ALLOWED",
        "runtime_execution_status": "NOT_ALLOWED",
        "operator_review_status": "REVIEW_REQUIRED",
    }
    for field, expected in expected_scalars.items():
        if bundle.get(field) != expected:
            errors.append(f"{field}_invalid")

    for field in (
        "runtime_limit_bundle_id",
        "source_routing_contract_id",
    ):
        if not _valid_identifier(bundle.get(field)):
            errors.append(f"{field}_invalid")

    if bundle.get("policy_identifiers") != (
        _runtime_limit_policy_identifiers()
    ):
        errors.append("policy_identifiers_invalid")

    validators = {
        "timeout_contract": validate_timeout_contract,
        "retry_contract": validate_retry_contract,
        "fallback_contract": validate_fallback_contract,
        "cost_contract": validate_cost_contract,
    }
    for field, validator in validators.items():
        errors.extend(validator(bundle.get(field)))

    if bundle.get("bundle_status") not in (
        RUNTIME_LIMIT_STATUSES
    ):
        errors.append("bundle_status_invalid")

    errors.extend(
        _validate_safety_flags(
            bundle.get("safety_flags")
        )
    )

    return errors
