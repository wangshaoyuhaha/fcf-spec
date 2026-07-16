from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path
from threading import Thread
from typing import Sequence

from apps.browser_product_console_runtime_app_1 import (
    build_browser_console_runtime,
)
from apps.fcf_web_console_app_1 import (
    FCFWebConsoleApplication,
    FCFWebConsoleServerConfig,
    WebConsoleSnapshot,
    create_fcf_web_console_server,
)

from .contracts import LocalLifecycleState, LocalRuntimeState
from .controller import utc_now
from .state_store import LocalOperationsStateStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Internal FCF local service")
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--allowed-root", type=Path, required=True)
    parser.add_argument("--index", type=Path, required=True)
    parser.add_argument("--state-root", type=Path, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--instance-id", required=True)
    return parser


def run_service(args: argparse.Namespace) -> int:
    store = LocalOperationsStateStore(args.state_root)
    runtime = build_browser_console_runtime(
        allowed_root=args.allowed_root,
        index_path=args.index,
        port=args.port,
        title="FCF One-Click Local Operations",
    )
    snapshot = WebConsoleSnapshot.from_console_read_model(
        runtime.application.read_model
    )
    application = FCFWebConsoleApplication(snapshot)
    server = create_fcf_web_console_server(
        FCFWebConsoleServerConfig(port=args.port),
        application,
    )

    def watch_stop_request() -> None:
        while True:
            try:
                request = store.read_stop_request(args.instance_id)
            except (OSError, ValueError):
                request = None
            if request is not None and int(request.get("pid", 0)) == os.getpid():
                server.shutdown()
                return
            time.sleep(0.1)

    watcher = Thread(target=watch_stop_request, daemon=True)
    watcher.start()
    try:
        server.serve_forever()
    finally:
        server.server_close()
        state = store.read_state()
        if state is not None and state.instance_id == args.instance_id:
            store.write_state(
                LocalRuntimeState(
                    **{
                        **state.__dict__,
                        "lifecycle_state": LocalLifecycleState.STOPPED,
                        "updated_at_utc": utc_now(),
                    }
                )
            )
        store.stop_request_path(args.instance_id).unlink(missing_ok=True)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return run_service(args)
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"FCF local service failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
