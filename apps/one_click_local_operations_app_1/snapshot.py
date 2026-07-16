from __future__ import annotations

import hashlib
import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from apps.browser_product_console_runtime_app_1 import (
    load_console_artifact_index,
)

from .contracts import LocalOperationsProfile
from .state_store import LocalOperationsStateStore


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True)
class OperationalSnapshotReceipt:
    operation: str
    status: str
    path: str
    archive_sha256: str
    file_count: int
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        if self.automatic_activation_allowed:
            raise ValueError("operational snapshots cannot activate automatically")


class OperationalSnapshotService:
    def create_snapshot(
        self,
        profile: LocalOperationsProfile,
        destination: Path,
        *,
        snapshot_kind: str = "CONFIGURATION_AND_STATE_BACKUP",
    ) -> OperationalSnapshotReceipt:
        loaded = load_console_artifact_index(
            profile.index_path,
            profile.allowed_root,
        )
        files: dict[str, bytes] = {}
        files["registered/index.json"] = profile.index_path.read_bytes()
        for artifact in loaded.artifacts:
            registration = artifact.registration
            source = (profile.allowed_root / registration.relative_path).resolve()
            source.relative_to(profile.allowed_root)
            files[f"registered/{registration.relative_path}"] = source.read_bytes()
        state_store = LocalOperationsStateStore(profile.state_root)
        if state_store.state_path.is_file():
            files["operations/runtime_state.json"] = (
                state_store.state_path.read_bytes()
            )
        for database_path in profile.database_paths:
            files[f"database/{database_path.name}"] = database_path.read_bytes()
        profile_payload = json.dumps(
            {
                "allowed_root_relative": str(
                    profile.allowed_root.relative_to(profile.project_root)
                ).replace("\\", "/"),
                "database_target_count": len(profile.database_paths),
                "index_path_relative": str(
                    profile.index_path.relative_to(profile.project_root)
                ).replace("\\", "/"),
                "port": profile.port,
                "schema_version": "fcf.one_click_local_operations.profile.v1",
            },
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        ).encode("ascii")
        files["operations/profile.json"] = profile_payload
        manifest = {
            "automatic_activation_allowed": False,
            "database_backup_status": (
                "INCLUDED" if profile.database_paths else "NOT_CONFIGURED"
            ),
            "files": {
                name: _sha256(payload)
                for name, payload in sorted(files.items())
            },
            "operator_review_required": True,
            "schema_version": "fcf.one_click_local_operations.snapshot.v1",
            "snapshot_kind": snapshot_kind,
        }
        files["manifest.json"] = json.dumps(
            manifest,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        ).encode("ascii")
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        with zipfile.ZipFile(
            temporary,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            for name, payload in sorted(files.items()):
                archive.writestr(name, payload)
        temporary.replace(destination)
        archive_bytes = destination.read_bytes()
        return OperationalSnapshotReceipt(
            operation="CREATE_SNAPSHOT",
            status="CREATED",
            path=str(destination.resolve()),
            archive_sha256=_sha256(archive_bytes),
            file_count=len(files),
        )

    def stage_recovery(
        self,
        snapshot_path: Path,
        recovery_root: Path,
    ) -> OperationalSnapshotReceipt:
        snapshot_path = Path(snapshot_path).resolve()
        recovery_root = Path(recovery_root).resolve()
        if recovery_root.exists() and any(recovery_root.iterdir()):
            raise ValueError("recovery_root must be absent or empty")
        recovery_root.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(snapshot_path, "r") as archive:
            names = tuple(archive.namelist())
            for name in names:
                candidate = Path(name)
                if candidate.is_absolute() or ".." in candidate.parts:
                    raise ValueError("snapshot contains an unsafe path")
            if "manifest.json" not in names:
                raise ValueError("snapshot manifest is missing")
            manifest = json.loads(archive.read("manifest.json").decode("ascii"))
            if (
                manifest.get("schema_version")
                != "fcf.one_click_local_operations.snapshot.v1"
                or manifest.get("automatic_activation_allowed") is not False
            ):
                raise ValueError("snapshot manifest is incompatible")
            expected_files = manifest.get("files")
            if not isinstance(expected_files, dict):
                raise ValueError("snapshot file manifest is invalid")
            for name, expected_digest in expected_files.items():
                payload = archive.read(name)
                if _sha256(payload) != expected_digest:
                    raise ValueError("snapshot file digest mismatch")
                target = (recovery_root / name).resolve()
                target.relative_to(recovery_root)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(payload)
            (recovery_root / "manifest.json").write_bytes(
                archive.read("manifest.json")
            )
        return OperationalSnapshotReceipt(
            operation="STAGE_RECOVERY",
            status="RESTORED_TO_RECOVERY_STAGING",
            path=str(recovery_root),
            archive_sha256=_sha256(snapshot_path.read_bytes()),
            file_count=len(expected_files) + 1,
        )

    def export_state(
        self,
        profile: LocalOperationsProfile,
        destination: Path,
    ) -> OperationalSnapshotReceipt:
        store = LocalOperationsStateStore(profile.state_root)
        if not store.state_path.is_file():
            raise ValueError("runtime state is not available")
        payload = store.state_path.read_bytes()
        json.loads(payload.decode("ascii"))
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_suffix(destination.suffix + ".tmp")
        temporary.write_bytes(payload)
        temporary.replace(destination)
        return OperationalSnapshotReceipt(
            operation="EXPORT_STATE",
            status="EXPORTED",
            path=str(destination.resolve()),
            archive_sha256=_sha256(payload),
            file_count=1,
        )
