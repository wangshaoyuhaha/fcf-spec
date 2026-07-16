from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Mapping

from .contracts import LocalLifecycleState, LocalRuntimeState


class LocalOperationsStateStore:
    def __init__(self, root: Path) -> None:
        self._root = Path(root)

    @property
    def state_path(self) -> Path:
        return self._root / "runtime_state.json"

    @property
    def log_path(self) -> Path:
        return self._root / "service.log"

    def stop_request_path(self, instance_id: str) -> Path:
        return self._root / f"stop-{instance_id}.json"

    def ensure_root(self) -> None:
        self._root.mkdir(parents=True, exist_ok=True)

    def write_state(self, state: LocalRuntimeState) -> None:
        self.ensure_root()
        payload = asdict(state)
        payload["lifecycle_state"] = state.lifecycle_state.value
        self._atomic_json(self.state_path, payload)

    def read_state(self) -> LocalRuntimeState | None:
        if not self.state_path.exists():
            return None
        payload = json.loads(self.state_path.read_text(encoding="ascii"))
        if not isinstance(payload, dict):
            raise ValueError("runtime state must be a JSON object")
        return LocalRuntimeState(
            instance_id=payload.get("instance_id", ""),
            pid=payload.get("pid", 0),
            lifecycle_state=payload.get("lifecycle_state", ""),
            port=payload.get("port", 0),
            url=payload.get("url", ""),
            started_at_utc=payload.get("started_at_utc", ""),
            updated_at_utc=payload.get("updated_at_utc", ""),
            correlation_id=payload.get("correlation_id", ""),
            artifact_count=payload.get("artifact_count", 0),
            schema_version=payload.get("schema_version", ""),
        )

    def write_stop_request(self, state: LocalRuntimeState, requested_at: str) -> Path:
        path = self.stop_request_path(state.instance_id)
        self._atomic_json(
            path,
            {
                "instance_id": state.instance_id,
                "pid": state.pid,
                "requested_at_utc": requested_at,
                "schema_version": "fcf.one_click_local_operations.stop.v1",
            },
        )
        return path

    def read_stop_request(self, instance_id: str) -> Mapping[str, object] | None:
        path = self.stop_request_path(instance_id)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="ascii"))
        if not isinstance(payload, dict) or payload.get("instance_id") != instance_id:
            raise ValueError("stop request ownership mismatch")
        return payload

    @staticmethod
    def _atomic_json(path: Path, payload: Mapping[str, object]) -> None:
        encoded = json.dumps(
            dict(payload),
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(encoded + "\n", encoding="ascii", newline="\n")
        temporary.replace(path)
