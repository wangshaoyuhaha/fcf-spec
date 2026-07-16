from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping, Tuple


_INSTANCE_PATTERN = re.compile(r"^[a-f0-9]{32}$")


def require_text(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


class LocalLifecycleState(str, Enum):
    STARTING = "STARTING"
    READY = "READY"
    STOP_REQUESTED = "STOP_REQUESTED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class LocalOperationsProfile:
    project_root: Path
    allowed_root: Path
    index_path: Path
    state_root: Path
    backup_root: Path
    port: int = 8775
    open_browser: bool = True
    required_model_ids: Tuple[str, ...] = ()
    database_paths: Tuple[Path, ...] = ()

    def __post_init__(self) -> None:
        project_root = Path(self.project_root).resolve()
        allowed_root = Path(self.allowed_root).resolve()
        index_path = Path(self.index_path).resolve()
        state_root = Path(self.state_root).resolve()
        backup_root = Path(self.backup_root).resolve()
        if isinstance(self.port, bool) or not 1024 <= int(self.port) <= 65535:
            raise ValueError("port must be between 1024 and 65535")
        for name, path in (
            ("allowed_root", allowed_root),
            ("index_path", index_path),
            ("state_root", state_root),
            ("backup_root", backup_root),
        ):
            try:
                path.relative_to(project_root)
            except ValueError as exc:
                raise ValueError(f"{name} must remain inside project_root") from exc
        model_ids = tuple(
            require_text(value, "required_model_id")
            for value in self.required_model_ids
        )
        if len(set(model_ids)) != len(model_ids):
            raise ValueError("required_model_ids must be unique")
        databases = tuple(Path(path).resolve() for path in self.database_paths)
        for path in databases:
            try:
                path.relative_to(project_root)
            except ValueError as exc:
                raise ValueError(
                    "database_paths must remain inside project_root"
                ) from exc
        object.__setattr__(self, "project_root", project_root)
        object.__setattr__(self, "allowed_root", allowed_root)
        object.__setattr__(self, "index_path", index_path)
        object.__setattr__(self, "state_root", state_root)
        object.__setattr__(self, "backup_root", backup_root)
        object.__setattr__(self, "port", int(self.port))
        object.__setattr__(self, "required_model_ids", model_ids)
        object.__setattr__(self, "database_paths", databases)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.port}/"


@dataclass(frozen=True)
class LocalRuntimeState:
    instance_id: str
    pid: int
    lifecycle_state: LocalLifecycleState
    port: int
    url: str
    started_at_utc: str
    updated_at_utc: str
    correlation_id: str
    artifact_count: int
    schema_version: str = "fcf.one_click_local_operations.state.v1"

    def __post_init__(self) -> None:
        if not _INSTANCE_PATTERN.fullmatch(self.instance_id):
            raise ValueError("instance_id must be a 32-character lowercase hex id")
        if isinstance(self.pid, bool) or int(self.pid) < 1:
            raise ValueError("pid must be positive")
        state = (
            self.lifecycle_state
            if isinstance(self.lifecycle_state, LocalLifecycleState)
            else LocalLifecycleState(self.lifecycle_state)
        )
        if not 1024 <= int(self.port) <= 65535:
            raise ValueError("state port is invalid")
        expected_url = f"http://127.0.0.1:{int(self.port)}/"
        if self.url != expected_url:
            raise ValueError("state URL must remain exact loopback")
        if self.artifact_count < 1:
            raise ValueError("runtime state requires registered artifacts")
        for field_name in (
            "started_at_utc",
            "updated_at_utc",
            "correlation_id",
        ):
            require_text(getattr(self, field_name), field_name)
        object.__setattr__(self, "lifecycle_state", state)
        object.__setattr__(self, "pid", int(self.pid))
        object.__setattr__(self, "port", int(self.port))


@dataclass(frozen=True)
class LocalPreflightReport:
    status: str
    checks: Mapping[str, bool]
    correlation_id: str
    artifact_count: int
    missing_model_ids: Tuple[str, ...]
    notifications: Tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in {"READY", "BLOCKED"}:
            raise ValueError("invalid preflight status")
        checks = MappingProxyType(dict(sorted(self.checks.items())))
        if self.status == "READY" and (not checks or not all(checks.values())):
            raise ValueError("ready preflight requires every check")
        if self.status == "BLOCKED" and all(checks.values()):
            raise ValueError("blocked preflight requires a failed check")
        object.__setattr__(self, "checks", checks)
        object.__setattr__(self, "missing_model_ids", tuple(self.missing_model_ids))
        object.__setattr__(self, "notifications", tuple(self.notifications))


@dataclass(frozen=True)
class LocalOperationReceipt:
    operation: str
    status: str
    message: str
    instance_id: str = ""
    pid: int = 0
    url: str = ""
    automatic_authority_transition: bool = False
    financial_execution_performed: bool = False
    unrelated_process_terminated: bool = False

    def __post_init__(self) -> None:
        require_text(self.operation, "operation")
        require_text(self.status, "status")
        require_text(self.message, "message")
        if (
            self.automatic_authority_transition
            or self.financial_execution_performed
            or self.unrelated_process_terminated
        ):
            raise ValueError("local operations cannot change financial authority")
