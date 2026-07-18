from __future__ import annotations

import os
import uuid
from pathlib import Path


FCF_PYTEST_ROOT_NAME = "FCF-pytest-scratch-v2"


def is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def windows_pytest_scratch_parent(project_root: Path) -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        raise RuntimeError("LOCALAPPDATA is required for Windows pytest scratch")
    parent = (Path(local_app_data) / FCF_PYTEST_ROOT_NAME).resolve()
    if is_within(parent, project_root.resolve()):
        raise RuntimeError("Windows pytest scratch must remain outside the repository")
    return parent


def verify_writable_parent(parent: Path) -> None:
    parent.mkdir(parents=True, exist_ok=True)
    probe = parent / f"fcf-write-probe-{uuid.uuid4().hex}"
    probe.mkdir(exist_ok=False)
    probe.rmdir()
