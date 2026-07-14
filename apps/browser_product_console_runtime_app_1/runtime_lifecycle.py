from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from enum import Enum
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import BoundedSemaphore, RLock
from typing import Sequence, Type

from .runtime_diagnostics import (
    RuntimeDiagnosticsSnapshot,
    RuntimeFaultCode,
    RuntimeFaultLedger,
)
from .runtime_hardening import (
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS,
    RuntimeHardeningLimits,
)


_EXACT_BIND_HOST = "127.0.0.1"
_ALLOWED_HOST_NAMES = frozenset(
    {
        "127.0.0.1",
        "localhost",
    }
)


def _validated_port(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("port must be an integer")
    if not 1024 <= value <= 65535:
        raise ValueError(
            "port must be between 1024 and 65535"
        )
    return value


def _validated_bind_host(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("bind host must be text")
    if value != _EXACT_BIND_HOST:
        raise ValueError(
            "bind host must remain exactly 127.0.0.1"
        )
    return value


def normalize_loopback_host_authority(
    value: object,
    expected_port: int,
) -> str:
    port = _validated_port(expected_port)

    if not isinstance(value, str):
        raise ValueError("Host header must be text")

    authority = value.strip()

    if not authority or authority != value:
        raise ValueError(
            "Host header must not contain outer whitespace"
        )

    if any(character.isspace() for character in authority):
        raise ValueError(
            "Host header must not contain whitespace"
        )

    if any(
        character in authority
        for character in (
            ",",
            "/",
            "\\",
            "@",
            "?",
            "#",
        )
    ):
        raise ValueError(
            "Host header contains prohibited syntax"
        )

    if authority.startswith("[") or authority.endswith("]"):
        raise ValueError(
            "IPv6 Host authority is not permitted"
        )

    if authority.count(":") > 1:
        raise ValueError(
            "Host header contains invalid port syntax"
        )

    if ":" in authority:
        host_text, port_text = authority.rsplit(":", 1)

        if not port_text.isdigit():
            raise ValueError(
                "Host header port must be numeric"
            )

        if int(port_text) != port:
            raise ValueError(
                "Host header port does not match runtime port"
            )
    else:
        host_text = authority

    normalized_host = host_text.lower()

    if normalized_host not in _ALLOWED_HOST_NAMES:
        try:
            address = ipaddress.ip_address(
                normalized_host
            )
        except ValueError as exc:
            raise ValueError(
                "Host header is not loopback"
            ) from exc

        if (
            address.version != 4
            or str(address) != _EXACT_BIND_HOST
        ):
            raise ValueError(
                "Host header is not exact loopback"
            )

        normalized_host = _EXACT_BIND_HOST

    return f"{normalized_host}:{port}"


def host_header_is_valid(
    values: Sequence[str],
    expected_port: int,
) -> bool:
    if isinstance(values, (str, bytes)):
        return False

    normalized_values = tuple(values)

    if len(normalized_values) != 1:
        return False

    try:
        normalize_loopback_host_authority(
            normalized_values[0],
            expected_port,
        )
    except ValueError:
        return False

    return True


class RuntimeLifecycleState(str, Enum):
    CREATED = "CREATED"
    READY = "READY"
    SERVING = "SERVING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    CLOSED = "CLOSED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class RuntimeLifecycleSnapshot:
    state: RuntimeLifecycleState
    host: str
    port: int

    def __post_init__(self) -> None:
        if not isinstance(
            self.state,
            RuntimeLifecycleState,
        ):
            raise ValueError(
                "state must be RuntimeLifecycleState"
            )

        object.__setattr__(
            self,
            "host",
            _validated_bind_host(self.host),
        )
        object.__setattr__(
            self,
            "port",
            _validated_port(self.port),
        )


class HardenedLoopbackHTTPServer(
    ThreadingHTTPServer
):
    allow_reuse_address = False
    daemon_threads = True
    block_on_close = True

    def __init__(
        self,
        server_address: tuple[str, int],
        handler_class: Type[BaseHTTPRequestHandler],
        *,
        limits: RuntimeHardeningLimits = (
            BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
        ),
    ) -> None:
        host, port = server_address

        validated_host = _validated_bind_host(host)
        validated_port = _validated_port(port)

        if not isinstance(limits, RuntimeHardeningLimits):
            raise ValueError("limits must be RuntimeHardeningLimits")

        self._limits = limits
        self._request_slots = BoundedSemaphore(
            limits.max_concurrent_requests
        )
        self._resource_lock = RLock()
        self._active_request_count = 0
        self._rejected_request_count = 0
        self._fault_ledger = RuntimeFaultLedger(
            capacity=32
        )

        self._lifecycle_lock = RLock()
        self._lifecycle_state = (
            RuntimeLifecycleState.CREATED
        )

        try:
            super().__init__(
                (
                    validated_host,
                    validated_port,
                ),
                handler_class,
                bind_and_activate=True,
            )
        except OSError:
            self._set_lifecycle_state(
                RuntimeLifecycleState.FAILED
            )
            raise

        actual_host = str(self.server_address[0])
        actual_port = int(self.server_address[1])

        if (
            actual_host != validated_host
            or actual_port != validated_port
        ):
            super().server_close()
            self._set_lifecycle_state(
                RuntimeLifecycleState.FAILED
            )
            raise RuntimeError(
                "runtime server bound to unexpected address"
            )

        self._set_lifecycle_state(
            RuntimeLifecycleState.READY
        )

    @property
    def socket_timeout_seconds(self) -> float:
        return self._limits.socket_timeout_seconds

    @property
    def max_concurrent_requests(self) -> int:
        return self._limits.max_concurrent_requests

    @property
    def active_request_count(self) -> int:
        with self._resource_lock:
            return self._active_request_count

    @property
    def rejected_request_count(self) -> int:
        with self._resource_lock:
            return self._rejected_request_count

    def record_runtime_fault(
        self,
        code: RuntimeFaultCode,
    ):
        return self._fault_ledger.record(
            code,
            self.lifecycle_state.value,
        )

    def diagnostics_snapshot(
        self,
    ) -> RuntimeDiagnosticsSnapshot:
        with self._resource_lock:
            active_request_count = (
                self._active_request_count
            )
            rejected_request_count = (
                self._rejected_request_count
            )

        return self._fault_ledger.snapshot(
            lifecycle_state=self.lifecycle_state.value,
            host=str(self.server_address[0]),
            port=int(self.server_address[1]),
            active_request_count=active_request_count,
            rejected_request_count=rejected_request_count,
        )

    def get_request(self):
        request, client_address = super().get_request()
        request.settimeout(self._limits.socket_timeout_seconds)
        return request, client_address

    @staticmethod
    def _send_capacity_rejection(request) -> None:
        response = (
            b"HTTP/1.1 503 Service Unavailable\r\n"
            b"Content-Type: text/plain; charset=utf-8\r\n"
            b"Content-Length: 19\r\n"
            b"Cache-Control: no-store\r\n"
            b"X-Content-Type-Options: nosniff\r\n"
            b"Content-Security-Policy: "
            b"default-src 'self'; style-src 'unsafe-inline'\r\n"
            b"Connection: close\r\n"
            b"\r\n"
            b"Service Unavailable"
        )
        try:
            request.sendall(response)
        except OSError:
            return

    def process_request(self, request, client_address) -> None:
        acquired = self._request_slots.acquire(blocking=False)

        if not acquired:
            with self._resource_lock:
                self._rejected_request_count += 1
            self.record_runtime_fault(
                RuntimeFaultCode.CAPACITY_REJECTED
            )
            self._send_capacity_rejection(request)
            self.shutdown_request(request)
            return

        with self._resource_lock:
            self._active_request_count += 1

        try:
            super().process_request(request, client_address)
        except BaseException:
            with self._resource_lock:
                self._active_request_count -= 1
            self._request_slots.release()
            raise

    def process_request_thread(self, request, client_address) -> None:
        try:
            super().process_request_thread(request, client_address)
        finally:
            with self._resource_lock:
                self._active_request_count -= 1
            self._request_slots.release()

    def handle_error(
        self,
        request,
        client_address,
    ) -> None:
        self.record_runtime_fault(
            RuntimeFaultCode.REQUEST_HANDLER_FAILURE
        )

    def _set_lifecycle_state(
        self,
        state: RuntimeLifecycleState,
    ) -> None:
        with self._lifecycle_lock:
            self._lifecycle_state = state

    @property
    def lifecycle_state(
        self,
    ) -> RuntimeLifecycleState:
        with self._lifecycle_lock:
            return self._lifecycle_state

    def lifecycle_snapshot(
        self,
    ) -> RuntimeLifecycleSnapshot:
        return RuntimeLifecycleSnapshot(
            state=self.lifecycle_state,
            host=str(self.server_address[0]),
            port=int(self.server_address[1]),
        )

    def serve_forever(
        self,
        poll_interval: float = 0.05,
    ) -> None:
        with self._lifecycle_lock:
            if self._lifecycle_state not in {
                RuntimeLifecycleState.READY,
                RuntimeLifecycleState.STOPPED,
            }:
                raise RuntimeError(
                    "runtime server is not ready to serve"
                )

            self._lifecycle_state = (
                RuntimeLifecycleState.SERVING
            )

        try:
            super().serve_forever(
                poll_interval=poll_interval
            )
        except BaseException:
            self._set_lifecycle_state(
                RuntimeLifecycleState.FAILED
            )
            self.record_runtime_fault(
                RuntimeFaultCode.SERVER_LOOP_FAILURE
            )
            raise
        finally:
            with self._lifecycle_lock:
                if self._lifecycle_state not in {
                    RuntimeLifecycleState.CLOSED,
                    RuntimeLifecycleState.FAILED,
                }:
                    self._lifecycle_state = (
                        RuntimeLifecycleState.STOPPED
                    )

    def shutdown(self) -> None:
        with self._lifecycle_lock:
            if (
                self._lifecycle_state
                is RuntimeLifecycleState.CLOSED
            ):
                return

            if (
                self._lifecycle_state
                is not RuntimeLifecycleState.SERVING
            ):
                self.record_runtime_fault(
                    RuntimeFaultCode.SHUTDOWN_FAILURE
                )
                raise RuntimeError(
                    "runtime server is not serving"
                )

            self._lifecycle_state = (
                RuntimeLifecycleState.STOPPING
            )

        super().shutdown()

    def server_close(self) -> None:
        try:
            super().server_close()
        except BaseException:
            self.record_runtime_fault(
                RuntimeFaultCode.SHUTDOWN_FAILURE
            )
            raise
        finally:
            self._set_lifecycle_state(
                RuntimeLifecycleState.CLOSED
            )


def create_hardened_loopback_server(
    host: str,
    port: int,
    handler_class: Type[BaseHTTPRequestHandler],
    *,
    limits: RuntimeHardeningLimits = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
    ),
) -> HardenedLoopbackHTTPServer:
    validated_host = _validated_bind_host(host)
    validated_port = _validated_port(port)

    try:
        return HardenedLoopbackHTTPServer(
            (
                validated_host,
                validated_port,
            ),
            handler_class,
            limits=limits,
        )
    except OSError as exc:
        raise RuntimeError(
            "console loopback port is unavailable"
        ) from exc
