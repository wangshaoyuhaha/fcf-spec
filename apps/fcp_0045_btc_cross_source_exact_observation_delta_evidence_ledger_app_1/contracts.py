from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    canonical_sha256,
    decimal_text,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


COMMON_FIELDS = (
    "observation_id",
    "artifact_id",
    "venue_id",
    "source_sequence",
    "received_at_utc",
    "ingested_at_utc",
    "schema_version",
    "header_hash",
    "observation_hash",
)
KIND_FIELDS = {
    "TRADE": ("price", "quantity", "aggressor_side"),
    "BOOK_SNAPSHOT": ("bids", "asks"),
    "BOOK_DELTA": ("previous_sequence", "bid_updates", "ask_updates"),
    "REFERENCE_PRICE": ("mark_price", "index_price"),
    "FUNDING": ("funding_rate", "interval_start_utc", "interval_end_utc"),
}
FIELD_KINDS = {
    "observation_id": "EXACT_TEXT",
    "artifact_id": "EXACT_TEXT",
    "venue_id": "EXACT_TEXT",
    "source_sequence": "ABS_INTEGER",
    "received_at_utc": "ABS_SECONDS",
    "ingested_at_utc": "ABS_SECONDS",
    "schema_version": "ABS_INTEGER",
    "header_hash": "EXACT_HASH",
    "observation_hash": "EXACT_HASH",
    "price": "EXACT_DECIMAL",
    "quantity": "EXACT_DECIMAL",
    "aggressor_side": "EXACT_TEXT",
    "bids": "EXACT_LEVELS",
    "asks": "EXACT_LEVELS",
    "previous_sequence": "ABS_INTEGER",
    "bid_updates": "EXACT_LEVELS",
    "ask_updates": "EXACT_LEVELS",
    "mark_price": "EXACT_DECIMAL",
    "index_price": "EXACT_DECIMAL",
    "funding_rate": "EXACT_DECIMAL",
    "interval_start_utc": "ABS_SECONDS",
    "interval_end_utc": "ABS_SECONDS",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def ledger_fields(observation_kind: str) -> tuple[str, ...]:
    try:
        return COMMON_FIELDS + KIND_FIELDS[observation_kind]
    except KeyError as exc:
        raise ValueError("observation kind is not registered") from exc


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return value


def _ascii_text(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be text")
    result = value.strip()
    if not result or len(result) > 2000 or any(ord(char) < 32 or ord(char) > 126 for char in result):
        raise ValueError(f"{name} must be bounded printable ASCII")
    return result


def _canonical_decimal(value: object, name: str) -> str:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{name} must use an exact decimal value")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{name} must be decimal-compatible") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return decimal_text(result)


def _canonical_integer(value: object, name: str) -> str:
    result = _ascii_text(value, name)
    try:
        parsed = int(result)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if str(parsed) != result:
        raise ValueError(f"{name} must be a canonical integer")
    return result


def _canonical_levels(value: object, name: str) -> str:
    text = _ascii_text(value, name)
    try:
        rows = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} must be canonical level JSON") from exc
    if not isinstance(rows, list):
        raise ValueError(f"{name} must be canonical level JSON")
    canonical = []
    for row in rows:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError(f"{name} must contain price and quantity pairs")
        canonical.append(
            [
                _canonical_decimal(row[0], f"{name} price"),
                _canonical_decimal(row[1], f"{name} quantity"),
            ]
        )
    result = json.dumps(canonical, ensure_ascii=True, separators=(",", ":"))
    if result != text:
        raise ValueError(f"{name} must be canonical level JSON")
    return result


def _canonical_value(value: object | None, kind: str, name: str) -> str | None:
    if value is None:
        return None
    if kind == "EXACT_DECIMAL":
        return _canonical_decimal(value, name)
    if kind == "ABS_INTEGER":
        return _canonical_integer(value, name)
    if kind == "ABS_SECONDS":
        return utc(value, name)
    if kind == "EXACT_HASH":
        return _digest(value, name)
    if kind == "EXACT_LEVELS":
        return _canonical_levels(value, name)
    if kind == "EXACT_TEXT":
        return _ascii_text(value, name)
    raise ValueError("delta kind is not registered")


def _expected_delta(left: str | None, right: str | None, kind: str) -> str | None:
    if left is None or right is None:
        return None
    if kind == "EXACT_DECIMAL":
        return decimal_text(abs(Decimal(left) - Decimal(right)))
    if kind == "ABS_INTEGER":
        return str(abs(int(left) - int(right)))
    if kind == "ABS_SECONDS":
        return str(round(abs((instant(left) - instant(right)).total_seconds())))
    return None


@dataclass(frozen=True)
class BTCObservationDatasetLineage:
    dataset_id: str
    dataset_hash: str
    source_id: str
    artifact_id: str
    artifact_hash: str
    lineage_hash: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("dataset_id", "source_id", "artifact_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        for name in ("dataset_hash", "artifact_hash"):
            object.__setattr__(self, name, _digest(getattr(self, name), name))
        object.__setattr__(
            self,
            "lineage_hash",
            canonical_sha256(
                {
                    "artifact_hash": self.artifact_hash,
                    "artifact_id": self.artifact_id,
                    "dataset_hash": self.dataset_hash,
                    "dataset_id": self.dataset_id,
                    "source_id": self.source_id,
                }
            ),
        )


@dataclass(frozen=True)
class BTCObservationDeltaEvidenceEntry:
    left_dataset_id: str
    right_dataset_id: str
    instrument_id: str
    instrument_kind: str
    observation_kind: str
    event_at_utc: str
    field_name: str
    delta_kind: str
    left_value: str | None
    right_value: str | None
    delta_value: str | None
    comparison_state: str
    entry_hash: str = field(init=False)

    def __post_init__(self) -> None:
        left_id = identifier(self.left_dataset_id, "left_dataset_id")
        right_id = identifier(self.right_dataset_id, "right_dataset_id")
        if left_id >= right_id:
            raise ValueError("entry dataset pair must be strictly ordered")
        instrument = identifier(self.instrument_id, "instrument_id")
        instrument_kind = str(self.instrument_kind).strip().upper()
        if instrument_kind not in {"SPOT", "PERPETUAL"}:
            raise ValueError("instrument kind is not registered")
        observation_kind = str(self.observation_kind).strip().upper()
        fields = ledger_fields(observation_kind)
        if self.field_name not in fields:
            raise ValueError("ledger field is not registered for observation kind")
        expected_kind = FIELD_KINDS[self.field_name]
        if self.delta_kind != expected_kind:
            raise ValueError("delta kind disagrees with ledger field")
        event = utc(self.event_at_utc, "event_at_utc")
        left = _canonical_value(self.left_value, expected_kind, "left_value")
        right = _canonical_value(self.right_value, expected_kind, "right_value")
        delta = _expected_delta(left, right, expected_kind)
        state = (
            "PAIR_INCOMPLETE"
            if left is None or right is None
            else "EXACT_MATCH"
            if left == right
            else "DELTA_PRESENT"
        )
        if self.delta_value != delta or self.comparison_state != state:
            raise ValueError("observation delta evidence is inconsistent")
        object.__setattr__(self, "left_dataset_id", left_id)
        object.__setattr__(self, "right_dataset_id", right_id)
        object.__setattr__(self, "instrument_id", instrument)
        object.__setattr__(self, "instrument_kind", instrument_kind)
        object.__setattr__(self, "observation_kind", observation_kind)
        object.__setattr__(self, "event_at_utc", event)
        object.__setattr__(self, "left_value", left)
        object.__setattr__(self, "right_value", right)
        object.__setattr__(
            self,
            "entry_hash",
            canonical_sha256(
                {
                    "comparison_state": state,
                    "delta_kind": expected_kind,
                    "delta_value": delta,
                    "event_at_utc": event,
                    "field_name": self.field_name,
                    "instrument_id": instrument,
                    "instrument_kind": instrument_kind,
                    "left_dataset_id": left_id,
                    "left_value": left,
                    "observation_kind": observation_kind,
                    "right_dataset_id": right_id,
                    "right_value": right,
                }
            ),
        )


@dataclass(frozen=True)
class BTCCrossSourceExactObservationDeltaEvidenceLedger:
    dataset_lineage: tuple[BTCObservationDatasetLineage, ...]
    policy_id: str
    policy_hash: str
    reconciliation_result_hash: str
    reconciliation_quality_state: str
    finding_hashes: tuple[str, ...]
    dataset_pair_count: int
    pair_key_count: int
    entries: tuple[BTCObservationDeltaEvidenceEntry, ...]
    exact_match_entry_count: int
    delta_entry_count: int
    incomplete_entry_count: int
    ledger_state: str = "READ_ONLY_REGISTERED_EVIDENCE_ONLY"
    operator_review_required: bool = True
    tolerance_changed: bool = False
    severity_changed: bool = False
    quality_state_changed: bool = False
    source_ranked: bool = False
    source_selected: bool = False
    evidence_replaced: bool = False
    gap_closed: bool = False
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    ledger_hash: str = field(init=False)

    def __post_init__(self) -> None:
        lineage = tuple(self.dataset_lineage)
        if len(lineage) < 2 or not all(isinstance(item, BTCObservationDatasetLineage) for item in lineage):
            raise ValueError("ledger requires typed dataset lineage")
        ids = tuple(item.dataset_id for item in lineage)
        hashes = tuple(item.dataset_hash for item in lineage)
        if ids != tuple(sorted(ids)) or len(ids) != len(set(ids)) or len(hashes) != len(set(hashes)):
            raise ValueError("dataset lineage must be ordered and distinct")
        policy_id = identifier(self.policy_id, "policy_id")
        policy_hash = _digest(self.policy_hash, "policy_hash")
        result_hash = _digest(self.reconciliation_result_hash, "reconciliation_result_hash")
        finding_hashes = tuple(_digest(item, "finding_hash") for item in self.finding_hashes)
        if finding_hashes != tuple(sorted(finding_hashes)) or len(finding_hashes) != len(set(finding_hashes)):
            raise ValueError("finding hashes must be ordered and unique")
        if self.reconciliation_quality_state not in {"CONSISTENT", "QUARANTINE_REVIEW_REQUIRED"}:
            raise ValueError("reconciliation quality state is not registered")
        expected_pairs = len(lineage) * (len(lineage) - 1) // 2
        if self.dataset_pair_count != expected_pairs:
            raise ValueError("dataset pair count disagrees with lineage")
        entries = tuple(self.entries)
        if not entries or not all(isinstance(item, BTCObservationDeltaEvidenceEntry) for item in entries):
            raise ValueError("ledger requires typed observation delta entries")
        lineage_ids = set(ids)
        if any({item.left_dataset_id, item.right_dataset_id} - lineage_ids for item in entries):
            raise ValueError("entry dataset lineage is not registered")
        keys = tuple(
            (
                item.left_dataset_id,
                item.right_dataset_id,
                item.instrument_id,
                item.instrument_kind,
                item.observation_kind,
                item.event_at_utc,
                ledger_fields(item.observation_kind).index(item.field_name),
            )
            for item in entries
        )
        if keys != tuple(sorted(keys)) or len(keys) != len(set(keys)):
            raise ValueError("ledger entries must be ordered and unique")
        groups: dict[tuple[str, ...], list[str]] = {}
        for item in entries:
            key = (
                item.left_dataset_id,
                item.right_dataset_id,
                item.instrument_id,
                item.instrument_kind,
                item.observation_kind,
                item.event_at_utc,
            )
            groups.setdefault(key, []).append(item.field_name)
        if self.pair_key_count != len(groups) or any(
            tuple(fields) != ledger_fields(key[4]) for key, fields in groups.items()
        ):
            raise ValueError("ledger field coverage disagrees with pair keys")
        counts = {
            state: sum(item.comparison_state == state for item in entries)
            for state in ("EXACT_MATCH", "DELTA_PRESENT", "PAIR_INCOMPLETE")
        }
        if (
            self.exact_match_entry_count != counts["EXACT_MATCH"]
            or self.delta_entry_count != counts["DELTA_PRESENT"]
            or self.incomplete_entry_count != counts["PAIR_INCOMPLETE"]
        ):
            raise ValueError("ledger state counts disagree with entries")
        if self.ledger_state != "READ_ONLY_REGISTERED_EVIDENCE_ONLY":
            raise ValueError("ledger state is immutable")
        if (
            self.operator_review_required is not True
            or any(
                (
                    self.tolerance_changed,
                    self.severity_changed,
                    self.quality_state_changed,
                    self.source_ranked,
                    self.source_selected,
                    self.evidence_replaced,
                    self.gap_closed,
                )
            )
        ):
            raise ValueError("ledger cannot decide, mutate, select, replace, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("ledger authority identities are immutable")
        object.__setattr__(self, "dataset_lineage", lineage)
        object.__setattr__(self, "entries", entries)
        object.__setattr__(self, "policy_id", policy_id)
        object.__setattr__(self, "policy_hash", policy_hash)
        object.__setattr__(self, "reconciliation_result_hash", result_hash)
        object.__setattr__(self, "finding_hashes", finding_hashes)
        object.__setattr__(
            self,
            "ledger_hash",
            canonical_sha256(
                {
                    "dataset_lineage_hashes": [item.lineage_hash for item in lineage],
                    "dataset_pair_count": self.dataset_pair_count,
                    "delta_entry_count": self.delta_entry_count,
                    "entry_hashes": [item.entry_hash for item in entries],
                    "exact_match_entry_count": self.exact_match_entry_count,
                    "finding_hashes": finding_hashes,
                    "incomplete_entry_count": self.incomplete_entry_count,
                    "ledger_state": self.ledger_state,
                    "pair_key_count": self.pair_key_count,
                    "policy_hash": policy_hash,
                    "policy_id": policy_id,
                    "reconciliation_quality_state": self.reconciliation_quality_state,
                    "reconciliation_result_hash": result_hash,
                }
            ),
        )
