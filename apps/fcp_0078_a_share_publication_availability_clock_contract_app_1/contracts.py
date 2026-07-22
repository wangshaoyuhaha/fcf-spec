from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
    instant,
    utc,
)


SUBJECT_TYPES = (
    "CORPORATE_ACTION",
    "EARNINGS_DISCLOSURE",
    "MARKET_DATA",
    "POLICY_RELEASE",
    "TRADING_CALENDAR",
)
CLOCK_SCHEMA_VERSION = "FCP-0078-V1"
PUBLICATION_STATES = (
    "DATE_ONLY_BLOCKED",
    "EXACT_OBSERVED",
    "UNKNOWN_BLOCKED",
)
REVISION_STATES = ("CANCELLED", "ORIGINAL", "REVISED")
RESOLUTION_STATES = (
    "BLOCKED_CANCELLED",
    "BLOCKED_DATE_ONLY",
    "BLOCKED_UNKNOWN",
    "EXACT_AVAILABLE",
    "NOT_YET_OBSERVABLE",
)


def _closed(value: object, allowed: tuple[str, ...], name: str) -> str:
    result = str(value).strip().upper()
    if result not in allowed:
        raise ValueError(f"{name} is not registered")
    return result


def _iso_date(value: object, name: str) -> str:
    result = str(value).strip()
    try:
        date.fromisoformat(result)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an ISO date") from exc
    return result


@dataclass(frozen=True)
class RegisteredPublicationSource:
    source_id: str
    registered_artifact_id: str
    artifact_sha256: str
    registered_at_utc: str
    rights_state: str
    retention_state: str
    operator_registered: bool = True
    local_artifact_only: bool = True
    network_retrieval_allowed: bool = False
    provider_selected: bool = False
    claims_data_authority: bool = False
    source_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_id", identifier(self.source_id, "source_id"))
        object.__setattr__(
            self,
            "registered_artifact_id",
            identifier(self.registered_artifact_id, "registered_artifact_id"),
        )
        object.__setattr__(
            self,
            "artifact_sha256",
            digest(self.artifact_sha256, "artifact_sha256"),
        )
        object.__setattr__(
            self,
            "registered_at_utc",
            utc(self.registered_at_utc, "registered_at_utc"),
        )
        if self.rights_state not in {"DECLARED_LOCAL_RESEARCH", "UNRESOLVED"}:
            raise ValueError("rights_state is not registered")
        if self.retention_state not in {
            "LOCAL_DERIVED_ONLY",
            "SESSION_ONLY",
            "UNRESOLVED",
        }:
            raise ValueError("retention_state is not registered")
        if self.operator_registered is not True or self.local_artifact_only is not True:
            raise ValueError("publication source requires registered local evidence")
        if (
            self.network_retrieval_allowed is not False
            or self.provider_selected is not False
            or self.claims_data_authority is not False
        ):
            raise ValueError("publication source exceeds local non-authorizing scope")
        object.__setattr__(
            self,
            "source_hash",
            canonical_sha256(
                {
                    "artifact_sha256": self.artifact_sha256,
                    "claims_data_authority": False,
                    "local_artifact_only": True,
                    "network_retrieval_allowed": False,
                    "operator_registered": True,
                    "provider_selected": False,
                    "registered_artifact_id": self.registered_artifact_id,
                    "registered_at_utc": self.registered_at_utc,
                    "retention_state": self.retention_state,
                    "rights_state": self.rights_state,
                    "source_id": self.source_id,
                }
            ),
        )


@dataclass(frozen=True)
class PublicationAvailabilityClock:
    record_id: str
    subject_id: str
    subject_type: str
    market: str
    publication_state: str
    publication_at_utc: str | None
    publication_date: str | None
    first_legally_available_at_utc: str | None
    retrieved_at_utc: str
    ingested_at_utc: str
    first_tradable_at_utc: str | None
    revision_at_utc: str
    source: RegisteredPublicationSource
    revision_number: int = 0
    revision_state: str = "ORIGINAL"
    revises_record_hash: str | None = None
    observed_not_inferred: bool = True
    operator_review_required: bool = True
    claims_data_authority: bool = False
    closes_gap: bool = False
    record_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("record_id", "subject_id", "market"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(
            self,
            "subject_type",
            _closed(self.subject_type, SUBJECT_TYPES, "subject_type"),
        )
        object.__setattr__(
            self,
            "publication_state",
            _closed(self.publication_state, PUBLICATION_STATES, "publication_state"),
        )
        object.__setattr__(
            self,
            "revision_state",
            _closed(self.revision_state, REVISION_STATES, "revision_state"),
        )
        if not isinstance(self.source, RegisteredPublicationSource):
            raise TypeError("source must be RegisteredPublicationSource")
        for name in ("retrieved_at_utc", "ingested_at_utc", "revision_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        retrieved = instant(self.retrieved_at_utc, "retrieved_at_utc")
        ingested = instant(self.ingested_at_utc, "ingested_at_utc")
        revision = instant(self.revision_at_utc, "revision_at_utc")
        if not retrieved <= ingested <= revision:
            raise ValueError("retrieval, ingest, and revision clocks are not monotonic")

        if self.publication_state == "EXACT_OBSERVED":
            if self.publication_date is not None:
                raise ValueError("exact publication cannot also carry date-only evidence")
            for name in (
                "publication_at_utc",
                "first_legally_available_at_utc",
                "first_tradable_at_utc",
            ):
                value = getattr(self, name)
                if value is None:
                    raise ValueError(f"{name} is required for exact publication")
                object.__setattr__(self, name, utc(value, name))
            publication = instant(self.publication_at_utc, "publication_at_utc")
            legal = instant(
                self.first_legally_available_at_utc,
                "first_legally_available_at_utc",
            )
            tradable = instant(self.first_tradable_at_utc, "first_tradable_at_utc")
            if not publication <= legal <= retrieved <= ingested <= revision:
                raise ValueError("publication availability clocks are not monotonic")
            if tradable < legal:
                raise ValueError("first tradable time cannot precede legal availability")
        elif self.publication_state == "DATE_ONLY_BLOCKED":
            if self.publication_date is None:
                raise ValueError("date-only publication requires publication_date")
            object.__setattr__(
                self,
                "publication_date",
                _iso_date(self.publication_date, "publication_date"),
            )
            self._require_exact_fields_absent()
        else:
            if self.publication_date is not None:
                raise ValueError("unknown publication cannot claim a date")
            self._require_exact_fields_absent()

        if isinstance(self.revision_number, bool) or not isinstance(
            self.revision_number, int
        ) or self.revision_number < 0:
            raise ValueError("revision_number must be a nonnegative integer")
        if self.revision_number == 0:
            if self.revision_state != "ORIGINAL" or self.revises_record_hash is not None:
                raise ValueError("revision zero must be original without predecessor")
        else:
            if self.revision_state == "ORIGINAL" or self.revises_record_hash is None:
                raise ValueError("later revision must identify a predecessor")
            object.__setattr__(
                self,
                "revises_record_hash",
                digest(self.revises_record_hash, "revises_record_hash"),
            )
        if self.observed_not_inferred is not True or self.operator_review_required is not True:
            raise ValueError("publication clocks must remain observed and reviewable")
        if self.claims_data_authority is not False or self.closes_gap is not False:
            raise ValueError("publication clocks cannot establish authority or close gaps")
        object.__setattr__(self, "record_hash", canonical_sha256(self.payload()))

    def _require_exact_fields_absent(self) -> None:
        for name in (
            "publication_at_utc",
            "first_legally_available_at_utc",
            "first_tradable_at_utc",
        ):
            if getattr(self, name) is not None:
                raise ValueError("blocked publication cannot claim an exact clock")

    @property
    def exact_time_usable(self) -> bool:
        return self.publication_state == "EXACT_OBSERVED" and self.revision_state != "CANCELLED"

    def payload(self) -> dict[str, object]:
        return {
            "claims_data_authority": False,
            "closes_gap": False,
            "first_legally_available_at_utc": self.first_legally_available_at_utc,
            "first_tradable_at_utc": self.first_tradable_at_utc,
            "ingested_at_utc": self.ingested_at_utc,
            "market": self.market,
            "observed_not_inferred": True,
            "operator_review_required": True,
            "publication_at_utc": self.publication_at_utc,
            "publication_date": self.publication_date,
            "publication_state": self.publication_state,
            "record_id": self.record_id,
            "retrieved_at_utc": self.retrieved_at_utc,
            "revision_at_utc": self.revision_at_utc,
            "revision_number": self.revision_number,
            "revision_state": self.revision_state,
            "revises_record_hash": self.revises_record_hash,
            "source_hash": self.source.source_hash,
            "subject_id": self.subject_id,
            "subject_type": self.subject_type,
        }


@dataclass(frozen=True)
class PublicationClockResolution:
    subject_id: str
    evaluated_at_utc: str
    resolution_state: str
    selected_record: PublicationAvailabilityClock | None
    observed_record_hashes: tuple[str, ...]
    operator_review_required: bool = True
    claims_data_authority: bool = False
    closes_gap: bool = False
    resolution_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "subject_id", identifier(self.subject_id, "subject_id"))
        object.__setattr__(
            self,
            "evaluated_at_utc",
            utc(self.evaluated_at_utc, "evaluated_at_utc"),
        )
        object.__setattr__(
            self,
            "resolution_state",
            _closed(self.resolution_state, RESOLUTION_STATES, "resolution_state"),
        )
        if not isinstance(self.observed_record_hashes, tuple) or tuple(
            sorted(set(self.observed_record_hashes))
        ) != self.observed_record_hashes:
            raise ValueError("observed_record_hashes must be unique and sorted")
        for value in self.observed_record_hashes:
            digest(value, "observed_record_hash")
        if self.resolution_state == "NOT_YET_OBSERVABLE":
            if self.selected_record is not None or self.observed_record_hashes:
                raise ValueError("unobservable resolution cannot select evidence")
        elif not isinstance(self.selected_record, PublicationAvailabilityClock):
            raise TypeError("observable resolution requires a selected clock")
        if self.selected_record is not None:
            expected_state = (
                "BLOCKED_CANCELLED"
                if self.selected_record.revision_state == "CANCELLED"
                else "EXACT_AVAILABLE"
                if self.selected_record.publication_state == "EXACT_OBSERVED"
                else "BLOCKED_DATE_ONLY"
                if self.selected_record.publication_state == "DATE_ONLY_BLOCKED"
                else "BLOCKED_UNKNOWN"
            )
            if self.resolution_state != expected_state:
                raise ValueError("resolution state disagrees with selected clock")
            if self.selected_record.record_hash not in self.observed_record_hashes:
                raise ValueError("selected clock must be present in observed hashes")
        if self.operator_review_required is not True:
            raise ValueError("Operator review must remain required")
        if self.claims_data_authority is not False or self.closes_gap is not False:
            raise ValueError("resolution cannot establish authority or close gaps")
        object.__setattr__(
            self,
            "resolution_hash",
            canonical_sha256(
                {
                    "claims_data_authority": False,
                    "closes_gap": False,
                    "evaluated_at_utc": self.evaluated_at_utc,
                    "observed_record_hashes": self.observed_record_hashes,
                    "operator_review_required": True,
                    "resolution_state": self.resolution_state,
                    "selected_record_hash": (
                        self.selected_record.record_hash
                        if self.selected_record is not None
                        else None
                    ),
                    "subject_id": self.subject_id,
                }
            ),
        )
