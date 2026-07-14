import hashlib
import json
import socket
from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    build_browser_console_runtime,
    build_browser_console_runtime_acceptance,
)


def _write_json(path: Path, payload: object) -> str:
    content = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
    )
    path.write_text(content, encoding="utf-8")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _write_runtime_fixture(root: Path) -> Path:
    watchlist_digest = _write_json(
        root / "watchlist.json",
        {
            "candidates": [
                {
                    "symbol": "600000",
                    "name": "Sample Stock",
                    "rank": 1,
                    "total_score": 88.5,
                    "score_breakdown": {
                        "momentum": 90.0,
                        "quality": 87.0,
                    },
                    "reason_codes": ["volume_expansion"],
                    "risk_flags": ["high_volatility"],
                    "data_quality_state": "PASS_STRICT",
                    "confidence_level": "MEDIUM",
                    "operator_review_required": True,
                }
            ]
        },
    )
    _write_json(
        root / "index.json",
        {
            "schema_version": "fcf.browser_console.artifact_index.v1",
            "correlation_id": "corr-d6-runtime-1",
            "entries": [
                {
                    "artifact_id": "watchlist-d6",
                    "artifact_type": "ranked_watchlist",
                    "correlation_id": "corr-d6-runtime-1",
                    "relative_path": "watchlist.json",
                    "content_sha256": watchlist_digest,
                }
            ],
        },
    )
    return root / "index.json"


def _free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return int(probe.getsockname()[1])


def test_d6_acceptance_is_ready_for_main_merge():
    acceptance = build_browser_console_runtime_acceptance()

    assert acceptance.phase == "BROWSER-PRODUCT-CONSOLE-RUNTIME-APP-1"
    assert acceptance.status == "READY_FOR_MAIN_MERGE"
    assert acceptance.checks
    assert all(acceptance.checks.values())


def test_d6_acceptance_preserves_permanent_restrictions():
    acceptance = build_browser_console_runtime_acceptance()

    assert "p1-p47-frozen" in acceptance.permanent_restrictions
    assert "no-p48" in acceptance.permanent_restrictions
    assert "paper-only" in acceptance.permanent_restrictions
    assert "loopback-only" in acceptance.permanent_restrictions
    assert "operator-review-required" in acceptance.permanent_restrictions
    assert "no-order-path" in acceptance.permanent_restrictions
    assert "no-real-execution" in acceptance.permanent_restrictions


def test_d6_explicit_launcher_builds_health_endpoint(tmp_path: Path):
    index_path = _write_runtime_fixture(tmp_path)

    runtime = build_browser_console_runtime(
        allowed_root=tmp_path,
        index_path=index_path,
    )
    response = runtime.application.dispatch("GET", "/health")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert '"status": "ok"' in body
    assert '"host_scope": "loopback-only"' in body
    assert '"operator_review_required": true' in body


def test_d6_explicit_launcher_renders_stock_workspace(tmp_path: Path):
    index_path = _write_runtime_fixture(tmp_path)

    runtime = build_browser_console_runtime(
        allowed_root=tmp_path,
        index_path=index_path,
    )
    response = runtime.application.dispatch("GET", "/stocks")
    body = response.body.decode("utf-8")

    assert response.status == 200
    assert "600000" in body
    assert "volume_expansion" in body
    assert "high_volatility" in body
    assert "PASS_STRICT" in body


def test_d6_explicit_launcher_binds_exact_loopback(tmp_path: Path):
    index_path = _write_runtime_fixture(tmp_path)
    runtime = build_browser_console_runtime(
        allowed_root=tmp_path,
        index_path=index_path,
        port=_free_loopback_port(),
    )

    server = runtime.create_server()
    try:
        assert server.server_address[0] == "127.0.0.1"
        assert server.server_address[1] == runtime.config.port
    finally:
        server.server_close()


def test_d6_explicit_launcher_rejects_tampered_artifact(tmp_path: Path):
    index_path = _write_runtime_fixture(tmp_path)
    (tmp_path / "watchlist.json").write_text(
        json.dumps({"candidates": []}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        build_browser_console_runtime(
            allowed_root=tmp_path,
            index_path=index_path,
        )
