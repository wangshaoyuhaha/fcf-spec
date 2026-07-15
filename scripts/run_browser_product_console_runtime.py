from __future__ import annotations

import argparse
import sys
import webbrowser
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.browser_product_console_runtime_app_1 import (  # noqa: E402
    OPERATOR_LAUNCH_DEFAULT_TITLE,
    STARTER_DATA_CLASSIFICATION,
    OperatorLaunchProfile,
    build_default_operator_launch_profile,
    open_operator_browser,
    prepare_operator_launch,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run the FCF paper-only browser product console on 127.0.0.1."
        )
    )
    parser.add_argument(
        "--allowed-root",
        type=Path,
        help=(
            "Custom local registered-artifact root. Omit with --index to "
            "use the demonstrative starter package."
        ),
    )
    parser.add_argument(
        "--index",
        type=Path,
        help=(
            "Custom registered browser console artifact index. Omit with "
            "--allowed-root to use the demonstrative starter package."
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Loopback port between 1024 and 65535.",
    )
    parser.add_argument(
        "--title",
        help="Local browser page title.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Start the console without opening the default browser.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate startup and registered artifacts without serving.",
    )
    return parser


def resolve_profile(args: argparse.Namespace) -> OperatorLaunchProfile:
    if (args.allowed_root is None) != (args.index is None):
        raise ValueError("--allowed-root and --index must be provided together")

    if args.allowed_root is None:
        profile = build_default_operator_launch_profile(
            project_root=ROOT,
            port=args.port,
            open_browser=not args.no_browser,
        )
        if args.title:
            profile = OperatorLaunchProfile(
                allowed_root=profile.allowed_root,
                index_path=profile.index_path,
                port=profile.port,
                title=args.title,
                open_browser=profile.open_browser,
            )
        return profile

    root = args.allowed_root
    index = args.index
    if not index.is_absolute():
        index = root / index
    return OperatorLaunchProfile(
        allowed_root=root,
        index_path=index,
        port=args.port,
        title=args.title or "FCF Browser Product Console",
        open_browser=not args.no_browser,
        data_classification="REGISTERED_EVIDENCE",
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profile = resolve_profile(args)
        session = prepare_operator_launch(profile)
    except (OSError, ValueError) as exc:
        print(f"FCF console startup rejected: {exc}", file=sys.stderr)
        return 2

    print(
        f"FCF browser console: {session.url}",
        flush=True,
    )
    print(
        "Paper-only / Local loopback / Operator review required",
        flush=True,
    )
    print(
        f"Data classification: {profile.data_classification}",
        flush=True,
    )
    print(f"Registered artifacts: {session.artifact_count}", flush=True)

    if args.check:
        print("Startup preflight: PASS", flush=True)
        return 0

    try:
        server = session.create_server()
    except (OSError, ValueError) as exc:
        print(f"FCF console server rejected: {exc}", file=sys.stderr)
        return 2

    try:
        if profile.open_browser:
            open_operator_browser(session.url, opener=webbrowser.open)
        server.serve_forever()
    except KeyboardInterrupt:
        print("FCF browser console stopped by Operator.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
