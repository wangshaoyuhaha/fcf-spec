from typing import Any, Dict, Iterable, List

CATALOG_NAME = "schema_error_catalog"
CATALOG_VERSION = "0.1.0"

ERROR_MISSING_FIELD = "MissingField"
ERROR_INVALID_ENUM_VALUE = "InvalidEnumValue"
ERROR_INVALID_NUMBER = "InvalidNumber"
ERROR_INVALID_POSITIVE_NUMBER = "InvalidPositiveNumber"
ERROR_INVALID_NON_NEGATIVE_NUMBER = "InvalidNonNegativeNumber"
ERROR_INVALID_SPREAD = "InvalidSpread"
ERROR_INVALID_PAYLOAD_TYPE = "InvalidPayloadType"

ERROR_TYPES = {
    ERROR_MISSING_FIELD,
    ERROR_INVALID_ENUM_VALUE,
    ERROR_INVALID_NUMBER,
    ERROR_INVALID_POSITIVE_NUMBER,
    ERROR_INVALID_NON_NEGATIVE_NUMBER,
    ERROR_INVALID_SPREAD,
    ERROR_INVALID_PAYLOAD_TYPE,
}


def describe_schema_error_catalog() -> Dict[str, Any]:
    return {
        "catalog": CATALOG_NAME,
        "catalog_version": CATALOG_VERSION,
        "error_types": sorted(ERROR_TYPES),
        "stable_messages": {
            ERROR_MISSING_FIELD: "missing required fields: field_a, field_b",
            ERROR_INVALID_ENUM_VALUE: "field_name is not supported: value",
            ERROR_INVALID_NUMBER: "field_name must be a valid number",
            ERROR_INVALID_POSITIVE_NUMBER: "field_name must be greater than 0",
            ERROR_INVALID_NON_NEGATIVE_NUMBER: "field_name must be greater than or equal to 0",
            ERROR_INVALID_SPREAD: "best_bid must be less than or equal to best_ask",
            ERROR_INVALID_PAYLOAD_TYPE: "raw market input must be a dict",
        },
        "safe_boundary": {
            "no_real_exchange_api": True,
            "no_real_order_placement": True,
            "no_secret_storage": True,
        },
    }


def build_schema_error(error_type: str, message: str) -> Dict[str, str]:
    if error_type not in ERROR_TYPES:
        raise ValueError(f"unknown schema error type: {error_type}")

    return {
        "type": error_type,
        "message": message,
    }


def missing_fields_message(fields: Iterable[str]) -> str:
    field_list: List[str] = [str(field) for field in fields]
    return "missing required fields: " + ", ".join(field_list)


def invalid_enum_message(field: str, value: Any) -> str:
    return f"{field} is not supported: {value}"


def invalid_number_message(field: str) -> str:
    return f"{field} must be a valid number"


def invalid_positive_number_message(field: str) -> str:
    return f"{field} must be greater than 0"


def invalid_non_negative_number_message(field: str) -> str:
    return f"{field} must be greater than or equal to 0"


def invalid_spread_message() -> str:
    return "best_bid must be less than or equal to best_ask"


def invalid_payload_type_message() -> str:
    return "raw market input must be a dict"
