"""Smoke tests for D4 credential-isolation contract."""

from fcf.sidecars.read_only_data_gateway_planning.credential_isolation import (
    build_credential_isolation_contract,
    validate_credential_isolation_contract,
)


def _contract():
    return build_credential_isolation_contract()


def test_valid_contract_passes_validation():
    assert validate_credential_isolation_contract(
        _contract()
    ) == []


def test_credentials_remain_outside_fcf_and_models():
    contract = _contract()
    flags = contract["safety_flags"]

    assert contract["credential_owner"] == (
        "ISOLATED_READ_ONLY_GATEWAY"
    )
    assert flags["credential_material_allowed_in_fcf"] is False
    assert (
        flags["credential_material_allowed_in_model_input"]
        is False
    )
    assert (
        flags["credential_material_allowed_in_model_output"]
        is False
    )
    assert flags["raw_secret_export_allowed"] is False


def test_validation_rejects_credential_exposure():
    contract = _contract()
    contract["safety_flags"][
        "credential_material_allowed_in_fcf"
    ] = True

    assert (
        "credential_material_allowed_in_fcf_must_be_false"
        in validate_credential_isolation_contract(contract)
    )

def test_identity_is_locked():
    contract = _contract()

    assert contract["app_id"] == (
        "READ-ONLY-DATA-GATEWAY-PLANNING-APP-1"
    )
    assert contract["stage_id"] == (
        "READ-ONLY-DATA-GATEWAY-PLANNING-D4"
    )
    assert contract["contract_version"] == "1.0.0"
    assert contract["planning_mode"] == "PLANNING_ONLY"


def test_fcf_receives_only_governed_normalized_output():
    contract = _contract()

    assert contract["credential_storage_location"] == (
        "OUTSIDE_FCF_IN_ISOLATED_GATEWAY"
    )
    assert contract["fcf_receives"] == (
        "NORMALIZED_REDACTED_EVIDENCE_LINKED_DATA_ONLY"
    )
    assert contract["operator_review_status"] == (
        "REVIEW_REQUIRED"
    )


def test_builder_rejects_invalid_contract_id():
    import pytest

    from fcf.sidecars.read_only_data_gateway_planning.credential_isolation import (
        CredentialIsolationContractViolation,
    )

    with pytest.raises(
        CredentialIsolationContractViolation
    ):
        build_credential_isolation_contract(
            contract_id="invalid contract id"
        )


def test_builder_returns_fresh_safety_flags():
    first = _contract()
    second = _contract()

    first["safety_flags"][
        "credential_material_allowed_in_fcf"
    ] = True

    assert second == _contract()
    assert first != second


def test_non_mapping_contract_is_rejected():
    assert validate_credential_isolation_contract(
        []
    ) == ["contract_must_be_mapping"]

def test_validation_rejects_balance_access():
    contract = _contract()
    contract["safety_flags"][
        "balance_access_allowed"
    ] = True

    assert "balance_access_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_position_access():
    contract = _contract()
    contract["safety_flags"][
        "position_access_allowed"
    ] = True

    assert "position_access_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_wallet_access():
    contract = _contract()
    contract["safety_flags"][
        "wallet_access_allowed"
    ] = True

    assert "wallet_access_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_database_write():
    contract = _contract()
    contract["safety_flags"][
        "database_write_allowed"
    ] = True

    assert "database_write_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_real_execution():
    contract = _contract()
    contract["safety_flags"][
        "real_execution_allowed"
    ] = True

    assert "real_execution_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )

def test_validation_rejects_balance_access():
    contract = _contract()
    contract["safety_flags"][
        "balance_access_allowed"
    ] = True

    assert "balance_access_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_position_access():
    contract = _contract()
    contract["safety_flags"][
        "position_access_allowed"
    ] = True

    assert "position_access_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_wallet_access():
    contract = _contract()
    contract["safety_flags"][
        "wallet_access_allowed"
    ] = True

    assert "wallet_access_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_database_write():
    contract = _contract()
    contract["safety_flags"][
        "database_write_allowed"
    ] = True

    assert "database_write_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_real_execution():
    contract = _contract()
    contract["safety_flags"][
        "real_execution_allowed"
    ] = True

    assert "real_execution_allowed_must_be_false" in (
        validate_credential_isolation_contract(contract)
    )

def test_validation_rejects_credential_owner_tampering():
    contract = _contract()
    contract["credential_owner"] = "FCF"

    assert "credential_owner_invalid" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_storage_location_tampering():
    contract = _contract()
    contract["credential_storage_location"] = (
        "INSIDE_FCF"
    )

    assert "credential_storage_location_invalid" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_fcf_receive_scope_tampering():
    contract = _contract()
    contract["fcf_receives"] = "RAW_SECRET_DATA"

    assert "fcf_receives_invalid" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_missing_safety_flag():
    contract = _contract()
    del contract["safety_flags"][
        "wallet_access_allowed"
    ]

    assert "safety_flag_names_must_match_contract" in (
        validate_credential_isolation_contract(contract)
    )


def test_validation_rejects_non_mapping_safety_flags():
    contract = _contract()
    contract["safety_flags"] = []

    assert "safety_flags_must_be_mapping" in (
        validate_credential_isolation_contract(contract)
    )