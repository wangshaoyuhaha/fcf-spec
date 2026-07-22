from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    identifier,
)


PROVIDERS = ("AKSHARE", "BAOSTOCK", "TUSHARE")
CANONICAL_FIELDS = (
    "amount",
    "close",
    "high",
    "instrument_id",
    "low",
    "open",
    "trade_date",
    "volume",
)
PROFILE_STATES = ("DECLARED_UNVERIFIED_BLOCKED",)
RIGHTS_STATES = ("UNRESOLVED",)
ADJUSTMENT_STATES = ("UNRESOLVED_BLOCKED",)
CLOCK_STATES = ("SOURCE_DATE_ONLY_NO_AVAILABILITY_CLOCK",)
BLOCKERS = (
    "ADJUSTMENT_SEMANTICS_UNVERIFIED",
    "POINT_IN_TIME_CLOCK_MISSING",
    "RIGHTS_UNRESOLVED",
    "SCHEMA_AUTHORITY_UNVERIFIED",
    "TRADING_STATUS_MISSING",
    "UNITS_UNVERIFIED",
)
SOURCE_UNITS = (
    "AMOUNT_SOURCE_UNIT_UNVERIFIED",
    "DATE_TEXT",
    "IDENTIFIER_TEXT",
    "PRICE_SOURCE_UNIT_UNVERIFIED",
    "VOLUME_SOURCE_UNIT_UNVERIFIED",
)
CANONICAL_UNITS = ("CNY", "ISO_DATE", "NORMALIZED_IDENTIFIER", "SHARES")
TRANSFORMS = (
    "AMOUNT_TO_CNY_BLOCKED",
    "DATE_TO_ISO",
    "EXACT_DECIMAL",
    "IDENTIFIER_TO_CANONICAL",
    "VOLUME_TO_SHARES_BLOCKED",
)
PROFILE_SCHEMA_VERSION = "FCP-0080-V1"


def _closed(value: object, allowed: tuple[str, ...], name: str) -> str:
    result = str(value).strip().upper()
    if result not in allowed:
        raise ValueError(f"{name} is not registered")
    return result


@dataclass(frozen=True)
class FieldMapping:
    source_field: str
    canonical_field: str
    source_unit: str
    canonical_unit: str
    transform_id: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_field", identifier(self.source_field, "source_field"))
        canonical_field = str(self.canonical_field).strip().lower()
        if canonical_field not in CANONICAL_FIELDS:
            raise ValueError("canonical_field is not registered")
        object.__setattr__(self, "canonical_field", canonical_field)
        object.__setattr__(self, "source_unit", _closed(self.source_unit, SOURCE_UNITS, "source_unit"))
        object.__setattr__(
            self,
            "canonical_unit",
            _closed(self.canonical_unit, CANONICAL_UNITS, "canonical_unit"),
        )
        object.__setattr__(self, "transform_id", _closed(self.transform_id, TRANSFORMS, "transform_id"))

    def payload(self) -> dict[str, str]:
        return {
            "canonical_field": self.canonical_field,
            "canonical_unit": self.canonical_unit,
            "source_field": self.source_field,
            "source_unit": self.source_unit,
            "transform_id": self.transform_id,
        }


@dataclass(frozen=True)
class CandidateProviderCompatibilityProfile:
    provider: str
    profile_id: str
    source_columns: tuple[str, ...]
    field_mappings: tuple[FieldMapping, ...]
    source_identifier_scheme: str
    source_date_format: str
    profile_state: str = "DECLARED_UNVERIFIED_BLOCKED"
    rights_state: str = "UNRESOLVED"
    adjustment_state: str = "UNRESOLVED_BLOCKED"
    clock_state: str = "SOURCE_DATE_ONLY_NO_AVAILABILITY_CLOCK"
    blockers: tuple[str, ...] = BLOCKERS
    schema_version: str = PROFILE_SCHEMA_VERSION
    access_mode: str = "REGISTERED_LOCAL_ARTIFACT"
    local_artifact_only: bool = True
    sdk_invocation_allowed: bool = False
    network_access_allowed: bool = False
    credentials_allowed: bool = False
    provider_selected: bool = False
    fallback_allowed: bool = False
    promotion_ready: bool = False
    promotes_candidate_data: bool = False
    claims_data_authority: bool = False
    operator_review_required: bool = True
    profile_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "provider", _closed(self.provider, PROVIDERS, "provider"))
        object.__setattr__(self, "profile_id", identifier(self.profile_id, "profile_id"))
        object.__setattr__(self, "schema_version", identifier(self.schema_version, "schema_version"))
        columns = tuple(identifier(item, "source_column") for item in self.source_columns)
        if not columns or len(columns) != len(set(columns)):
            raise ValueError("source_columns must be nonempty and unique")
        mappings = tuple(self.field_mappings)
        if not mappings or not all(isinstance(item, FieldMapping) for item in mappings):
            raise TypeError("field_mappings must contain FieldMapping")
        if tuple(item.source_field for item in mappings) != columns:
            raise ValueError("field mappings must follow the exact source schema")
        canonical = tuple(sorted(item.canonical_field for item in mappings))
        if canonical != CANONICAL_FIELDS:
            raise ValueError("field mappings must cover the exact canonical schema")
        if len(canonical) != len(set(canonical)):
            raise ValueError("canonical field mappings must be unique")
        object.__setattr__(self, "source_columns", columns)
        object.__setattr__(self, "field_mappings", mappings)
        object.__setattr__(self, "source_identifier_scheme", identifier(self.source_identifier_scheme, "source_identifier_scheme"))
        object.__setattr__(self, "source_date_format", identifier(self.source_date_format, "source_date_format"))
        object.__setattr__(self, "profile_state", _closed(self.profile_state, PROFILE_STATES, "profile_state"))
        object.__setattr__(self, "rights_state", _closed(self.rights_state, RIGHTS_STATES, "rights_state"))
        object.__setattr__(self, "adjustment_state", _closed(self.adjustment_state, ADJUSTMENT_STATES, "adjustment_state"))
        object.__setattr__(self, "clock_state", _closed(self.clock_state, CLOCK_STATES, "clock_state"))
        blockers = tuple(sorted(set(self.blockers)))
        if blockers != BLOCKERS:
            raise ValueError("profile blockers must remain exact and fail closed")
        object.__setattr__(self, "blockers", blockers)
        if self.access_mode != "REGISTERED_LOCAL_ARTIFACT":
            raise ValueError("candidate profile access must remain registered-local only")
        expected = {
            "local_artifact_only": True,
            "sdk_invocation_allowed": False,
            "network_access_allowed": False,
            "credentials_allowed": False,
            "provider_selected": False,
            "fallback_allowed": False,
            "promotion_ready": False,
            "promotes_candidate_data": False,
            "claims_data_authority": False,
            "operator_review_required": True,
        }
        if any(getattr(self, name) is not value for name, value in expected.items()):
            raise ValueError("candidate profile exceeds approved non-authorizing scope")
        object.__setattr__(self, "profile_hash", canonical_sha256(self.payload()))

    def payload(self) -> dict[str, object]:
        return {
            "access_mode": self.access_mode,
            "adjustment_state": self.adjustment_state,
            "blockers": list(self.blockers),
            "claims_data_authority": False,
            "clock_state": self.clock_state,
            "credentials_allowed": False,
            "fallback_allowed": False,
            "field_mappings": [item.payload() for item in self.field_mappings],
            "local_artifact_only": True,
            "network_access_allowed": False,
            "operator_review_required": True,
            "profile_id": self.profile_id,
            "profile_state": self.profile_state,
            "promotes_candidate_data": False,
            "promotion_ready": False,
            "provider": self.provider,
            "provider_selected": False,
            "rights_state": self.rights_state,
            "schema_version": self.schema_version,
            "sdk_invocation_allowed": False,
            "source_columns": list(self.source_columns),
            "source_date_format": self.source_date_format,
            "source_identifier_scheme": self.source_identifier_scheme,
        }


def _mapping(source: str, canonical: str, source_unit: str, canonical_unit: str, transform: str) -> FieldMapping:
    return FieldMapping(source, canonical, source_unit, canonical_unit, transform)


def _profile(provider: str, columns: tuple[str, ...], identifier_scheme: str, date_format: str) -> CandidateProviderCompatibilityProfile:
    mapping_by_canonical = {
        "instrument_id": (columns[0], "IDENTIFIER_TEXT", "NORMALIZED_IDENTIFIER", "IDENTIFIER_TO_CANONICAL"),
        "trade_date": (columns[1], "DATE_TEXT", "ISO_DATE", "DATE_TO_ISO"),
        "open": (columns[2], "PRICE_SOURCE_UNIT_UNVERIFIED", "CNY", "EXACT_DECIMAL"),
        "high": (columns[3], "PRICE_SOURCE_UNIT_UNVERIFIED", "CNY", "EXACT_DECIMAL"),
        "low": (columns[4], "PRICE_SOURCE_UNIT_UNVERIFIED", "CNY", "EXACT_DECIMAL"),
        "close": (columns[5], "PRICE_SOURCE_UNIT_UNVERIFIED", "CNY", "EXACT_DECIMAL"),
        "volume": (columns[6], "VOLUME_SOURCE_UNIT_UNVERIFIED", "SHARES", "VOLUME_TO_SHARES_BLOCKED"),
        "amount": (columns[7], "AMOUNT_SOURCE_UNIT_UNVERIFIED", "CNY", "AMOUNT_TO_CNY_BLOCKED"),
    }
    mappings = tuple(
        _mapping(source, canonical, source_unit, canonical_unit, transform)
        for canonical in ("instrument_id", "trade_date", "open", "high", "low", "close", "volume", "amount")
        for source, source_unit, canonical_unit, transform in (mapping_by_canonical[canonical],)
    )
    return CandidateProviderCompatibilityProfile(
        provider=provider,
        profile_id=f"fcp-0080-{provider.lower()}-local-export-v1",
        source_columns=columns,
        field_mappings=mappings,
        source_identifier_scheme=identifier_scheme,
        source_date_format=date_format,
    )


def candidate_provider_profiles() -> tuple[CandidateProviderCompatibilityProfile, ...]:
    return (
        _profile(
            "AKSHARE",
            ("symbol", "date", "open", "high", "low", "close", "volume", "amount"),
            "SOURCE_SYMBOL_UNVERIFIED",
            "SOURCE_DATE_UNVERIFIED",
        ),
        _profile(
            "BAOSTOCK",
            ("code", "date", "open", "high", "low", "close", "volume", "amount"),
            "SOURCE_CODE_UNVERIFIED",
            "SOURCE_DATE_UNVERIFIED",
        ),
        _profile(
            "TUSHARE",
            ("ts_code", "trade_date", "open", "high", "low", "close", "vol", "amount"),
            "SOURCE_TS_CODE_UNVERIFIED",
            "SOURCE_TRADE_DATE_UNVERIFIED",
        ),
    )
