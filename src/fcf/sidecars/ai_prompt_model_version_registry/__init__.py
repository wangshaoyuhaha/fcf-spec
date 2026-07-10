"""AI prompt and model version registry sidecar."""

from .contract import (
    APP_ID,
    CONTRACT_VERSION,
    VERSION_KINDS,
    VERSION_STATUSES,
    build_contract,
    validate_contract,
)
from .registry_index import (
    build_registry_index,
    get_record_by_id,
    get_records_by_kind,
    validate_registry_index,
)
from .version_record import (
    build_version_record,
    validate_version_record,
)

__all__ = [
    "APP_ID",
    "CONTRACT_VERSION",
    "VERSION_KINDS",
    "VERSION_STATUSES",
    "build_contract",
    "validate_contract",
    "build_version_record",
    "validate_version_record",
    "build_registry_index",
    "validate_registry_index",
    "get_record_by_id",
    "get_records_by_kind",
]
