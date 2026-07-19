from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
import uuid
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from .contracts import (
    LocalLifecycleState,
    LocalOperationReceipt,
    LocalOperationsProfile,
    LocalRuntimeState,
)
from .preflight import run_local_operations_preflight
from .state_store import LocalOperationsStateStore


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def process_is_alive(pid: int) -> bool:
    if pid < 1:
        return False
    if os.name == "nt":
        import ctypes

        process_query_limited_information = 0x1000
        still_active = 259
        handle = ctypes.windll.kernel32.OpenProcess(
            process_query_limited_information,
            False,
            pid,
        )
        if not handle:
            return False
        try:
            exit_code = ctypes.c_ulong()
            if not ctypes.windll.kernel32.GetExitCodeProcess(
                handle,
                ctypes.byref(exit_code),
            ):
                return False
            return int(exit_code.value) == still_active
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def probe_health(url: str, timeout: float = 1.0) -> bool:
    request = urllib.request.Request(
        url.rstrip("/") + "/health",
        method="GET",
        headers={"Host": url.removeprefix("http://").rstrip("/")},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("ascii"))
    except (OSError, ValueError):
        return False
    return (
        response.status == 200
        and payload.get("status") == "ok"
        and payload.get("host_scope") == "loopback-only"
        and payload.get("mode") == "paper-only"
    )


class OneClickLocalOperationsController:
    def __init__(
        self,
        profile: LocalOperationsProfile,
        *,
        process_launcher: Callable[[LocalOperationsProfile, str], int] | None = None,
        alive_probe: Callable[[int], bool] = process_is_alive,
        health_probe: Callable[[str], bool] = probe_health,
        browser_opener: Callable[[str], object] = webbrowser.open,
        clock: Callable[[], str] = utc_now,
        sleeper: Callable[[float], None] = time.sleep,
    ) -> None:
        self._profile = profile
        self._store = LocalOperationsStateStore(profile.state_root)
        self._process_launcher = process_launcher or self._launch_service_process
        self._alive_probe = alive_probe
        self._health_probe = health_probe
        self._browser_opener = browser_opener
        self._clock = clock
        self._sleeper = sleeper
        self._owned_process: subprocess.Popen[bytes] | None = None

    @property
    def store(self) -> LocalOperationsStateStore:
        return self._store

    def start(
        self,
        *,
        health_timeout_seconds: float = 8.0,
    ) -> LocalOperationReceipt:
        preflight = run_local_operations_preflight(self._profile)
        if preflight.status != "READY":
            return LocalOperationReceipt(
                operation="START",
                status="BLOCKED",
                message="; ".join(preflight.notifications)
                or "Local operations preflight failed.",
            )
        existing = self._safe_read_state()
        if existing is not None and self._alive_probe(existing.pid):
            return LocalOperationReceipt(
                operation="START",
                status="ALREADY_RUNNING",
                message="The owned FCF local service is already running.",
                instance_id=existing.instance_id,
                pid=existing.pid,
                url=existing.url,
            )
        instance_id = uuid.uuid4().hex
        started_at = self._clock()
        try:
            pid = self._process_launcher(self._profile, instance_id)
        except OSError as exc:
            return LocalOperationReceipt(
                operation="START",
                status="BLOCKED",
                message=f"Service launch failed: {exc}",
            )
        state = LocalRuntimeState(
            instance_id=instance_id,
            pid=pid,
            lifecycle_state=LocalLifecycleState.STARTING,
            port=self._profile.port,
            url=self._profile.url,
            started_at_utc=started_at,
            updated_at_utc=started_at,
            correlation_id=preflight.correlation_id,
            artifact_count=preflight.artifact_count,
        )
        self._store.write_state(state)
        deadline = time.monotonic() + health_timeout_seconds
        while time.monotonic() < deadline:
            if not self._alive_probe(pid):
                return self._fail_start(state, "Local service stopped before readiness.")
            if self._health_probe(state.url):
                ready = LocalRuntimeState(
                    **{
                        **state.__dict__,
                        "lifecycle_state": LocalLifecycleState.READY,
                        "updated_at_utc": self._clock(),
                    }
                )
                self._store.write_state(ready)
                opened = True
                if self._profile.open_browser:
                    opened = bool(self._browser_opener(ready.url))
                return LocalOperationReceipt(
                    operation="START",
                    status="READY",
                    message=(
                        "FCF is healthy and the browser was opened."
                        if opened
                        else "FCF is healthy; open the local URL manually."
                    ),
                    instance_id=ready.instance_id,
                    pid=ready.pid,
                    url=ready.url,
                )
            self._sleeper(0.05)
        return self._fail_start(state, "Health readiness timed out.")

    def stop(
        self,
        *,
        stop_timeout_seconds: float = 8.0,
    ) -> LocalOperationReceipt:
        state = self._safe_read_state()
        if state is None:
            return LocalOperationReceipt(
                operation="STOP",
                status="NOT_RUNNING",
                message="No owned FCF local service state exists.",
            )
        if not self._alive_probe(state.pid):
            self._reap_owned_process()
            stopped = self._copy_state(
                state,
                LocalLifecycleState.STOPPED,
            )
            self._store.write_state(stopped)
            return LocalOperationReceipt(
                operation="STOP",
                status="ALREADY_STOPPED",
                message="The recorded FCF local service is not running.",
                instance_id=state.instance_id,
                pid=state.pid,
                url=state.url,
            )
        requested = self._copy_state(
            state,
            LocalLifecycleState.STOP_REQUESTED,
        )
        self._store.write_state(requested)
        self._store.write_stop_request(requested, self._clock())
        deadline = time.monotonic() + stop_timeout_seconds
        while time.monotonic() < deadline:
            observed = self._safe_read_state()
            if (
                observed is not None
                and observed.instance_id == state.instance_id
                and observed.lifecycle_state is LocalLifecycleState.STOPPED
                and not self._alive_probe(state.pid)
            ):
                self._reap_owned_process()
                return LocalOperationReceipt(
                    operation="STOP",
                    status="STOPPED",
                    message="Owned FCF local service stopped gracefully.",
                    instance_id=state.instance_id,
                    pid=state.pid,
                    url=state.url,
                )
            if not self._alive_probe(state.pid):
                self._reap_owned_process()
                stopped = self._copy_state(
                    requested,
                    LocalLifecycleState.STOPPED,
                )
                self._store.write_state(stopped)
                return LocalOperationReceipt(
                    operation="STOP",
                    status="STOPPED",
                    message="Owned FCF local service stopped gracefully.",
                    instance_id=state.instance_id,
                    pid=state.pid,
                    url=state.url,
                )
            self._sleeper(0.05)
        return LocalOperationReceipt(
            operation="STOP",
            status="BLOCKED",
            message=(
                "Graceful stop timed out. No process was force-terminated; "
                "review the service log and instance state."
            ),
            instance_id=state.instance_id,
            pid=state.pid,
            url=state.url,
        )

    def status(self) -> LocalOperationReceipt:
        state = self._safe_read_state()
        if state is None:
            return LocalOperationReceipt(
                operation="STATUS",
                status="NOT_RUNNING",
                message="No local runtime state exists.",
            )
        if state.lifecycle_state is LocalLifecycleState.STOPPED:
            self._reap_owned_process()
            return LocalOperationReceipt(
                operation="STATUS",
                status="STOPPED",
                message="Owned FCF local service is stopped.",
                instance_id=state.instance_id,
                pid=state.pid,
                url=state.url,
            )
        alive = self._alive_probe(state.pid)
        healthy = alive and self._health_probe(state.url)
        if healthy:
            status = "READY"
            message = "Owned FCF local service is healthy."
        elif alive:
            status = "DEGRADED"
            message = "Owned service is running but its health check failed."
        else:
            status = "STOPPED"
            message = "Recorded service process is not running."
            self._reap_owned_process()
        return LocalOperationReceipt(
            operation="STATUS",
            status=status,
            message=message,
            instance_id=state.instance_id,
            pid=state.pid,
            url=state.url,
        )

    def _fail_start(
        self,
        state: LocalRuntimeState,
        message: str,
    ) -> LocalOperationReceipt:
        failed = self._copy_state(state, LocalLifecycleState.FAILED)
        self._store.write_state(failed)
        if self._alive_probe(state.pid):
            self._store.write_stop_request(failed, self._clock())
        return LocalOperationReceipt(
            operation="START",
            status="BLOCKED",
            message=message,
            instance_id=state.instance_id,
            pid=state.pid,
            url=state.url,
        )

    def _copy_state(
        self,
        state: LocalRuntimeState,
        lifecycle: LocalLifecycleState,
    ) -> LocalRuntimeState:
        return LocalRuntimeState(
            **{
                **state.__dict__,
                "lifecycle_state": lifecycle,
                "updated_at_utc": self._clock(),
            }
        )

    def _safe_read_state(self) -> LocalRuntimeState | None:
        try:
            return self._store.read_state()
        except (OSError, ValueError, json.JSONDecodeError):
            return None

    def _launch_service_process(
        self,
        profile: LocalOperationsProfile,
        instance_id: str,
    ) -> int:
        self._store.ensure_root()
        command = (
            sys.executable,
            "-m",
            "apps.one_click_local_operations_app_1.service",
            "--project-root",
            str(profile.project_root),
            "--allowed-root",
            str(profile.allowed_root),
            "--index",
            str(profile.index_path),
            "--state-root",
            str(profile.state_root),
            "--port",
            str(profile.port),
            "--instance-id",
            instance_id,
        )
        creationflags = 0
        start_new_session = os.name != "nt"
        if os.name == "nt":
            creationflags = (
                subprocess.CREATE_NEW_PROCESS_GROUP
                | subprocess.CREATE_NO_WINDOW
            )
        with self._store.log_path.open("ab") as log:
            process = subprocess.Popen(
                command,
                cwd=profile.project_root,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                close_fds=True,
                creationflags=creationflags,
                start_new_session=start_new_session,
            )
        self._owned_process = process
        return int(process.pid)

    def _reap_owned_process(self) -> None:
        process = self._owned_process
        if process is not None and process.poll() is not None:
            self._owned_process = None
