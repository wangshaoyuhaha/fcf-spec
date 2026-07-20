from __future__ import annotations

import json
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
from apps.fcp_0011_candidate_data_source_onboarding_evidence_review_app_1 import (  # noqa: E402
    build_candidate_data_source_onboarding_runtime,
    build_operator_declared_candidate_profiles,
    review_candidate_sources,
)
from scripts.run_browser_product_console_runtime import (  # noqa: E402
    build_parser as build_base_parser,
    resolve_profile,
)


def build_parser():
    parser = build_base_parser()
    parser.description = "Run the FCP-0011 read-only candidate onboarding review."
    parser.add_argument("--language", choices=("zh-CN", "en"), default="zh-CN")
    parser.add_argument("--review-json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    profiles = build_operator_declared_candidate_profiles()
    if args.review_json:
        payload = [dict(packet.as_payload()) for packet in review_candidate_sources(profiles)]
        print(json.dumps(payload, ensure_ascii=True, sort_keys=True))
        return 0
    try:
        profile = resolve_profile(args)
        _, snapshot = build_registered_local_replay_fixture()
        runtime = build_candidate_data_source_onboarding_runtime(
            allowed_root=profile.allowed_root,
            index_path=profile.index_path,
            snapshot=snapshot,
            profiles=profiles,
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
    url = f"http://127.0.0.1:{profile.port}/data-source-onboarding"
    print(f"FCF candidate source onboarding review: {url}", flush=True)
    print("Read-only / No secrets / Operator review", flush=True)
    if args.check:
        server.server_close()
        print("FCP-0011 startup preflight: PASS", flush=True)
        return 0
    try:
        if profile.open_browser:
            open_operator_browser(
                f"http://127.0.0.1:{profile.port}/",
                opener=webbrowser.open,
            )
        server.serve_forever()
    except KeyboardInterrupt:
        print("FCP-0011 console stopped by Operator.", flush=True)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
