from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
    instant,
    utc,
)


EXPECTED_DATE_COLUMNS = ("trade_date",)
_INSTRUMENT = re.compile(r"^[0-9]{6}\.(?:XSHG|XSHE)$")
_MARKETS = {"XSHG", "XSHE"}


@dataclass(frozen=True)
class RegisteredExpectedTradingDateArtifact:
    artifact_id: str
    source_id: str
    source_revision_id: str
    artifact_sha256: str
    byte_length: int
    market_id: str
    instrument_id: str
    declared_start_date: str
    declared_end_date: str
    observed_at_utc: str
    available_at_utc: str
    registered_at_utc: str
    revision_at_utc: str
    rights_state: str
    retention_state: str
    usage_scope: str = "LOCAL_EVALUATION_ONLY"
    operator_registered: bool = True
    natural_day_inference_allowed: bool = False
    raw_repository_storage_allowed: bool = False
    provider_selected: bool = False
    registration_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("artifact_id", "source_id", "source_revision_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(
            self, "artifact_sha256", digest(self.artifact_sha256, "artifact_sha256")
        )
        if (
            isinstance(self.byte_length, bool)
            or not isinstance(self.byte_length, int)
            or not 1 <= self.byte_length <= 5_000_000
        ):
            raise ValueError("byte_length exceeds the bounded calendar artifact limit")
        market = str(self.market_id).strip().upper()
        instrument = str(self.instrument_id).strip().upper()
        if market not in _MARKETS:
            raise ValueError("market_id must be XSHG or XSHE")
        if _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("instrument_id must be an A-share exchange identifier")
        if not instrument.endswith(market):
            raise ValueError("instrument_id and market_id disagree")
        object.__setattr__(self, "market_id", market)
        object.__setattr__(self, "instrument_id", instrument)
        try:
            start = date.fromisoformat(self.declared_start_date)
            end = date.fromisoformat(self.declared_end_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("declared coverage dates must be ISO dates") from exc
        if start > end:
            raise ValueError("declared coverage range is reversed")
        object.__setattr__(self, "declared_start_date", start.isoformat())
        object.__setattr__(self, "declared_end_date", end.isoformat())
        observed = instant(self.observed_at_utc, "observed_at_utc")
        available = instant(self.available_at_utc, "available_at_utc")
        registered = instant(self.registered_at_utc, "registered_at_utc")
        revision = instant(self.revision_at_utc, "revision_at_utc")
        if not observed <= available <= registered <= revision:
            raise ValueError("calendar artifact time lineage is inconsistent")
        for name in (
            "observed_at_utc",
            "available_at_utc",
            "registered_at_utc",
            "revision_at_utc",
        ):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if self.rights_state not in {"UNRESOLVED", "DECLARED_LOCAL_RESEARCH"}:
            raise ValueError("rights_state is not registered")
        if self.retention_state not in {
            "UNRESOLVED",
            "SESSION_ONLY",
            "LOCAL_DERIVED_ONLY",
        }:
            raise ValueError("retention_state is not registered")
        if self.usage_scope != "LOCAL_EVALUATION_ONLY":
            raise ValueError("usage_scope must remain local evaluation only")
        if self.operator_registered is not True:
            raise ValueError("calendar artifact requires Operator registration")
        if self.natural_day_inference_allowed is not False:
            raise ValueError("natural-day inference must remain forbidden")
        if (
            self.raw_repository_storage_allowed is not False
            or self.provider_selected is not False
        ):
            raise ValueError("calendar registration cannot grant storage or provider authority")
        object.__setattr__(
            self,
            "registration_hash",
            canonical_sha256(
                {
                    "artifact_id": self.artifact_id,
                    "artifact_sha256": self.artifact_sha256,
                    "available_at_utc": self.available_at_utc,
                    "byte_length": self.byte_length,
                    "declared_end_date": self.declared_end_date,
                    "declared_start_date": self.declared_start_date,
                    "instrument_id": self.instrument_id,
                    "market_id": self.market_id,
                    "natural_day_inference_allowed": False,
                    "observed_at_utc": self.observed_at_utc,
                    "operator_registered": True,
                    "provider_selected": False,
                    "raw_repository_storage_allowed": False,
                    "registered_at_utc": self.registered_at_utc,
                    "retention_state": self.retention_state,
                    "revision_at_utc": self.revision_at_utc,
                    "rights_state": self.rights_state,
                    "source_id": self.source_id,
                    "source_revision_id": self.source_revision_id,
                    "usage_scope": self.usage_scope,
                }
            ),
        )


@dataclass(frozen=True)
class TradingDateArtifactManifest:
    registration_hash: str
    artifact_sha256: str
    source_id: str
    source_revision_id: str
    market_id: str
    instrument_id: str
    start_date: str
    end_date: str
    date_count: int
    date_set_hash: str
    rights_state: str
    retention_state: str
    quality_state: str
    finding_codes: tuple[str, ...]
    manifest_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("registration_hash", "artifact_sha256", "date_set_hash"):
            object.__setattr__(self, name, digest(getattr(self, name), name))
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        object.__setattr__(
            self,
            "source_revision_id",
            identifier(self.source_revision_id, "source_revision_id"),
        )
        market = str(self.market_id).strip().upper()
        instrument = str(self.instrument_id).strip().upper()
        if market not in _MARKETS or _INSTRUMENT.fullmatch(instrument) is None:
            raise ValueError("manifest market or instrument identity is invalid")
        if not instrument.endswith(market):
            raise ValueError("manifest instrument_id and market_id disagree")
        object.__setattr__(self, "market_id", market)
        object.__setattr__(self, "instrument_id", instrument)
        try:
            start = date.fromisoformat(self.start_date)
            end = date.fromisoformat(self.end_date)
        except (TypeError, ValueError) as exc:
            raise ValueError("manifest range must use ISO dates") from exc
        if start > end:
            raise ValueError("manifest range is reversed")
        object.__setattr__(self, "start_date", start.isoformat())
        object.__setattr__(self, "end_date", end.isoformat())
        if (
            isinstance(self.date_count, bool)
            or not isinstance(self.date_count, int)
            or self.date_count <= 0
        ):
            raise ValueError("date_count must be a positive integer")
        findings = tuple(sorted(set(self.finding_codes)))
        if not findings:
            raise ValueError("calendar manifest requires visible findings")
        object.__setattr__(self, "finding_codes", findings)
        if self.quality_state not in {
            "REGISTERED_EXPECTED_DATES_READY",
            "REVIEW_REQUIRED_UNRESOLVED_RIGHTS",
        }:
            raise ValueError("quality_state is not registered")
        if self.rights_state not in {"UNRESOLVED", "DECLARED_LOCAL_RESEARCH"}:
            raise ValueError("manifest rights_state is not registered")
        if self.retention_state not in {
            "UNRESOLVED",
            "SESSION_ONLY",
            "LOCAL_DERIVED_ONLY",
        }:
            raise ValueError("manifest retention_state is not registered")
        object.__setattr__(
            self,
            "manifest_hash",
            canonical_sha256(
                {
                    "artifact_sha256": self.artifact_sha256,
                    "date_count": self.date_count,
                    "date_set_hash": self.date_set_hash,
                    "end_date": self.end_date,
                    "finding_codes": findings,
                    "instrument_id": self.instrument_id,
                    "market_id": self.market_id,
                    "quality_state": self.quality_state,
                    "registration_hash": self.registration_hash,
                    "retention_state": self.retention_state,
                    "rights_state": self.rights_state,
                    "source_id": self.source_id,
                    "source_revision_id": self.source_revision_id,
                    "start_date": self.start_date,
                }
            ),
        )


@dataclass(frozen=True)
class RegisteredExpectedTradingDateProfile:
    registration: RegisteredExpectedTradingDateArtifact
    dates: tuple[str, ...]
    manifest: TradingDateArtifactManifest
    operator_review_required: bool = True
    provider_selected: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.registration, RegisteredExpectedTradingDateArtifact):
            raise TypeError("registration must be RegisteredExpectedTradingDateArtifact")
        if not self.dates or tuple(sorted(set(self.dates))) != self.dates:
            raise ValueError("dates must be ordered, unique, and nonempty")
        if self.manifest.date_count != len(self.dates):
            raise ValueError("manifest date count disagrees with dates")
        expected_hash = canonical_sha256(
            {
                "dates": self.dates,
                "instrument_id": self.registration.instrument_id,
                "market_id": self.registration.market_id,
                "registration_hash": self.registration.registration_hash,
                "source_id": self.registration.source_id,
                "source_revision_id": self.registration.source_revision_id,
            }
        )
        if (
            self.manifest.registration_hash != self.registration.registration_hash
            or self.manifest.artifact_sha256 != self.registration.artifact_sha256
            or self.manifest.source_id != self.registration.source_id
            or self.manifest.source_revision_id
            != self.registration.source_revision_id
            or self.manifest.market_id != self.registration.market_id
            or self.manifest.instrument_id != self.registration.instrument_id
            or self.manifest.start_date != self.dates[0]
            or self.manifest.end_date != self.dates[-1]
            or self.manifest.date_set_hash != expected_hash
            or self.manifest.rights_state != self.registration.rights_state
            or self.manifest.retention_state != self.registration.retention_state
        ):
            raise ValueError("profile registration and manifest lineage disagree")
        if self.operator_review_required is not True or self.provider_selected is not False:
            raise ValueError("calendar profile must remain reviewed and provider-unselected")
