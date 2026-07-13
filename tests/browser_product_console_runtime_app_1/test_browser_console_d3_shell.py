
from types import MappingProxyType

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
    StockCandidateCard,
)


def _model():
    candidate = StockCandidateCard(
        symbol="600000",
        name="Sample Stock",
        rank=1,
        total_score=88.5,
        score_breakdown=MappingProxyType(
            {"momentum": 90.0, "quality": 87.0}
        ),
        reason_codes=("volume_expansion",),
        risk_flags=("high_volatility",),
        data_quality_state="PASS_STRICT",
        confidence_level="MEDIUM",
        operator_review_required=True,
    )
    return ConsoleReadModel(
        correlation_id="corr-shell-1",
        candidates=(candidate,),
        sections=MappingProxyType(
            {
                "paper_validation": (
                    {"status": "REVIEW_REQUIRED"},
                ),
                "shadow_observation": (
                    {"status": "REVIEW_PACKET_READY"},
                ),
                "operator_review": (
                    {"status": "PENDING"},
                ),
                "report_archive": (
                    {"status": "NOT_ARCHIVED"},
                ),
            }
        ),
        source_artifact_ids=(
            "watchlist-1",
            "paper-1",
            "shadow-1",
        ),
    )


def test_d3_overview_page_is_read_only_console():
    response = BrowserProductConsoleApplication(_model()).dispatch(
        "GET",
        "/",
    )

    body = response.body.decode("utf-8")
    assert response.status == 200
    assert "Paper-only" in body
    assert "Operator review required" in body
    assert "Stock candidates: 1" in body


def test_d3_stock_page_renders_required_candidate_evidence():
    response = BrowserProductConsoleApplication(_model()).dispatch(
        "GET",
        "/stocks",
    )

    body = response.body.decode("utf-8")
    assert response.status == 200
    assert "600000" in body
    assert "momentum" in body
    assert "volume_expansion" in body
    assert "high_volatility" in body
    assert "PASS_STRICT" in body


def test_d3_validation_page_renders_paper_and_shadow_sections():
    response = BrowserProductConsoleApplication(_model()).dispatch(
        "GET",
        "/validation",
    )

    body = response.body.decode("utf-8")
    assert response.status == 200
    assert "paper_validation" in body
    assert "shadow_observation" in body
    assert "REVIEW_PACKET_READY" in body


def test_d3_health_endpoint_is_loopback_paper_only_metadata():
    response = BrowserProductConsoleApplication(_model()).dispatch(
        "GET",
        "/health",
    )

    body = response.body.decode("utf-8")
    assert response.status == 200
    assert '"host_scope": "loopback-only"' in body
    assert '"operator_review_required": true' in body
    assert '"mode": "paper-only"' in body


def test_d3_write_methods_are_rejected():
    response = BrowserProductConsoleApplication(_model()).dispatch(
        "POST",
        "/review",
    )

    assert response.status == 405
    assert response.body == b"Method Not Allowed"


def test_d3_unknown_route_is_not_found():
    response = BrowserProductConsoleApplication(_model()).dispatch(
        "GET",
        "/unknown",
    )

    assert response.status == 404
    assert response.body == b"Not Found"
