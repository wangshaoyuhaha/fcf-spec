from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from typing import Any

from scripts.fcf_pytest_scratch import is_within
from scripts.fcf_pytest_scratch import verify_writable_parent
from scripts.fcf_pytest_scratch import windows_pytest_scratch_parent


PROJECT_ROOT = Path(__file__).resolve().parent


def pytest_configure(config: Any) -> None:
    if os.name != "nt" or config.option.basetemp is not None:
        return
    parent = windows_pytest_scratch_parent(PROJECT_ROOT)
    verify_writable_parent(parent)
    base_temp = parent / f"pytest-{os.getpid()}-{uuid.uuid4().hex}"
    config.option.basetemp = str(base_temp)
    config._fcf_windows_basetemp = base_temp


def pytest_unconfigure(config: Any) -> None:
    base_temp = getattr(config, "_fcf_windows_basetemp", None)
    if base_temp is None or not base_temp.exists():
        return
    parent = windows_pytest_scratch_parent(PROJECT_ROOT)
    resolved = base_temp.resolve()
    if resolved.parent != parent or not is_within(resolved, parent):
        raise RuntimeError("refusing to remove an unexpected pytest scratch path")
    shutil.rmtree(resolved)
