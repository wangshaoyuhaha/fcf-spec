import threading
import urllib.request
from pathlib import Path

from apps.browser_product_console_runtime_app_1 import (
    EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY,
    PRODUCT_ACCEPTANCE_STAGE_ID,
    RESEARCH_WORKSPACE_ROUTE_REGISTRY,
    build_default_operator_launch_profile,
    build_operator_launch_acceptance,
    prepare_operator_launch,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _required_paths() -> tuple[str, ...]:
    return tuple(
        route.path for route in RESEARCH_WORKSPACE_ROUTE_REGISTRY.routes
    ) + tuple(
        route.path for route in EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY.routes
    )


def test_d5_machine_readable_acceptance_preserves_boundaries() -> None:
    acceptance = build_operator_launch_acceptance()

    assert PRODUCT_ACCEPTANCE_STAGE_ID == "D5"
    assert acceptance.status == "READY_FOR_OPERATOR_USE"
    assert all(acceptance.checks.values())
    assert "loopback-only" in acceptance.permanent_restrictions
    assert "read-only-presentation" in acceptance.permanent_restrictions
    assert "no-real-execution" in acceptance.permanent_restrictions


def test_d5_real_http_product_routes_are_read_only_and_labeled() -> None:
    profile = build_default_operator_launch_profile(
        project_root=PROJECT_ROOT,
        port=18765,
        open_browser=False,
    )
    session = prepare_operator_launch(profile)
    server = session.create_server()
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        assert server.server_address == ("127.0.0.1", 18765)
        for path in _required_paths():
            request = urllib.request.Request(
                f"http://127.0.0.1:18765{path}",
                method="GET",
            )
            with urllib.request.urlopen(request, timeout=2.0) as response:
                status = response.status
                body = response.read().decode("utf-8")
                headers = response.headers

            assert status == 200, path
            assert "DEMONSTRATION_ONLY" in body, path
            assert "Operator review" in body, path
            assert "<form" not in body.lower(), path
            assert "<button" not in body.lower(), path
            assert "<script" not in body.lower(), path
            assert headers["Cache-Control"] == "no-store", path
            assert headers["X-Content-Type-Options"] == "nosniff", path
    finally:
        server.shutdown()
        thread.join(timeout=3.0)
        server.server_close()

    assert not thread.is_alive()


def test_d5_stocks_page_demonstrates_all_requested_market_types() -> None:
    profile = build_default_operator_launch_profile(project_root=PROJECT_ROOT)
    session = prepare_operator_launch(profile)
    body = session.runtime.application.dispatch(
        "GET", "/stocks"
    ).body.decode("utf-8")

    assert "Demonstration A Share" in body
    assert "Demonstration US Equity" in body
    assert "Demonstration Bitcoin" in body
    assert "NOT_CURRENT_MARKET_DATA" in body


def test_d5_windows_launcher_is_explicit_and_local() -> None:
    launcher = (PROJECT_ROOT / "START_FCF_BROWSER_CONSOLE.cmd").read_text(
        encoding="ascii"
    )

    assert "run_browser_product_console_runtime.py" in launcher
    assert "--allowed-root" not in launcher
    assert "http://" not in launcher
    assert "start " not in launcher.lower()


def test_d5_operator_guide_contains_safe_product_handoff() -> None:
    guide = (
        PROJECT_ROOT / "docs" / "BROWSER_PRODUCT_CONSOLE_OPERATOR_GUIDE.md"
    ).read_text(encoding="ascii")

    assert "START_FCF_BROWSER_CONSOLE.cmd" in guide
    assert "DEMONSTRATION_ONLY" in guide
    assert "A-share, US-equity, and BTC" in guide
    assert "FCF-LAUNCH-PORT-UNAVAILABLE" in guide
    assert "no broker, exchange, credential" in guide
