from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0022_btc_local_export_canonicalization_bridge_app_1 import (
    BTCLocalExportProfile,
    RegisteredBTCLocalExport,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


OBSERVATION_KINDS = (
    "BOOK_DELTA",
    "BOOK_SNAPSHOT",
    "FUNDING",
    "REFERENCE_PRICE",
    "TRADE",
)


@dataclass(frozen=True)
class BTCLocalExportValidationRequest:
    registration: RegisteredBTCLocalExport
    profile: BTCLocalExportProfile
    output_artifact_id: str
    as_of_utc: str

    def __post_init__(self) -> None:
        if not isinstance(self.registration, RegisteredBTCLocalExport):
            raise TypeError("registration must be RegisteredBTCLocalExport")
        if not isinstance(self.profile, BTCLocalExportProfile):
            raise TypeError("profile must be BTCLocalExportProfile")
        if self.registration.source_id != self.profile.source_id:
            raise ValueError("registration and profile source lineage disagree")
        output_id = identifier(self.output_artifact_id, "output_artifact_id")
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(as_of) < instant(self.registration.registered_at_utc):
            raise ValueError("validation cannot precede artifact registration")
        object.__setattr__(self, "output_artifact_id", output_id)
        object.__setattr__(self, "as_of_utc", as_of)


@dataclass(frozen=True)
class BTCLocalExportValidationResult:
    source_artifact_id: str
    source_artifact_sha256: str
    source_byte_length: int
    canonical_artifact_id: str
    canonical_artifact_sha256: str
    canonical_byte_length: int
    profile_hash: str
    manifest_hash: str
    observation_hashes_sha256: str
    observation_count: int
    observation_kind_counts: tuple[tuple[str, int], ...]
    sequence_min: int
    sequence_max: int
    event_start_utc: str
    event_end_utc: str
    received_start_utc: str
    received_end_utc: str
    ingested_start_utc: str
    ingested_end_utc: str
    as_of_utc: str
    quality_state: str = "READY_FOR_REPLAY"
    operator_review_required: bool = True
    local_only: bool = True
    provider_selected: bool = False
    network_used: bool = False
    sdk_used: bool = False
    raw_rows_retained: bool = False
    canonical_rows_retained: bool = False
    local_paths_retained: bool = False
    gap_closed: bool = False
    result_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("source_artifact_id", "canonical_artifact_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in (
            "source_artifact_sha256",
            "canonical_artifact_sha256",
            "profile_hash",
            "manifest_hash",
            "observation_hashes_sha256",
        ):
            value = str(getattr(self, name))
            if len(value) != 64 or any(char not in "0123456789abcdef" for char in value):
                raise ValueError(f"{name} must be lowercase SHA-256")
        for name in ("source_byte_length", "canonical_byte_length", "observation_count"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.source_byte_length > 25_000_000 or self.canonical_byte_length > 25_000_000:
            raise ValueError("artifact byte length exceeds the bounded domain")
        counts = tuple(self.observation_kind_counts)
        if tuple(kind for kind, _ in counts) != OBSERVATION_KINDS:
            raise ValueError("observation_kind_counts must use the closed order")
        if any(isinstance(count, bool) or not isinstance(count, int) or count < 0 for _, count in counts):
            raise ValueError("observation kind counts must be nonnegative integers")
        if sum(count for _, count in counts) != self.observation_count:
            raise ValueError("observation kind counts disagree with total")
        for name in ("sequence_min", "sequence_max"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if self.sequence_min > self.sequence_max:
            raise ValueError("sequence bounds are reversed")
        clock_pairs = (
            ("event_start_utc", "event_end_utc"),
            ("received_start_utc", "received_end_utc"),
            ("ingested_start_utc", "ingested_end_utc"),
        )
        for start_name, end_name in clock_pairs:
            start = utc(getattr(self, start_name), start_name)
            end = utc(getattr(self, end_name), end_name)
            if instant(start) > instant(end):
                raise ValueError("clock bounds are reversed")
            object.__setattr__(self, start_name, start)
            object.__setattr__(self, end_name, end)
        as_of = utc(self.as_of_utc, "as_of_utc")
        if instant(self.ingested_end_utc) > instant(as_of):
            raise ValueError("validation contains future ingestion")
        if self.quality_state != "READY_FOR_REPLAY":
            raise ValueError("quality_state is closed")
        if (
            self.operator_review_required is not True
            or self.local_only is not True
            or self.provider_selected is not False
            or self.network_used is not False
            or self.sdk_used is not False
            or self.raw_rows_retained is not False
            or self.canonical_rows_retained is not False
            or self.local_paths_retained is not False
            or self.gap_closed is not False
        ):
            raise ValueError("validation result cannot gain runtime or action authority")
        object.__setattr__(self, "observation_kind_counts", counts)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(self, "result_hash", canonical_sha256(self.to_record(include_hash=False)))

    def to_record(self, *, include_hash: bool = True) -> dict[str, object]:
        record: dict[str, object] = {
            "artifacts": {
                "canonical": {
                    "artifact_id": self.canonical_artifact_id,
                    "byte_length": self.canonical_byte_length,
                    "sha256": self.canonical_artifact_sha256,
                },
                "source": {
                    "artifact_id": self.source_artifact_id,
                    "byte_length": self.source_byte_length,
                    "sha256": self.source_artifact_sha256,
                },
            },
            "as_of_utc": self.as_of_utc,
            "authority": {
                "canonical_rows_retained": False,
                "gap_closed": False,
                "local_only": True,
                "local_paths_retained": False,
                "network_used": False,
                "operator_review_required": True,
                "provider_selected": False,
                "raw_rows_retained": False,
                "sdk_used": False,
            },
            "clocks": {
                "event": [self.event_start_utc, self.event_end_utc],
                "ingested": [self.ingested_start_utc, self.ingested_end_utc],
                "received": [self.received_start_utc, self.received_end_utc],
            },
            "lineage": {
                "manifest_hash": self.manifest_hash,
                "observation_hashes_sha256": self.observation_hashes_sha256,
                "profile_hash": self.profile_hash,
            },
            "observations": {
                "count": self.observation_count,
                "kind_counts": {
                    kind: count for kind, count in self.observation_kind_counts
                },
                "sequence_max": self.sequence_max,
                "sequence_min": self.sequence_min,
            },
            "quality_state": self.quality_state,
        }
        if include_hash:
            record["result_hash"] = self.result_hash
        return record
