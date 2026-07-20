from __future__ import annotations

import sys
import webbrowser
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.browser_product_console_runtime_app_1 import (  # noqa: E402
    classify_operator_launch_error,
    open_operator_browser,
)
from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (  # noqa: E402
    RegisteredLocalCSVArtifact,
    build_localized_browser_console_runtime,
    inspect_registered_local_csv,
)
from scripts.run_browser_product_console_runtime import (  # noqa: E402
    build_parser as build_base_parser,
    resolve_profile,
)


def build_parser():
    parser = build_base_parser()
    parser.description = (
        "Run the localized FCF read-only browser console on 127.0.0.1."
    )
    parser.add_argument(
        "--language",
        choices=("zh-CN", "en"),
        default="zh-CN",
        help="Presentation language. Source artifacts remain unchanged.",
    )
    parser.add_argument("--local-csv", type=Path)
    parser.add_argument("--local-csv-artifact-id")
    parser.add_argument("--local-csv-source-id")
    parser.add_argument("--local-csv-sha256")
    parser.add_argument("--local-csv-byte-length", type=int)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profile = resolve_profile(args)
        local_values = (
            args.local_csv,
            args.local_csv_artifact_id,
            args.local_csv_source_id,
            args.local_csv_sha256,
            args.local_csv_byte_length,
        )
        if any(value is not None for value in local_values) and not all(
            value is not None for value in local_values
        ):
            raise ValueError("all local CSV registration arguments are required")
        previews = ()
        if args.local_csv is not None:
            registration = RegisteredLocalCSVArtifact(
                artifact_id=args.local_csv_artifact_id,
                source_id=args.local_csv_source_id,
                artifact_sha256=args.local_csv_sha256,
                byte_length=args.local_csv_byte_length,
            )
            previews = (inspect_registered_local_csv(args.local_csv, registration),)
        runtime = build_localized_browser_console_runtime(
            allowed_root=profile.allowed_root,
            index_path=profile.index_path,
            port=profile.port,
            title=profile.title,
            locale_id=args.language,
            local_csv_previews=previews,
        )
        server = runtime.create_server()
    except (FileNotFoundError, OSError, RuntimeError, TypeError, ValueError) as exc:
        code, message, remediation = classify_operator_launch_error(exc)
        print(f"{code.value}: {message}", file=sys.stderr)
        print(f"Guidance: {remediation}", file=sys.stderr)
        return 2

    url = f"http://127.0.0.1:{profile.port}/"
    print(f"FCF localized browser console: {url}", flush=True)
    print("Paper-only / Local loopback / Operator review required", flush=True)
    print(f"Presentation language: {args.language}", flush=True)
    if args.check:
        server.server_close()
        print("Localized startup preflight: PASS", flush=True)
        return 0
    try:
        if profile.open_browser:
            open_operator_browser(url, opener=webbrowser.open)
        server.serve_forever()
    except KeyboardInterrupt:
        print("FCF localized browser console stopped by Operator.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
