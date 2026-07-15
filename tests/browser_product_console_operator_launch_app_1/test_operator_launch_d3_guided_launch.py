from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    GUIDED_LAUNCH_STAGE_ID,
    build_default_operator_launch_profile,
    open_operator_browser,
    prepare_operator_launch,
)
from scripts.run_browser_product_console_runtime import (
    build_parser,
    main,
    resolve_profile,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_d3_no_argument_profile_uses_registered_starter_package() -> None:
    args = build_parser().parse_args([])
    profile = resolve_profile(args)

    assert GUIDED_LAUNCH_STAGE_ID == "D3"
    assert profile == build_default_operator_launch_profile(
        project_root=PROJECT_ROOT
    )


def test_d3_prepared_session_renders_a_share_us_and_btc() -> None:
    profile = build_default_operator_launch_profile(project_root=PROJECT_ROOT)
    session = prepare_operator_launch(profile)

    response = session.runtime.application.dispatch("GET", "/stocks")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert "DEMO-600000" in body
    assert "DEMO-AAPL" in body
    assert "DEMO-BTC-USD" in body
    assert session.artifact_count == 14


def test_d3_browser_open_is_exact_loopback_and_explicit() -> None:
    opened: list[str] = []

    result = open_operator_browser(
        "http://127.0.0.1:8765/",
        opener=lambda url: opened.append(url) or True,
    )

    assert result is True
    assert opened == ["http://127.0.0.1:8765/"]


@pytest.mark.parametrize(
    "url",
    (
        "https://127.0.0.1:8765/",
        "http://localhost:8765/",
        "http://0.0.0.0:8765/",
        "http://127.0.0.1:8765/path",
        "http://127.0.0.1:8765/?remote=true",
    ),
)
def test_d3_browser_open_rejects_noncanonical_url(url: str) -> None:
    with pytest.raises(ValueError, match="loopback"):
        open_operator_browser(url, opener=lambda _: True)


def test_d3_check_mode_is_nonblocking_and_does_not_open_browser(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["--check"]) == 0
    output = capsys.readouterr()
    assert "Startup preflight: PASS" in output.out
    assert "DEMONSTRATION_ONLY" in output.out
    assert output.err == ""


def test_d3_custom_root_and_index_must_be_paired(tmp_path: Path) -> None:
    args = build_parser().parse_args(["--allowed-root", str(tmp_path)])

    with pytest.raises(ValueError, match="provided together"):
        resolve_profile(args)
