from __future__ import annotations

import hashlib
import json
import os
import stat
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .contracts import (
    REQUIRED_CACHE_FAMILIES,
    REQUIRED_DIRECTORY_CLASSES,
    RuntimeFootprintSnapshot,
)


_DIRECTORY_CLASS_BY_NAME = {
    "datadir": "DATADIR",
    "datas": "DATAS",
    "dumps": "DUMPS",
    "log": "LOG",
    "quoter": "QUOTER",
    "users": "USERS",
}
_CACHE_FAMILY_BY_NAME = {
    "miniqmtShmStockListCacheSH": "STOCK_LIST_SH",
    "miniqmtShmStockListCacheSZ": "STOCK_LIST_SZ",
    "miniqmtShmTradeDateListCache": "TRADE_DATE_LIST",
}
_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def _is_reparse(stat_result: os.stat_result) -> bool:
    return bool(getattr(stat_result, "st_file_attributes", 0) & _REPARSE_POINT)


def _canonical_utc(mtime_ns: int) -> str:
    seconds, nanoseconds = divmod(mtime_ns, 1_000_000_000)
    value = datetime.fromtimestamp(seconds, timezone.utc) + timedelta(
        microseconds=nanoseconds // 1000
    )
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def scan_top_level_metadata(
    directory: Path,
    *,
    max_top_level_entries: int,
) -> RuntimeFootprintSnapshot:
    root = Path(directory)
    root_stat = root.lstat()
    if root.is_symlink() or _is_reparse(root_stat):
        raise ValueError("runtime footprint root must not be a link or reparse point")
    if not root.is_dir():
        raise ValueError("runtime footprint root must be a directory")

    with os.scandir(root) as iterator:
        entries = sorted(iterator, key=lambda item: item.name.casefold())
    if len(entries) > max_top_level_entries:
        raise ValueError("runtime footprint exceeds the top-level entry limit")

    directory_count = 0
    regular_file_count = 0
    aggregate_bytes = 0
    latest_mtime_ns = 0
    directories_present: set[str] = set()
    cache_families_present: set[str] = set()
    manifest: list[dict[str, object]] = []

    for entry in entries:
        entry_stat = entry.stat(follow_symlinks=False)
        if entry.is_symlink() or _is_reparse(entry_stat):
            raise ValueError("runtime footprint entries must not be links or reparse points")
        if stat.S_ISDIR(entry_stat.st_mode):
            kind = "DIRECTORY"
            byte_length = 0
            directory_count += 1
            registered_class = _DIRECTORY_CLASS_BY_NAME.get(entry.name)
            if registered_class is not None:
                directories_present.add(registered_class)
        elif stat.S_ISREG(entry_stat.st_mode):
            kind = "REGULAR_FILE"
            byte_length = int(entry_stat.st_size)
            regular_file_count += 1
            aggregate_bytes += byte_length
            registered_family = _CACHE_FAMILY_BY_NAME.get(entry.name)
            if registered_family is not None:
                cache_families_present.add(registered_family)
        else:
            raise ValueError("runtime footprint contains an unsupported entry kind")
        latest_mtime_ns = max(latest_mtime_ns, int(entry_stat.st_mtime_ns))
        manifest.append(
            {
                "byte_length": byte_length,
                "kind": kind,
                "name_sha256": hashlib.sha256(entry.name.encode("utf-8")).hexdigest(),
                "write_time_ns": int(entry_stat.st_mtime_ns),
            }
        )

    if not entries:
        latest_mtime_ns = int(root_stat.st_mtime_ns)
    manifest_sha256 = hashlib.sha256(
        json.dumps(
            manifest,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("ascii")
    ).hexdigest()
    directories_missing = tuple(
        sorted(set(REQUIRED_DIRECTORY_CLASSES) - directories_present)
    )
    caches_missing = tuple(
        sorted(set(REQUIRED_CACHE_FAMILIES) - cache_families_present)
    )
    return RuntimeFootprintSnapshot(
        top_level_entry_count=len(entries),
        directory_count=directory_count,
        regular_file_count=regular_file_count,
        aggregate_regular_file_bytes=aggregate_bytes,
        latest_metadata_time_utc=_canonical_utc(latest_mtime_ns),
        required_directories_present=tuple(sorted(directories_present)),
        required_directories_missing=directories_missing,
        required_cache_families_present=tuple(sorted(cache_families_present)),
        required_cache_families_missing=caches_missing,
        manifest_sha256=manifest_sha256,
    )
