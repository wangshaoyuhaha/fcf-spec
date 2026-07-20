from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping

from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, utc


OBSERVATION_KINDS = ("TICK", "MINUTE_BAR", "ORDER_BOOK")
REQUIRED_FIELDS = MappingProxyType(
    {
        "TICK": ("instrument_id", "event_at", "last", "volume"),
        "MINUTE_BAR": (
            "instrument_id",
            "event_at",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "interval",
        ),
        "ORDER_BOOK": (
            "instrument_id",
            "event_at",
            "bid_price_1",
            "bid_size_1",
            "ask_price_1",
            "ask_size_1",
        ),
    }
)


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class MarketDataFieldMap:
    mapping_id: str
    market: str
    observation_kind: str
    registered_artifact_id: str
    canonical_to_source: Mapping[str, str]
    provider_selection_state: str = "UNSELECTED"
    operator_registered: bool = True
    mapping_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("mapping_id", "market", "registered_artifact_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        kind = str(self.observation_kind).strip().upper()
        if kind not in OBSERVATION_KINDS:
            raise ValueError("observation_kind is not registered")
        object.__setattr__(self, "observation_kind", kind)
        normalized = {
            identifier(key, "canonical field"): identifier(value, "source field")
            for key, value in self.canonical_to_source.items()
        }
        if set(REQUIRED_FIELDS[kind]) != set(normalized):
            raise ValueError("field map must match the closed canonical schema")
        if len(set(normalized.values())) != len(normalized):
            raise ValueError("source fields must be unique")
        if self.provider_selection_state != "UNSELECTED":
            raise ValueError("FCP-0009 cannot select a provider")
        if self.operator_registered is not True:
            raise ValueError("field map requires Operator registration")
        object.__setattr__(self, "canonical_to_source", MappingProxyType(normalized))
        object.__setattr__(
            self,
            "mapping_hash",
            canonical_sha256(
                {
                    "canonical_to_source": normalized,
                    "mapping_id": self.mapping_id,
                    "market": self.market,
                    "observation_kind": kind,
                    "provider_selection_state": "UNSELECTED",
                    "registered_artifact_id": self.registered_artifact_id,
                }
            ),
        )


@dataclass(frozen=True)
class RegisteredMarketDataObservation:
    observation_id: str
    mapping_id: str
    source_sequence: int
    received_at_utc: str
    processed_at_utc: str
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "observation_id", identifier(self.observation_id, "observation_id")
        )
        object.__setattr__(self, "mapping_id", identifier(self.mapping_id, "mapping_id"))
        if isinstance(self.source_sequence, bool) or self.source_sequence <= 0:
            raise ValueError("source_sequence must be positive")
        object.__setattr__(
            self, "received_at_utc", utc(self.received_at_utc, "received_at_utc")
        )
        object.__setattr__(
            self, "processed_at_utc", utc(self.processed_at_utc, "processed_at_utc")
        )
        if not isinstance(self.payload, Mapping) or not self.payload:
            raise ValueError("payload must be a nonempty mapping")
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


@dataclass(frozen=True)
class AdapterActivationGate:
    entitlement_state: str = "UNRESOLVED"
    retention_state: str = "UNRESOLVED"
    provider_selection_state: str = "UNSELECTED"
    credentials_state: str = "ABSENT"
    network_state: str = "DISABLED"
    external_activation_state: str = "BLOCKED"
    product_evidence_state: str = "BLOCKED"
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        expected = (
            self.entitlement_state == "UNRESOLVED",
            self.retention_state == "UNRESOLVED",
            self.provider_selection_state == "UNSELECTED",
            self.credentials_state == "ABSENT",
            self.network_state == "DISABLED",
            self.external_activation_state == "BLOCKED",
            self.product_evidence_state == "BLOCKED",
            self.operator_review_required is True,
        )
        if not all(expected):
            raise ValueError("adapter activation gate cannot be opened in FCP-0009")
