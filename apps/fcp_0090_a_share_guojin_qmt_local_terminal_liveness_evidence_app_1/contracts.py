from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Iterable, Mapping


PHASE_ID = (
    "FCF-FCP-0090-A-SHARE-GUOJIN-QMT-LOCAL-TERMINAL-LIVENESS-"
    "EVIDENCE-APP-1"
)
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
REGISTERED_FAMILIES = (
    "BROKER_PROXY",
    "MINIBROKER",
    "MINIQUOTE",
    "XT_IT_CLIENT",
    "XT_MINI_QMT",
)
IMAGE_TO_FAMILY = MappingProxyType(
    {
        "brokerproxy.exe": "BROKER_PROXY",
        "minibroker.exe": "MINIBROKER",
        "miniquote.exe": "MINIQUOTE",
        "xtitclient.exe": "XT_IT_CLIENT",
        "xtminiqmt.exe": "XT_MINI_QMT",
    }
)
TERMINAL_FAMILIES = frozenset({"XT_IT_CLIENT", "XT_MINI_QMT"})


def _safe_id(value: str, field: str) -> str:
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise ValueError(f"{field} must be a safe identifier")
    return value


def _utc(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("observed_at must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


@dataclass(frozen=True)
class TerminalLivenessRegistration:
    artifact_id: str
    source_kind: str
    registered_families: tuple[str, ...]
    max_observed_processes: int

    def __post_init__(self) -> None:
        _safe_id(self.artifact_id, "artifact_id")
        if self.source_kind != "WINDOWS_LOCAL_PROCESS_NAME_SNAPSHOT":
            raise ValueError("source_kind is not registered")
        if self.registered_families != REGISTERED_FAMILIES:
            raise ValueError("registered_families must match the closed registry")
        if not 1 <= self.max_observed_processes <= 16384:
            raise ValueError("max_observed_processes is outside the safe range")

    def payload(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "max_observed_processes": self.max_observed_processes,
            "registered_families": list(self.registered_families),
            "source_kind": self.source_kind,
        }

    @property
    def contract_sha256(self) -> str:
        return _digest(self.payload())


DEFAULT_REGISTRATION = TerminalLivenessRegistration(
    artifact_id="guojin-qmt-local-terminal-liveness-v1",
    source_kind="WINDOWS_LOCAL_PROCESS_NAME_SNAPSHOT",
    registered_families=REGISTERED_FAMILIES,
    max_observed_processes=4096,
)


@dataclass(frozen=True)
class TerminalLivenessSnapshot:
    artifact_id: str
    observed_at_utc: str
    observed_process_count: int
    family_counts: Mapping[str, int]
    readiness_state: str
    snapshot_sha256: str

    def __post_init__(self) -> None:
        _safe_id(self.artifact_id, "artifact_id")
        if self.observed_process_count < 0:
            raise ValueError("observed_process_count must be non-negative")
        counts = dict(self.family_counts)
        if tuple(counts) != REGISTERED_FAMILIES:
            raise ValueError("family_counts must match the closed registry")
        if any(not isinstance(value, int) or value < 0 for value in counts.values()):
            raise ValueError("family counts must be non-negative integers")
        expected = (
            "TERMINAL_OBSERVED"
            if any(counts[name] > 0 for name in TERMINAL_FAMILIES)
            else "TERMINAL_NOT_OBSERVED"
        )
        if self.readiness_state != expected:
            raise ValueError("readiness_state conflicts with family counts")
        if not re.fullmatch(r"[0-9a-f]{64}", self.snapshot_sha256):
            raise ValueError("snapshot_sha256 must be lowercase SHA-256")
        object.__setattr__(self, "family_counts", MappingProxyType(counts))

    def payload_without_hash(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "family_counts": dict(self.family_counts),
            "observed_at_utc": self.observed_at_utc,
            "observed_process_count": self.observed_process_count,
            "readiness_state": self.readiness_state,
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_hash(), "snapshot_sha256": self.snapshot_sha256}


@dataclass(frozen=True)
class TerminalLivenessEvidence:
    phase_id: str
    contract_sha256: str
    snapshot: TerminalLivenessSnapshot
    blockers: tuple[str, ...]
    gap_104_status: str
    entitlement_authority: bool
    market_data_authority: bool
    provider_selection_authority: bool
    realtime_activation_authority: bool
    data_promotion_authority: bool
    product_authority: bool
    execution_authority: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.phase_id != PHASE_ID:
            raise ValueError("phase_id mismatch")
        if self.gap_104_status != "RESEARCH_REQUIRED":
            raise ValueError("GAP-104 must remain open")
        authorities = (
            self.entitlement_authority,
            self.market_data_authority,
            self.provider_selection_authority,
            self.realtime_activation_authority,
            self.data_promotion_authority,
            self.product_authority,
            self.execution_authority,
        )
        if any(authorities):
            raise ValueError("liveness evidence cannot grant authority")
        if not re.fullmatch(r"[0-9a-f]{64}", self.evidence_hash):
            raise ValueError("evidence_hash must be lowercase SHA-256")

    def payload_without_hash(self) -> dict[str, object]:
        return {
            "blockers": list(self.blockers),
            "contract_sha256": self.contract_sha256,
            "data_promotion_authority": self.data_promotion_authority,
            "entitlement_authority": self.entitlement_authority,
            "execution_authority": self.execution_authority,
            "gap_104_status": self.gap_104_status,
            "market_data_authority": self.market_data_authority,
            "phase_id": self.phase_id,
            "product_authority": self.product_authority,
            "provider_selection_authority": self.provider_selection_authority,
            "realtime_activation_authority": self.realtime_activation_authority,
            "snapshot": self.snapshot.payload(),
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_hash(), "evidence_hash": self.evidence_hash}


def build_snapshot(
    process_image_names: Iterable[str],
    observed_at: datetime,
    registration: TerminalLivenessRegistration = DEFAULT_REGISTRATION,
) -> TerminalLivenessSnapshot:
    counts = {name: 0 for name in registration.registered_families}
    observed_count = 0
    for raw_name in process_image_names:
        observed_count += 1
        if observed_count > registration.max_observed_processes:
            raise ValueError("observed process count exceeds the registered limit")
        if not isinstance(raw_name, str):
            raise ValueError("process image names must be strings")
        family = IMAGE_TO_FAMILY.get(raw_name.strip().lower())
        if family is not None:
            counts[family] += 1
    readiness = (
        "TERMINAL_OBSERVED"
        if any(counts[name] > 0 for name in TERMINAL_FAMILIES)
        else "TERMINAL_NOT_OBSERVED"
    )
    payload = {
        "artifact_id": registration.artifact_id,
        "family_counts": counts,
        "observed_at_utc": _utc(observed_at),
        "observed_process_count": observed_count,
        "readiness_state": readiness,
    }
    return TerminalLivenessSnapshot(
        **payload,
        snapshot_sha256=_digest(payload),
    )


def build_evidence(
    snapshot: TerminalLivenessSnapshot,
    registration: TerminalLivenessRegistration = DEFAULT_REGISTRATION,
) -> TerminalLivenessEvidence:
    blockers = [
        "MINIQMT_ENTITLEMENT_UNPROVEN",
        "READ_ONLY_MARKET_DATA_PROBE_UNPROVEN",
    ]
    if snapshot.readiness_state != "TERMINAL_OBSERVED":
        blockers.append("QMT_TERMINAL_NOT_OBSERVED")
    payload = {
        "blockers": blockers,
        "contract_sha256": registration.contract_sha256,
        "data_promotion_authority": False,
        "entitlement_authority": False,
        "execution_authority": False,
        "gap_104_status": "RESEARCH_REQUIRED",
        "market_data_authority": False,
        "phase_id": PHASE_ID,
        "product_authority": False,
        "provider_selection_authority": False,
        "realtime_activation_authority": False,
        "snapshot": snapshot.payload(),
    }
    return TerminalLivenessEvidence(
        phase_id=PHASE_ID,
        contract_sha256=registration.contract_sha256,
        snapshot=snapshot,
        blockers=tuple(blockers),
        gap_104_status="RESEARCH_REQUIRED",
        entitlement_authority=False,
        market_data_authority=False,
        provider_selection_authority=False,
        realtime_activation_authority=False,
        data_promotion_authority=False,
        product_authority=False,
        execution_authority=False,
        evidence_hash=_digest(payload),
    )


def render_evidence_json(evidence: TerminalLivenessEvidence) -> str:
    return _canonical(evidence.payload()).decode("ascii")
