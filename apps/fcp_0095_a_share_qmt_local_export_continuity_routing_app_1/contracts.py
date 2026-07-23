from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from typing import Mapping


PHASE_ID = (
    "FCF-FCP-0095-A-SHARE-QMT-LOCAL-EXPORT-CONTINUITY-ROUTING-APP-1"
)
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def _canonical(payload: Mapping[str, object]) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _digest(payload: Mapping[str, object]) -> str:
    return hashlib.sha256(_canonical(payload)).hexdigest()


def _safe(value: str, name: str) -> str:
    if not isinstance(value, str) or not SAFE_ID.fullmatch(value):
        raise ValueError(f"{name} must be a safe identifier")
    return value


def _sha(value: str, name: str) -> str:
    if not isinstance(value, str) or not SHA256.fullmatch(value):
        raise ValueError(f"{name} must be a SHA-256 digest")
    return value


@dataclass(frozen=True)
class RuntimeCompatibilityEvidence:
    artifact_id: str
    terminal_liveness_snapshot_sha256: str
    terminal_liveness_evidence_hash: str
    probe_terminal_snapshot_sha256: str
    local_cache_probe_evidence_hash: str
    terminal_state: str
    observed_family: str
    loopback_call_state: str
    loopback_call_count: int
    loopback_row_count: int
    gap_104_status: str
    evidence_hash: str

    def __post_init__(self) -> None:
        _safe(self.artifact_id, "artifact_id")
        _sha(
            self.terminal_liveness_snapshot_sha256,
            "terminal_liveness_snapshot_sha256",
        )
        _sha(
            self.terminal_liveness_evidence_hash,
            "terminal_liveness_evidence_hash",
        )
        _sha(
            self.probe_terminal_snapshot_sha256,
            "probe_terminal_snapshot_sha256",
        )
        _sha(
            self.local_cache_probe_evidence_hash,
            "local_cache_probe_evidence_hash",
        )
        _sha(self.evidence_hash, "evidence_hash")
        exact = (
            self.artifact_id == "guojin-qmt-runtime-compatibility-evidence-v1",
            self.terminal_state == "TERMINAL_OBSERVED",
            self.observed_family == "XT_IT_CLIENT",
            self.loopback_call_state == "CALL_FAILED",
            type(self.loopback_call_count) is int,
            self.loopback_call_count == 1,
            type(self.loopback_row_count) is int,
            self.loopback_row_count == 0,
            self.gap_104_status == "RESEARCH_REQUIRED",
        )
        if not all(exact):
            raise ValueError("runtime compatibility evidence must be exact")
        if self.evidence_hash != _digest(self.payload_without_hash()):
            raise ValueError("evidence_hash does not match the payload")

    def payload_without_hash(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "gap_104_status": self.gap_104_status,
            "local_cache_probe_evidence_hash": (
                self.local_cache_probe_evidence_hash
            ),
            "loopback_call_count": self.loopback_call_count,
            "loopback_call_state": self.loopback_call_state,
            "loopback_row_count": self.loopback_row_count,
            "observed_family": self.observed_family,
            "probe_terminal_snapshot_sha256": (
                self.probe_terminal_snapshot_sha256
            ),
            "terminal_liveness_evidence_hash": (
                self.terminal_liveness_evidence_hash
            ),
            "terminal_liveness_snapshot_sha256": (
                self.terminal_liveness_snapshot_sha256
            ),
            "terminal_state": self.terminal_state,
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_hash(), "evidence_hash": self.evidence_hash}


@dataclass(frozen=True)
class ContinuityRoute:
    phase_id: str
    decision_id: str
    decided_at_utc: str
    runtime_evidence_hash: str
    routing_state: str
    active_research_route: str
    miniqmt_route_state: str
    candidate_supplement_routes: tuple[str, ...]
    next_actions: tuple[str, ...]
    open_gaps: tuple[str, ...]
    provider_selection_authority: bool
    data_promotion_authority: bool
    realtime_activation_authority: bool
    product_authority: bool
    account_authority: bool
    execution_authority: bool
    route_hash: str

    def __post_init__(self) -> None:
        if self.phase_id != PHASE_ID:
            raise ValueError("phase_id must match FCP-0095")
        _safe(self.decision_id, "decision_id")
        if not isinstance(self.decided_at_utc, str) or not UTC.fullmatch(
            self.decided_at_utc
        ):
            raise ValueError("decided_at_utc must be canonical UTC")
        _sha(self.runtime_evidence_hash, "runtime_evidence_hash")
        _sha(self.route_hash, "route_hash")
        exact = (
            self.routing_state == "LOCAL_EXPORT_RESEARCH_CONTINUITY",
            self.active_research_route == "REGISTERED_QMT_LOCAL_EXPORT",
            self.miniqmt_route_state == "DEFERRED_NON_BLOCKING",
            self.candidate_supplement_routes
            == ("RQDATA_TRIAL_CANDIDATE", "TUSHARE_CANDIDATE"),
            self.next_actions
            == (
                "REGISTER_LOCAL_EXPORT_BATCH",
                "VALIDATE_BATCH_COVERAGE",
                "RECONCILE_INDEPENDENT_CANDIDATE",
            ),
            self.open_gaps
            == tuple(f"V2-FR-GAP-{number:03d}" for number in range(93, 110)),
        )
        if not all(exact):
            raise ValueError("continuity route must preserve the closed registry")
        authorities = (
            self.provider_selection_authority,
            self.data_promotion_authority,
            self.realtime_activation_authority,
            self.product_authority,
            self.account_authority,
            self.execution_authority,
        )
        if any(authorities):
            raise ValueError("continuity route cannot grant authority")
        if self.route_hash != _digest(self.payload_without_hash()):
            raise ValueError("route_hash does not match the payload")

    def payload_without_hash(self) -> dict[str, object]:
        return {
            "account_authority": self.account_authority,
            "active_research_route": self.active_research_route,
            "candidate_supplement_routes": list(
                self.candidate_supplement_routes
            ),
            "data_promotion_authority": self.data_promotion_authority,
            "decided_at_utc": self.decided_at_utc,
            "decision_id": self.decision_id,
            "execution_authority": self.execution_authority,
            "miniqmt_route_state": self.miniqmt_route_state,
            "next_actions": list(self.next_actions),
            "open_gaps": list(self.open_gaps),
            "phase_id": self.phase_id,
            "product_authority": self.product_authority,
            "provider_selection_authority": self.provider_selection_authority,
            "realtime_activation_authority": self.realtime_activation_authority,
            "routing_state": self.routing_state,
            "runtime_evidence_hash": self.runtime_evidence_hash,
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_hash(), "route_hash": self.route_hash}


def build_runtime_evidence(
    *,
    terminal_liveness_snapshot_sha256: str,
    terminal_liveness_evidence_hash: str,
    probe_terminal_snapshot_sha256: str,
    local_cache_probe_evidence_hash: str,
) -> RuntimeCompatibilityEvidence:
    payload: dict[str, object] = {
        "artifact_id": "guojin-qmt-runtime-compatibility-evidence-v1",
        "gap_104_status": "RESEARCH_REQUIRED",
        "local_cache_probe_evidence_hash": local_cache_probe_evidence_hash,
        "loopback_call_count": 1,
        "loopback_call_state": "CALL_FAILED",
        "loopback_row_count": 0,
        "observed_family": "XT_IT_CLIENT",
        "probe_terminal_snapshot_sha256": probe_terminal_snapshot_sha256,
        "terminal_liveness_evidence_hash": terminal_liveness_evidence_hash,
        "terminal_liveness_snapshot_sha256": (
            terminal_liveness_snapshot_sha256
        ),
        "terminal_state": "TERMINAL_OBSERVED",
    }
    return RuntimeCompatibilityEvidence(**payload, evidence_hash=_digest(payload))


def build_route(
    evidence: RuntimeCompatibilityEvidence,
    *,
    decision_id: str,
    decided_at_utc: str,
) -> ContinuityRoute:
    if not isinstance(evidence, RuntimeCompatibilityEvidence):
        raise TypeError("evidence must be RuntimeCompatibilityEvidence")
    payload: dict[str, object] = {
        "account_authority": False,
        "active_research_route": "REGISTERED_QMT_LOCAL_EXPORT",
        "candidate_supplement_routes": (
            "RQDATA_TRIAL_CANDIDATE",
            "TUSHARE_CANDIDATE",
        ),
        "data_promotion_authority": False,
        "decided_at_utc": decided_at_utc,
        "decision_id": decision_id,
        "execution_authority": False,
        "miniqmt_route_state": "DEFERRED_NON_BLOCKING",
        "next_actions": (
            "REGISTER_LOCAL_EXPORT_BATCH",
            "VALIDATE_BATCH_COVERAGE",
            "RECONCILE_INDEPENDENT_CANDIDATE",
        ),
        "open_gaps": tuple(
            f"V2-FR-GAP-{number:03d}" for number in range(93, 110)
        ),
        "phase_id": PHASE_ID,
        "product_authority": False,
        "provider_selection_authority": False,
        "realtime_activation_authority": False,
        "routing_state": "LOCAL_EXPORT_RESEARCH_CONTINUITY",
        "runtime_evidence_hash": evidence.evidence_hash,
    }
    return ContinuityRoute(**payload, route_hash=_digest(payload))
