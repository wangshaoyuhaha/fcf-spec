from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Callable, Mapping

from apps.fcp_0090_a_share_guojin_qmt_local_terminal_liveness_evidence_app_1.contracts import (
    TerminalLivenessSnapshot,
)


PHASE_ID = (
    "FCF-FCP-0091-A-SHARE-GUOJIN-QMT-REGISTERED-LOCAL-CACHE-LOOPBACK-"
    "READ-ONLY-PROBE-APP-1"
)
SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
CALL_STATES = (
    "NOT_RUN",
    "CALL_FAILED",
    "CALL_SUCCEEDED_EMPTY",
    "CALL_SUCCEEDED_WITH_ROWS",
)
TIMING_CLASSES = ("NOT_MEASURED", "LT_1S", "LT_5S", "LT_30S", "GE_30S")


def _canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("ascii")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(value: str, field: str) -> str:
    normalized = str(value).lower()
    if not re.fullmatch(r"[0-9a-f]{64}", normalized):
        raise ValueError(f"{field} must be lowercase SHA-256")
    return normalized


@dataclass(frozen=True)
class LocalCacheProbeRegistration:
    artifact_id: str
    function_identity: str
    symbol: str
    market: str
    period: str
    start_date: str
    end_date: str
    fields: tuple[str, ...]
    count: int
    dividend_type: str
    fill_data: bool
    server_retrieval_allowed: bool
    native_module_sha256: str
    xtdata_source_sha256: str

    def __post_init__(self) -> None:
        if not SAFE_ID.fullmatch(self.artifact_id):
            raise ValueError("artifact_id must be a safe identifier")
        exact = (
            self.artifact_id == "guojin-qmt-local-cache-loopback-probe-v1",
            self.function_identity == "xtquant.xtdata.get_local_data",
            self.symbol == "600000.SH",
            self.market == "SSE",
            self.period == "1d",
            self.start_date == "20260721",
            self.end_date == "20260721",
            self.fields == ("time",),
            self.count == 1,
            self.dividend_type == "none",
            self.fill_data is False,
            self.server_retrieval_allowed is False,
            self.native_module_sha256
            == "bfefebaa08f25666c86f73e714c100f4fbdcd308332453ed16bdd619d8a0d847",
            self.xtdata_source_sha256
            == "52bc303c97b5deb207888821a27c0af4d268f81dc252dfdffca964ba0568ae3e",
        )
        if not all(exact):
            raise ValueError("probe registration must match the closed request")
        object.__setattr__(
            self,
            "native_module_sha256",
            _sha(self.native_module_sha256, "native_module_sha256"),
        )
        object.__setattr__(
            self,
            "xtdata_source_sha256",
            _sha(self.xtdata_source_sha256, "xtdata_source_sha256"),
        )

    def payload(self) -> dict[str, object]:
        return {
            "artifact_id": self.artifact_id,
            "count": self.count,
            "dividend_type": self.dividend_type,
            "end_date": self.end_date,
            "fields": list(self.fields),
            "fill_data": self.fill_data,
            "function_identity": self.function_identity,
            "market": self.market,
            "native_module_sha256": self.native_module_sha256,
            "period": self.period,
            "server_retrieval_allowed": self.server_retrieval_allowed,
            "start_date": self.start_date,
            "symbol": self.symbol,
            "xtdata_source_sha256": self.xtdata_source_sha256,
        }

    @property
    def contract_sha256(self) -> str:
        return _digest(self.payload())


DEFAULT_REGISTRATION = LocalCacheProbeRegistration(
    artifact_id="guojin-qmt-local-cache-loopback-probe-v1",
    function_identity="xtquant.xtdata.get_local_data",
    symbol="600000.SH",
    market="SSE",
    period="1d",
    start_date="20260721",
    end_date="20260721",
    fields=("time",),
    count=1,
    dividend_type="none",
    fill_data=False,
    server_retrieval_allowed=False,
    native_module_sha256="bfefebaa08f25666c86f73e714c100f4fbdcd308332453ed16bdd619d8a0d847",
    xtdata_source_sha256="52bc303c97b5deb207888821a27c0af4d268f81dc252dfdffca964ba0568ae3e",
)


@dataclass(frozen=True)
class LocalCacheProbeEvidence:
    phase_id: str
    contract_sha256: str
    terminal_snapshot_sha256: str
    call_state: str
    call_attempted: bool
    call_count: int
    row_count: int
    schema_state: str
    timing_class: str
    blockers: tuple[str, ...]
    gap_104_status: str
    entitlement_authority: bool
    provider_selection_authority: bool
    realtime_activation_authority: bool
    data_promotion_authority: bool
    product_authority: bool
    execution_authority: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.phase_id != PHASE_ID:
            raise ValueError("phase_id must match FCP-0091")
        object.__setattr__(
            self,
            "contract_sha256",
            _sha(self.contract_sha256, "contract_sha256"),
        )
        object.__setattr__(
            self,
            "terminal_snapshot_sha256",
            _sha(self.terminal_snapshot_sha256, "terminal_snapshot_sha256"),
        )
        object.__setattr__(
            self,
            "evidence_hash",
            _sha(self.evidence_hash, "evidence_hash"),
        )
        if self.call_state not in CALL_STATES:
            raise ValueError("call_state must be registered")
        if self.timing_class not in TIMING_CLASSES:
            raise ValueError("timing_class must be registered")
        if self.schema_state not in {
            "NOT_INSPECTED",
            "EMPTY_MAPPING",
            "EXACT_TIME_ONLY",
            "REJECTED_OR_UNAVAILABLE",
        }:
            raise ValueError("schema_state must be registered")
        if type(self.call_count) is not int or self.call_count not in {0, 1}:
            raise ValueError("call_count must be zero or one")
        if type(self.row_count) is not int or self.row_count not in {0, 1}:
            raise ValueError("row_count must be zero or one")
        if tuple(sorted(set(self.blockers))) != self.blockers:
            raise ValueError("blockers must be sorted and unique")
        if not all(SAFE_ID.fullmatch(item) for item in self.blockers):
            raise ValueError("blockers must use safe identifiers")
        if self.gap_104_status != "RESEARCH_REQUIRED":
            raise ValueError("GAP-104 must remain open")
        authorities = (
            self.entitlement_authority,
            self.provider_selection_authority,
            self.realtime_activation_authority,
            self.data_promotion_authority,
            self.product_authority,
            self.execution_authority,
        )
        if any(authorities):
            raise ValueError("probe evidence cannot grant authority")
        baseline = {
            "MINIQMT_ENTITLEMENT_UNPROVEN",
            "RIGHTS_AND_RETENTION_UNPROVEN",
        }
        if not baseline.issubset(self.blockers):
            raise ValueError("external blockers must remain open")
        if self.call_state == "NOT_RUN":
            exact = (
                self.call_attempted is False,
                self.call_count == 0,
                self.row_count == 0,
                self.schema_state == "NOT_INSPECTED",
                self.timing_class == "NOT_MEASURED",
                "QMT_TERMINAL_NOT_OBSERVED" in self.blockers,
                "LOCAL_CACHE_PROBE_FAILED" not in self.blockers,
            )
        elif self.call_state == "CALL_FAILED":
            exact = (
                self.call_attempted is True,
                self.call_count == 1,
                self.row_count == 0,
                self.schema_state == "REJECTED_OR_UNAVAILABLE",
                self.timing_class != "NOT_MEASURED",
                "QMT_TERMINAL_NOT_OBSERVED" not in self.blockers,
                "LOCAL_CACHE_PROBE_FAILED" in self.blockers,
            )
        elif self.call_state == "CALL_SUCCEEDED_EMPTY":
            exact = (
                self.call_attempted is True,
                self.call_count == 1,
                self.row_count == 0,
                self.schema_state == "EMPTY_MAPPING",
                self.timing_class != "NOT_MEASURED",
                "QMT_TERMINAL_NOT_OBSERVED" not in self.blockers,
                "LOCAL_CACHE_PROBE_FAILED" not in self.blockers,
            )
        else:
            exact = (
                self.call_attempted is True,
                self.call_count == 1,
                self.row_count == 1,
                self.schema_state == "EXACT_TIME_ONLY",
                self.timing_class != "NOT_MEASURED",
                "QMT_TERMINAL_NOT_OBSERVED" not in self.blockers,
                "LOCAL_CACHE_PROBE_FAILED" not in self.blockers,
            )
        if not all(exact):
            raise ValueError("probe evidence state is inconsistent")
        if self.evidence_hash != _digest(self.payload_without_hash()):
            raise ValueError("evidence_hash does not match the payload")

    def payload_without_hash(self) -> dict[str, object]:
        return {
            "blockers": list(self.blockers),
            "call_attempted": self.call_attempted,
            "call_count": self.call_count,
            "call_state": self.call_state,
            "contract_sha256": self.contract_sha256,
            "data_promotion_authority": self.data_promotion_authority,
            "entitlement_authority": self.entitlement_authority,
            "execution_authority": self.execution_authority,
            "gap_104_status": self.gap_104_status,
            "phase_id": self.phase_id,
            "product_authority": self.product_authority,
            "provider_selection_authority": self.provider_selection_authority,
            "realtime_activation_authority": self.realtime_activation_authority,
            "row_count": self.row_count,
            "schema_state": self.schema_state,
            "terminal_snapshot_sha256": self.terminal_snapshot_sha256,
            "timing_class": self.timing_class,
        }

    def payload(self) -> dict[str, object]:
        return {**self.payload_without_hash(), "evidence_hash": self.evidence_hash}


def _timing_class(elapsed_ms: int | None) -> str:
    if elapsed_ms is None:
        return "NOT_MEASURED"
    if not isinstance(elapsed_ms, int) or elapsed_ms < 0:
        raise ValueError("elapsed_ms must be a non-negative integer")
    if elapsed_ms < 1000:
        return "LT_1S"
    if elapsed_ms < 5000:
        return "LT_5S"
    if elapsed_ms < 30000:
        return "LT_30S"
    return "GE_30S"


def _summarize_result(result: object, symbol: str) -> tuple[int, str]:
    if not isinstance(result, Mapping):
        raise ValueError("probe result must be a mapping")
    if not result:
        return 0, "EMPTY_MAPPING"
    if tuple(result) != (symbol,):
        raise ValueError("probe result keys do not match the registration")
    frame = result[symbol]
    shape = getattr(frame, "shape", None)
    columns = getattr(frame, "columns", None)
    if not isinstance(shape, tuple) or len(shape) != 2:
        raise ValueError("probe frame shape is invalid")
    rows, width = shape
    if not isinstance(rows, int) or not isinstance(width, int):
        raise ValueError("probe frame shape must use integers")
    if rows < 0 or rows > 1 or width != 1:
        raise ValueError("probe frame shape exceeds the closed request")
    if tuple(str(column) for column in columns) != ("time",):
        raise ValueError("probe frame schema does not match time-only")
    return rows, "EXACT_TIME_ONLY"


def build_probe_evidence(
    terminal_snapshot: TerminalLivenessSnapshot,
    probe_call: Callable[[], object],
    *,
    elapsed_ms: int | None = None,
    registration: LocalCacheProbeRegistration = DEFAULT_REGISTRATION,
) -> LocalCacheProbeEvidence:
    blockers = ["MINIQMT_ENTITLEMENT_UNPROVEN", "RIGHTS_AND_RETENTION_UNPROVEN"]
    call_attempted = False
    call_count = 0
    row_count = 0
    schema_state = "NOT_INSPECTED"
    timing = "NOT_MEASURED"
    if terminal_snapshot.readiness_state != "TERMINAL_OBSERVED":
        call_state = "NOT_RUN"
        blockers.append("QMT_TERMINAL_NOT_OBSERVED")
    else:
        call_attempted = True
        call_count = 1
        timing = _timing_class(elapsed_ms)
        try:
            result = probe_call()
            row_count, schema_state = _summarize_result(result, registration.symbol)
            call_state = (
                "CALL_SUCCEEDED_WITH_ROWS" if row_count else "CALL_SUCCEEDED_EMPTY"
            )
        except Exception:
            call_state = "CALL_FAILED"
            schema_state = "REJECTED_OR_UNAVAILABLE"
            blockers.append("LOCAL_CACHE_PROBE_FAILED")
    payload = {
        "blockers": sorted(blockers),
        "call_attempted": call_attempted,
        "call_count": call_count,
        "call_state": call_state,
        "contract_sha256": registration.contract_sha256,
        "data_promotion_authority": False,
        "entitlement_authority": False,
        "execution_authority": False,
        "gap_104_status": "RESEARCH_REQUIRED",
        "phase_id": PHASE_ID,
        "product_authority": False,
        "provider_selection_authority": False,
        "realtime_activation_authority": False,
        "row_count": row_count,
        "schema_state": schema_state,
        "terminal_snapshot_sha256": terminal_snapshot.snapshot_sha256,
        "timing_class": timing,
    }
    return LocalCacheProbeEvidence(
        phase_id=PHASE_ID,
        contract_sha256=registration.contract_sha256,
        terminal_snapshot_sha256=terminal_snapshot.snapshot_sha256,
        call_state=call_state,
        call_attempted=call_attempted,
        call_count=call_count,
        row_count=row_count,
        schema_state=schema_state,
        timing_class=timing,
        blockers=tuple(sorted(blockers)),
        gap_104_status="RESEARCH_REQUIRED",
        entitlement_authority=False,
        provider_selection_authority=False,
        realtime_activation_authority=False,
        data_promotion_authority=False,
        product_authority=False,
        execution_authority=False,
        evidence_hash=_digest(payload),
    )


def render_probe_evidence_json(evidence: LocalCacheProbeEvidence) -> str:
    return _canonical(evidence.payload()).decode("ascii")
