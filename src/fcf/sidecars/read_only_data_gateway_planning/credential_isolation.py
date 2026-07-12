"""Planning-only D4 credential-isolation boundary contract."""

import re
from collections.abc import Mapping
from typing import Any

APP_ID = "READ-ONLY-DATA-GATEWAY-PLANNING-APP-1"
STAGE_ID = "READ-ONLY-DATA-GATEWAY-PLANNING-D4"
CONTRACT_VERSION = "1.0.0"
PLANNING_MODE = "PLANNING_ONLY"

CREDENTIAL_OWNER = "ISOLATED_READ_ONLY_GATEWAY"

REQUIRED_TRUE_FLAGS = (
    "credential_isolation_required",
    "normalized_output_only",
    "operator_review_required",
    "read_only_scope_required",
)

REQUIRED_FALSE_FLAGS = (
    "balance_access_allowed",
    "credential_material_allowed_in_fcf",
    "credential_material_allowed_in_model_input",
    "credential_material_allowed_in_model_output",
    "database_write_allowed",
    "position_access_allowed",
    "raw_secret_export_allowed",
    "real_execution_allowed",
    "wallet_access_allowed",
)

REQUIRED_CONTRACT_FIELDS = (
    "contract_id",
    "app_id",
    "stage_id",
    "contract_version",
    "planning_mode",
    "credential_owner",
    "credential_storage_location",
    "fcf_receives",
    "operator_review_status",
    "safety_flags",
)

_IDENTIFIER_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$"
)


class CredentialIsolationContractViolation(ValueError):
    """Raised when the D4 credential-isolation contract is invalid."""


def _safety_flags() -> dict[str, bool]:
    return {
        **{name: True for name in REQUIRED_TRUE_FLAGS},
        **{name: False for name in REQUIRED_FALSE_FLAGS},
    }


def build_credential_isolation_contract(
    *,
    contract_id: str = "fcf.read_only_data_gateway.credential_isolation.v1",
) -> dict[str, Any]:
    """Build the deterministic D4 planning-only contract."""
    if (
        not isinstance(contract_id, str)
        or _IDENTIFIER_PATTERN.fullmatch(contract_id) is None
    ):
        raise CredentialIsolationContractViolation(
            "contract_id_invalid"
        )

    return {
        "contract_id": contract_id,
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "planning_mode": PLANNING_MODE,
        "credential_owner": CREDENTIAL_OWNER,
        "credential_storage_location": (
            "OUTSIDE_FCF_IN_ISOLATED_GATEWAY"
        ),
        "fcf_receives": (
            "NORMALIZED_REDACTED_EVIDENCE_LINKED_DATA_ONLY"
        ),
        "operator_review_status": "REVIEW_REQUIRED",
        "safety_flags": _safety_flags(),
    }


def validate_credential_isolation_contract(
    contract: object,
) -> list[str]:
    """Return deterministic D4 contract validation errors."""
    if not isinstance(contract, Mapping):
        return ["contract_must_be_mapping"]

    errors: list[str] = []

    if set(contract.keys()) != set(REQUIRED_CONTRACT_FIELDS):
        errors.append("contract_fields_must_match_schema")

    expected_scalars = {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "contract_version": CONTRACT_VERSION,
        "planning_mode": PLANNING_MODE,
        "credential_owner": CREDENTIAL_OWNER,
        "credential_storage_location": (
            "OUTSIDE_FCF_IN_ISOLATED_GATEWAY"
        ),
        "fcf_receives": (
            "NORMALIZED_REDACTED_EVIDENCE_LINKED_DATA_ONLY"
        ),
        "operator_review_status": "REVIEW_REQUIRED",
    }

    for field, expected in expected_scalars.items():
        if contract.get(field) != expected:
            errors.append(f"{field}_invalid")

    contract_id = contract.get("contract_id")

    if (
        not isinstance(contract_id, str)
        or _IDENTIFIER_PATTERN.fullmatch(contract_id) is None
    ):
        errors.append("contract_id_invalid")

    flags = contract.get("safety_flags")

    if not isinstance(flags, Mapping):
        errors.append("safety_flags_must_be_mapping")
        return errors

    expected_flag_names = set(
        REQUIRED_TRUE_FLAGS + REQUIRED_FALSE_FLAGS
    )

    if set(flags.keys()) != expected_flag_names:
        errors.append(
            "safety_flag_names_must_match_contract"
        )

    for name in REQUIRED_TRUE_FLAGS:
        if flags.get(name) is not True:
            errors.append(f"{name}_must_be_true")

    for name in REQUIRED_FALSE_FLAGS:
        if flags.get(name) is not False:
            errors.append(f"{name}_must_be_false")

    return errors