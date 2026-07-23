from __future__ import annotations

import hashlib
import importlib
import stat
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from apps.fcp_0090_a_share_guojin_qmt_local_terminal_liveness_evidence_app_1.contracts import (
    build_snapshot,
)
from apps.fcp_0090_a_share_guojin_qmt_local_terminal_liveness_evidence_app_1.observer import (
    iter_local_process_image_names,
)

from .contracts import (
    DEFAULT_REGISTRATION,
    LocalCacheProbeEvidence,
    build_probe_evidence,
)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _is_reparse_point(path: Path) -> bool:
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def _load_registered_xtdata(sdk_root: Path):
    root = sdk_root.resolve(strict=True)
    if str(root).startswith("\\\\"):
        raise ValueError("sdk_root must be local")
    if not root.is_dir() or root.is_symlink() or _is_reparse_point(root):
        raise ValueError("sdk_root must be a regular directory")
    package = root / "xtquant"
    native = package / "xtpythonclient.cp311-win_amd64.pyd"
    source = package / "xtdata.py"
    for path in (package, native, source):
        if path.is_symlink() or not path.exists() or _is_reparse_point(path):
            raise ValueError("registered SDK footprint is unavailable")
    if native.stat().st_size != 1147904:
        raise ValueError("registered native module length mismatch")
    if _file_sha256(native) != DEFAULT_REGISTRATION.native_module_sha256:
        raise ValueError("registered native module digest mismatch")
    if _file_sha256(source) != DEFAULT_REGISTRATION.xtdata_source_sha256:
        raise ValueError("registered xtdata source digest mismatch")
    sys.path.insert(0, str(root))
    try:
        module = importlib.import_module("xtquant.xtdata")
    finally:
        if sys.path and sys.path[0] == str(root):
            sys.path.pop(0)
    module_path = Path(module.__file__).resolve(strict=True)
    if module_path != source:
        raise ValueError("xtdata module did not load from the registered root")
    return module


def execute_registered_probe(sdk_root: Path) -> LocalCacheProbeEvidence:
    terminal = build_snapshot(
        iter_local_process_image_names(),
        datetime.now(timezone.utc),
    )
    if terminal.readiness_state != "TERMINAL_OBSERVED":
        return build_probe_evidence(
            terminal,
            lambda: (_ for _ in ()).throw(RuntimeError("probe gate failed")),
        )

    try:
        xtdata = _load_registered_xtdata(sdk_root)
        started = time.monotonic_ns()
        result = xtdata.get_local_data(
            field_list=["time"],
            stock_list=[DEFAULT_REGISTRATION.symbol],
            period=DEFAULT_REGISTRATION.period,
            start_time=DEFAULT_REGISTRATION.start_date,
            end_time=DEFAULT_REGISTRATION.end_date,
            count=DEFAULT_REGISTRATION.count,
            dividend_type=DEFAULT_REGISTRATION.dividend_type,
            fill_data=DEFAULT_REGISTRATION.fill_data,
        )
        elapsed_ms = max(0, (time.monotonic_ns() - started) // 1_000_000)
        return build_probe_evidence(
            terminal,
            lambda: result,
            elapsed_ms=elapsed_ms,
        )
    except Exception:
        return build_probe_evidence(
            terminal,
            lambda: (_ for _ in ()).throw(RuntimeError("probe failed")),
            elapsed_ms=0,
        )
