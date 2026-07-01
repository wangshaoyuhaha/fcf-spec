import pytest

from fcf.schemas.schema_error_catalog import (
    ERROR_INVALID_ENUM_VALUE,
    ERROR_INVALID_NON_NEGATIVE_NUMBER,
    ERROR_INVALID_NUMBER,
    ERROR_INVALID_PAYLOAD_TYPE,
    ERROR_INVALID_POSITIVE_NUMBER,
    ERROR_INVALID_SPREAD,
    ERROR_MISSING_FIELD,
    build_schema_error,
    describe_schema_error_catalog,
    invalid_enum_message,
    invalid_non_negative_number_message,
    invalid_number_message,
    invalid_payload_type_message,
    invalid_positive_number_message,
    invalid_spread_message,
    missing_fields_message,
)


def test_describe_schema_error_catalog_declares_error_types_and_boundary():
    catalog = describe_schema_error_catalog()

    assert catalog["catalog"] == "schema_error_catalog"
    assert catalog["catalog_version"] == "0.1.0"
    assert ERROR_MISSING_FIELD in catalog["error_types"]
    assert ERROR_INVALID_ENUM_VALUE in catalog["error_types"]
    assert ERROR_INVALID_NUMBER in catalog["error_types"]
    assert ERROR_INVALID_SPREAD in catalog["error_types"]
    assert catalog["safe_boundary"]["no_real_exchange_api"] is True
    assert catalog["safe_boundary"]["no_real_order_placement"] is True


def test_build_schema_error_returns_stable_dict():
    error = build_schema_error(
        ERROR_INVALID_NUMBER,
        "last_price must be a valid number",
    )

    assert error == {
        "type": "InvalidNumber",
        "message": "last_price must be a valid number",
    }


def test_build_schema_error_rejects_unknown_type():
    with pytest.raises(ValueError, match="unknown schema error type"):
        build_schema_error("NotReal", "bad")


def test_missing_fields_message_is_stable():
    assert missing_fields_message(["asset_class", "last_price"]) == (
        "missing required fields: asset_class, last_price"
    )


def test_invalid_enum_message_is_stable():
    assert invalid_enum_message("market_type", "not-real") == (
        "market_type is not supported: not-real"
    )


def test_invalid_number_message_is_stable():
    assert invalid_number_message("last_price") == (
        "last_price must be a valid number"
    )


def test_invalid_positive_number_message_is_stable():
    assert invalid_positive_number_message("last_price") == (
        "last_price must be greater than 0"
    )


def test_invalid_non_negative_number_message_is_stable():
    assert invalid_non_negative_number_message("volume") == (
        "volume must be greater than or equal to 0"
    )


def test_invalid_spread_and_payload_messages_are_stable():
    assert invalid_spread_message() == "best_bid must be less than or equal to best_ask"
    assert invalid_payload_type_message() == "raw market input must be a dict"


def test_catalog_exports_expected_error_type_constants():
    assert ERROR_MISSING_FIELD == "MissingField"
    assert ERROR_INVALID_ENUM_VALUE == "InvalidEnumValue"
    assert ERROR_INVALID_NUMBER == "InvalidNumber"
    assert ERROR_INVALID_POSITIVE_NUMBER == "InvalidPositiveNumber"
    assert ERROR_INVALID_NON_NEGATIVE_NUMBER == "InvalidNonNegativeNumber"
    assert ERROR_INVALID_SPREAD == "InvalidSpread"
    assert ERROR_INVALID_PAYLOAD_TYPE == "InvalidPayloadType"
