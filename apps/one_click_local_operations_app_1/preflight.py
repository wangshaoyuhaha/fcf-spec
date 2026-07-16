from __future__ import annotations

import socket
import sys
from typing import Iterable

from apps.browser_product_console_runtime_app_1 import (
    build_browser_console_runtime,
)

from .contracts import LocalOperationsProfile, LocalPreflightReport


def _port_available(port: int) -> bool:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
            handle.bind(("127.0.0.1", port))
    except OSError:
        return False
    return True


def run_local_operations_preflight(
    profile: LocalOperationsProfile,
    *,
    available_model_ids: Iterable[str] = (),
    check_port: bool = True,
) -> LocalPreflightReport:
    notifications = []
    checks = {
        "python_runtime_supported": sys.version_info >= (3, 11),
        "project_root_present": profile.project_root.is_dir(),
        "registered_root_present": profile.allowed_root.is_dir(),
        "registered_index_present": profile.index_path.is_file(),
        "state_root_contained": profile.state_root.is_relative_to(
            profile.project_root
        ),
        "backup_root_contained": profile.backup_root.is_relative_to(
            profile.project_root
        ),
        "port_available": _port_available(profile.port) if check_port else True,
        "registered_artifacts_valid": False,
        "migration_compatible": False,
        "required_models_available": False,
        "database_targets_readable": False,
    }
    correlation_id = "PRECHECK_BLOCKED"
    artifact_count = 0
    try:
        runtime = build_browser_console_runtime(
            allowed_root=profile.allowed_root,
            index_path=profile.index_path,
            port=profile.port,
            title="FCF One-Click Local Operations",
        )
        model = runtime.application.read_model
        correlation_id = model.correlation_id
        artifact_count = len(model.source_artifact_ids)
        checks["registered_artifacts_valid"] = artifact_count > 0
        checks["migration_compatible"] = True
    except (OSError, RuntimeError, ValueError) as exc:
        notifications.append(f"REGISTERED_ARTIFACT_FAILURE: {exc}")
    available = set(available_model_ids)
    missing = tuple(
        model_id
        for model_id in profile.required_model_ids
        if model_id not in available
    )
    checks["required_models_available"] = not missing
    if missing:
        notifications.append("MISSING_MODELS: " + ", ".join(missing))
    elif not profile.required_model_ids:
        notifications.append("MODELS_NOT_REQUIRED: Stage 9 invokes no models")
    unreadable_databases = tuple(
        path for path in profile.database_paths if not path.is_file()
    )
    checks["database_targets_readable"] = not unreadable_databases
    if unreadable_databases:
        notifications.append(
            "DATABASE_TARGET_MISSING: "
            + ", ".join(path.name for path in unreadable_databases)
        )
    if not checks["port_available"]:
        notifications.append(f"PORT_UNAVAILABLE: 127.0.0.1:{profile.port}")
    return LocalPreflightReport(
        status="READY" if all(checks.values()) else "BLOCKED",
        checks=checks,
        correlation_id=correlation_id,
        artifact_count=artifact_count,
        missing_model_ids=missing,
        notifications=tuple(notifications),
    )
