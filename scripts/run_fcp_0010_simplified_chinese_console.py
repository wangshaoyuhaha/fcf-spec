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
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (  # noqa: E402
    build_registered_local_replay_fixture,
)
from apps.fcp_0010_simplified_chinese_console_localization_consistency_app_1 import (  # noqa: E402
    build_simplified_chinese_console_runtime,
)
from scripts.run_browser_product_console_runtime import (  # noqa: E402
    build_parser as build_base_parser,
    resolve_profile,
)


def build_parser():
    parser = build_base_parser()
    parser.description = "Run the FCP-0010 read-only localized console."
    parser.add_argument(
        "--language",
        choices=("zh-CN", "en"),
        default="zh-CN",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profile = resolve_profile(args)
        _, snapshot = build_registered_local_replay_fixture()
        runtime = build_simplified_chinese_console_runtime(
            allowed_root=profile.allowed_root,
            index_path=profile.index_path,
            snapshot=snapshot,
            port=profile.port,
            title=profile.title,
            locale_id=args.language,
        )
        server = runtime.create_server()
    except (FileNotFoundError, OSError, RuntimeError, TypeError, ValueError) as exc:
        code, message, remediation = classify_operator_launch_error(exc)
        print(f"{code.value}: {message}", file=sys.stderr)
        print(f"Guidance: {remediation}", file=sys.stderr)
        return 2
    url = f"http://127.0.0.1:{profile.port}/"
    print(f"FCF Simplified Chinese console: {url}", flush=True)
    print("Read-only / Registered evidence / Operator review", flush=True)
    if args.check:
        server.server_close()
        print("FCP-0010 startup preflight: PASS", flush=True)
        return 0
    try:
        if profile.open_browser:
            open_operator_browser(url, opener=webbrowser.open)
        server.serve_forever()
    except KeyboardInterrupt:
        print("FCP-0010 console stopped by Operator.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
