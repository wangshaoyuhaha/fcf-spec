from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from .controller import OneClickLocalOperationsController
from .contracts import LocalOperationsProfile
from .preflight import run_local_operations_preflight
from .snapshot import OperationalSnapshotService


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def default_profile() -> LocalOperationsProfile:
    return LocalOperationsProfile(
        project_root=PROJECT_ROOT,
        allowed_root=PROJECT_ROOT / "examples" / "browser_product_console_starter",
        index_path=(
            PROJECT_ROOT
            / "examples"
            / "browser_product_console_starter"
            / "index.json"
        ),
        state_root=PROJECT_ROOT / "runtime" / "one_click_local_operations",
        backup_root=(
            PROJECT_ROOT
            / "runtime"
            / "one_click_local_operations"
            / "backups"
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FCF one-click local operations")
    parser.add_argument(
        "command",
        choices=("start", "stop", "status", "check", "backup", "snapshot", "restore", "export"),
    )
    parser.add_argument("--path", type=Path)
    return parser


def _print(payload: object) -> None:
    print(
        json.dumps(
            payload,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
    )


def _default_archive(profile: LocalOperationsProfile, prefix: str) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return profile.backup_root / f"{prefix}-{stamp}.zip"


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    profile = default_profile()
    controller = OneClickLocalOperationsController(profile)
    snapshots = OperationalSnapshotService()
    try:
        if args.command == "start":
            receipt = controller.start()
            _print(asdict(receipt))
            return 0 if receipt.status in {"READY", "ALREADY_RUNNING"} else 2
        if args.command == "stop":
            receipt = controller.stop()
            _print(asdict(receipt))
            return 0 if receipt.status in {
                "STOPPED",
                "ALREADY_STOPPED",
                "NOT_RUNNING",
            } else 2
        if args.command == "status":
            receipt = controller.status()
            _print(asdict(receipt))
            return 0 if receipt.status in {"READY", "STOPPED", "NOT_RUNNING"} else 2
        if args.command == "check":
            report = run_local_operations_preflight(profile)
            payload = {
                "status": report.status,
                "checks": dict(report.checks),
                "correlation_id": report.correlation_id,
                "artifact_count": report.artifact_count,
                "missing_model_ids": report.missing_model_ids,
                "notifications": report.notifications,
            }
            _print(payload)
            return 0 if report.status == "READY" else 2
        if args.command in {"backup", "snapshot"}:
            destination = args.path or _default_archive(
                profile,
                "backup" if args.command == "backup" else "upgrade-snapshot",
            )
            receipt = snapshots.create_snapshot(
                profile,
                destination,
                snapshot_kind=(
                    "CONFIGURATION_AND_STATE_BACKUP"
                    if args.command == "backup"
                    else "PRE_UPGRADE_SNAPSHOT"
                ),
            )
            _print(asdict(receipt))
            return 0
        if args.command == "restore":
            if args.path is None:
                raise ValueError("--path must identify the snapshot to restore")
            recovery = (
                profile.state_root
                / "recovery"
                / args.path.stem
            )
            receipt = snapshots.stage_recovery(args.path, recovery)
            _print(asdict(receipt))
            return 0
        if args.command == "export":
            destination = args.path or (
                profile.backup_root / "runtime-state-export.json"
            )
            receipt = snapshots.export_state(profile, destination)
            _print(asdict(receipt))
            return 0
    except (OSError, RuntimeError, ValueError) as exc:
        _print({"status": "BLOCKED", "message": str(exc)})
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
