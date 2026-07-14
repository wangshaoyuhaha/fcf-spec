from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import RLock
from typing import Tuple


class RuntimeFaultCode(str, Enum):
    APPLICATION_DISPATCH_FAILURE = "APPLICATION_DISPATCH_FAILURE"
    CAPACITY_REJECTED = "CAPACITY_REJECTED"
    REQUEST_HANDLER_FAILURE = "REQUEST_HANDLER_FAILURE"
    SERVER_LOOP_FAILURE = "SERVER_LOOP_FAILURE"
    SHUTDOWN_FAILURE = "SHUTDOWN_FAILURE"


_FAULT_MESSAGES = {
    RuntimeFaultCode.APPLICATION_DISPATCH_FAILURE: (
        "application dispatch failed"
    ),
    RuntimeFaultCode.CAPACITY_REJECTED: (
        "request capacity was exhausted"
    ),
    RuntimeFaultCode.REQUEST_HANDLER_FAILURE: (
        "request handler failed"
    ),
    RuntimeFaultCode.SERVER_LOOP_FAILURE: (
        "server loop failed"
    ),
    RuntimeFaultCode.SHUTDOWN_FAILURE: (
        "server shutdown failed"
    ),
}


def _required_single_line(
    value: object,
    field_name: str,
) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be text")

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or "\r" in normalized
        or "\n" in normalized
    ):
        raise ValueError(
            f"{field_name} must be canonical single-line text"
        )

    return normalized


def _non_negative_integer(
    value: object,
    field_name: str,
) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 0
    ):
        raise ValueError(
            f"{field_name} must be a non-negative integer"
        )

    return value


@dataclass(frozen=True)
class RuntimeFaultRecord:
    sequence: int
    code: RuntimeFaultCode
    lifecycle_state: str
    message: str

    def __post_init__(self) -> None:
        if (
            isinstance(self.sequence, bool)
            or not isinstance(self.sequence, int)
            or self.sequence < 1
        ):
            raise ValueError(
                "sequence must be a positive integer"
            )

        if not isinstance(self.code, RuntimeFaultCode):
            raise ValueError(
                "code must be RuntimeFaultCode"
            )

        lifecycle_state = _required_single_line(
            self.lifecycle_state,
            "lifecycle_state",
        )
        message = _required_single_line(
            self.message,
            "message",
        )

        if message != _FAULT_MESSAGES[self.code]:
            raise ValueError(
                "fault message must match deterministic code"
            )

        object.__setattr__(
            self,
            "lifecycle_state",
            lifecycle_state,
        )
        object.__setattr__(
            self,
            "message",
            message,
        )


@dataclass(frozen=True)
class RuntimeDiagnosticsSnapshot:
    lifecycle_state: str
    host: str
    port: int
    active_request_count: int
    rejected_request_count: int
    fault_count: int
    recent_faults: Tuple[RuntimeFaultRecord, ...]
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        lifecycle_state = _required_single_line(
            self.lifecycle_state,
            "lifecycle_state",
        )
        host = _required_single_line(
            self.host,
            "host",
        )

        if host != "127.0.0.1":
            raise ValueError(
                "diagnostics host must remain exact loopback"
            )

        if (
            isinstance(self.port, bool)
            or not isinstance(self.port, int)
            or not 1024 <= self.port <= 65535
        ):
            raise ValueError(
                "diagnostics port must be between 1024 and 65535"
            )

        active = _non_negative_integer(
            self.active_request_count,
            "active_request_count",
        )
        rejected = _non_negative_integer(
            self.rejected_request_count,
            "rejected_request_count",
        )
        faults = _non_negative_integer(
            self.fault_count,
            "fault_count",
        )
        recent = tuple(self.recent_faults)

        if any(
            not isinstance(item, RuntimeFaultRecord)
            for item in recent
        ):
            raise ValueError(
                "recent_faults must contain RuntimeFaultRecord values"
            )

        if len(recent) > faults:
            raise ValueError(
                "recent_faults cannot exceed fault_count"
            )

        sequences = tuple(
            item.sequence
            for item in recent
        )

        if sequences != tuple(sorted(sequences)):
            raise ValueError(
                "recent fault sequence must be ordered"
            )

        if len(set(sequences)) != len(sequences):
            raise ValueError(
                "recent fault sequence must be unique"
            )

        authority = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.read_only,
            self.operator_review_required,
        )

        if not all(authority):
            raise ValueError(
                "runtime diagnostics authority must remain enabled"
            )

        object.__setattr__(
            self,
            "lifecycle_state",
            lifecycle_state,
        )
        object.__setattr__(
            self,
            "host",
            host,
        )
        object.__setattr__(
            self,
            "active_request_count",
            active,
        )
        object.__setattr__(
            self,
            "rejected_request_count",
            rejected,
        )
        object.__setattr__(
            self,
            "fault_count",
            faults,
        )
        object.__setattr__(
            self,
            "recent_faults",
            recent,
        )


class RuntimeFaultLedger:
    def __init__(
        self,
        capacity: int = 32,
    ) -> None:
        if (
            isinstance(capacity, bool)
            or not isinstance(capacity, int)
            or not 1 <= capacity <= 128
        ):
            raise ValueError(
                "capacity must be between 1 and 128"
            )

        self._capacity = capacity
        self._lock = RLock()
        self._records: list[RuntimeFaultRecord] = []
        self._next_sequence = 1
        self._fault_count = 0

    @property
    def capacity(self) -> int:
        return self._capacity

    def record(
        self,
        code: RuntimeFaultCode,
        lifecycle_state: str,
    ) -> RuntimeFaultRecord:
        if not isinstance(code, RuntimeFaultCode):
            raise ValueError(
                "code must be RuntimeFaultCode"
            )

        state = _required_single_line(
            lifecycle_state,
            "lifecycle_state",
        )

        with self._lock:
            record = RuntimeFaultRecord(
                sequence=self._next_sequence,
                code=code,
                lifecycle_state=state,
                message=_FAULT_MESSAGES[code],
            )
            self._next_sequence += 1
            self._fault_count += 1
            self._records.append(record)

            if len(self._records) > self._capacity:
                self._records = self._records[
                    -self._capacity:
                ]

            return record

    def snapshot(
        self,
        *,
        lifecycle_state: str,
        host: str,
        port: int,
        active_request_count: int,
        rejected_request_count: int,
    ) -> RuntimeDiagnosticsSnapshot:
        with self._lock:
            records = tuple(self._records)
            fault_count = self._fault_count

        return RuntimeDiagnosticsSnapshot(
            lifecycle_state=lifecycle_state,
            host=host,
            port=port,
            active_request_count=active_request_count,
            rejected_request_count=rejected_request_count,
            fault_count=fault_count,
            recent_faults=records,
        )
