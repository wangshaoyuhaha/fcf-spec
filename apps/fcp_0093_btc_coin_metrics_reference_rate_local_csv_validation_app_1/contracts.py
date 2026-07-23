from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    LocalEventRights,
    identifier,
    instant,
    utc,
)


PHASE_ID = (
    "FCF-FCP-0093-BTC-COIN-METRICS-REFERENCE-RATE-LOCAL-CSV-"
    "VALIDATION-APP-1"
)
EXPECTED_HEADER = ("asset", "time", "ReferenceRateUSD")
MAX_SOURCE_BYTES = 1_000_000
EXPECTED_CADENCE_SECONDS = 3_600


def _sha256(value: object, name: str) -> str:
    text = str(value).strip().lower()
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return text


def _positive_int(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


@dataclass(frozen=True)
class CoinMetricsBTCReferenceCSVRegistration:
    artifact_id: str
    source_id: str
    content_sha256: str
    byte_length: int
    registered_at_utc: str
    rights: LocalEventRights
    media_type: str = "text/csv"
    schema_id: str = "coin-metrics-btc-reference-rate-csv-v1"
    operator_registered: bool = True
    local_only: bool = True
    raw_repository_storage_allowed: bool = False
    network_retrieval_allowed: bool = False
    provider_selected: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", identifier(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        object.__setattr__(
            self,
            "content_sha256",
            _sha256(self.content_sha256, "content_sha256"),
        )
        length = _positive_int(self.byte_length, "byte_length")
        if length > MAX_SOURCE_BYTES:
            raise ValueError("byte_length exceeds the bounded CSV limit")
        object.__setattr__(
            self,
            "registered_at_utc",
            utc(self.registered_at_utc, "registered_at_utc"),
        )
        if not isinstance(self.rights, LocalEventRights):
            raise TypeError("registration requires typed local rights")
        if self.media_type != "text/csv":
            raise ValueError("registration media_type must be text/csv")
        if self.schema_id != "coin-metrics-btc-reference-rate-csv-v1":
            raise ValueError("registration schema_id is not allowed")
        if (
            self.operator_registered is not True
            or self.local_only is not True
            or self.raw_repository_storage_allowed is not False
            or self.network_retrieval_allowed is not False
            or self.provider_selected is not False
        ):
            raise ValueError("registration cannot gain retrieval or provider authority")


@dataclass(frozen=True)
class CoinMetricsBTCReferenceCSVValidationRequest:
    registration: CoinMetricsBTCReferenceCSVRegistration
    output_artifact_id: str
    as_of_utc: str
    expected_asset: str = "btc"
    expected_header: tuple[str, ...] = EXPECTED_HEADER
    expected_cadence_seconds: int = EXPECTED_CADENCE_SECONDS

    def __post_init__(self) -> None:
        if not isinstance(self.registration, CoinMetricsBTCReferenceCSVRegistration):
            raise TypeError("registration must be typed")
        object.__setattr__(
            self,
            "output_artifact_id",
            identifier(self.output_artifact_id, "output_artifact_id"),
        )
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(as_of) < instant(self.registration.registered_at_utc):
            raise ValueError("validation cannot precede registration")
        if self.expected_asset != "btc":
            raise ValueError("expected_asset is closed to btc")
        header = tuple(self.expected_header)
        if header != EXPECTED_HEADER:
            raise ValueError("expected_header is closed")
        if self.expected_cadence_seconds != EXPECTED_CADENCE_SECONDS:
            raise ValueError("expected cadence is closed")
        object.__setattr__(self, "expected_header", header)
        object.__setattr__(self, "as_of_utc", as_of)


@dataclass(frozen=True)
class CoinMetricsBTCReferenceCSVValidationResult:
    source_artifact_id: str
    source_artifact_sha256: str
    source_byte_length: int
    output_artifact_id: str
    header_sha256: str
    observation_hashes_sha256: str
    observation_count: int
    observation_start_utc: str
    observation_end_utc: str
    cadence_seconds: int
    as_of_utc: str
    source_schema_id: str = "coin-metrics-btc-reference-rate-csv-v1"
    observation_kind: str = "NEUTRAL_REFERENCE_RATE_USD"
    quality_state: str = "READY_FOR_OPERATOR_REVIEW"
    operator_review_required: bool = True
    local_only: bool = True
    network_used: bool = False
    sdk_used: bool = False
    source_rows_retained: bool = False
    source_values_retained: bool = False
    local_paths_retained: bool = False
    provider_selected: bool = False
    venue_selected: bool = False
    realtime_activated: bool = False
    data_promoted: bool = False
    mark_or_index_authority: bool = False
    signal_authority: bool = False
    product_authority: bool = False
    execution_authority: bool = False
    gap_095_status: str = "RESEARCH_REQUIRED"
    result_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("source_artifact_id", "output_artifact_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in (
            "source_artifact_sha256",
            "header_sha256",
            "observation_hashes_sha256",
        ):
            object.__setattr__(self, name, _sha256(getattr(self, name), name))
        source_length = _positive_int(self.source_byte_length, "source_byte_length")
        if source_length > MAX_SOURCE_BYTES:
            raise ValueError("source_byte_length exceeds the bounded CSV limit")
        _positive_int(self.observation_count, "observation_count")
        if self.observation_count < 2:
            raise ValueError("validation requires at least two observations")
        if self.cadence_seconds != EXPECTED_CADENCE_SECONDS:
            raise ValueError("cadence_seconds is not the registered cadence")
        start = utc(self.observation_start_utc, "observation_start_utc")
        end = utc(self.observation_end_utc, "observation_end_utc")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if not instant(start) < instant(end) <= instant(as_of):
            raise ValueError("observation bounds must precede as_of_utc")
        if self.source_schema_id != "coin-metrics-btc-reference-rate-csv-v1":
            raise ValueError("source_schema_id is closed")
        if self.observation_kind != "NEUTRAL_REFERENCE_RATE_USD":
            raise ValueError("observation_kind is closed")
        if self.quality_state != "READY_FOR_OPERATOR_REVIEW":
            raise ValueError("quality_state is closed")
        if self.gap_095_status != "RESEARCH_REQUIRED":
            raise ValueError("GAP-095 must remain open")
        if (
            self.operator_review_required is not True
            or self.local_only is not True
            or self.network_used is not False
            or self.sdk_used is not False
            or self.source_rows_retained is not False
            or self.source_values_retained is not False
            or self.local_paths_retained is not False
            or self.provider_selected is not False
            or self.venue_selected is not False
            or self.realtime_activated is not False
            or self.data_promoted is not False
            or self.mark_or_index_authority is not False
            or self.signal_authority is not False
            or self.product_authority is not False
            or self.execution_authority is not False
        ):
            raise ValueError("validation result cannot gain authority")
        object.__setattr__(self, "observation_start_utc", start)
        object.__setattr__(self, "observation_end_utc", end)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "result_hash",
            canonical_sha256(self.to_record(include_hash=False)),
        )

    def to_record(self, *, include_hash: bool = True) -> dict[str, object]:
        record: dict[str, object] = {
            "artifact": {
                "output_artifact_id": self.output_artifact_id,
                "source_artifact_id": self.source_artifact_id,
                "source_byte_length": self.source_byte_length,
                "source_sha256": self.source_artifact_sha256,
            },
            "as_of_utc": self.as_of_utc,
            "authority": {
                "data_promoted": False,
                "execution_authority": False,
                "local_only": True,
                "local_paths_retained": False,
                "mark_or_index_authority": False,
                "network_used": False,
                "operator_review_required": True,
                "product_authority": False,
                "provider_selected": False,
                "realtime_activated": False,
                "sdk_used": False,
                "signal_authority": False,
                "source_rows_retained": False,
                "source_values_retained": False,
                "venue_selected": False,
            },
            "gap_095_status": self.gap_095_status,
            "lineage": {
                "header_sha256": self.header_sha256,
                "observation_hashes_sha256": self.observation_hashes_sha256,
                "source_schema_id": self.source_schema_id,
            },
            "observations": {
                "cadence_seconds": self.cadence_seconds,
                "count": self.observation_count,
                "end_utc": self.observation_end_utc,
                "kind": self.observation_kind,
                "start_utc": self.observation_start_utc,
            },
            "phase_id": PHASE_ID,
            "quality_state": self.quality_state,
        }
        if include_hash:
            record["result_hash"] = self.result_hash
        return record
