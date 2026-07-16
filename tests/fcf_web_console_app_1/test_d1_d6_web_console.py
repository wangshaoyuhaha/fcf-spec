import json
import socket
import time
from http.client import HTTPConnection
from threading import Thread
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import ConsoleReadModel
from apps.fcf_web_console_app_1 import (
    FCF_WEB_CONSOLE_BOUNDARY,
    FCF_WEB_CONSOLE_ROUTES,
    ConsoleAction,
    FCFWebConsoleApplication,
    FCFWebConsoleServerConfig,
    GovernedConsoleActionService,
    GovernedIntakeService,
    WebConsoleSnapshot,
    build_fcf_web_console_acceptance,
    create_fcf_web_console_server,
)
from apps.browser_product_console_runtime_app_1 import RuntimeLifecycleState


_DIGEST = "a" * 64


def _snapshot() -> WebConsoleSnapshot:
    return WebConsoleSnapshot(
        correlation_id="corr-stage-8",
        sections=MappingProxyType(
            {
                "workflow_status": (
                    MappingProxyType(
                        {
                            "active_role": "RESEARCH_READER",
                            "elapsed_seconds": 14,
                            "prompt_version": "prompt-v1",
                            "status": "OPERATOR_REVIEW_REQUIRED",
                        }
                    ),
                ),
                "ai_explanation": (
                    MappingProxyType(
                        {
                            "disagreement": "VISIBLE",
                            "model_name": "registered-advisory-model",
                            "risk_flags": ["MODEL_DRIFT"],
                        }
                    ),
                ),
                "portfolio_construction": (
                    MappingProxyType(
                        {
                            "authority": "DETERMINISTIC_ENGINE",
                            "paper_only": True,
                            "weight": 0.25,
                        }
                    ),
                ),
                "paper_position_proposal": (
                    MappingProxyType(
                        {
                            "operator_review_required": True,
                            "symbol": "BTC-USD",
                            "target_notional": 2500,
                        }
                    ),
                ),
                "comprehensive_report": (
                    MappingProxyType(
                        {
                            "evidence_reference": "evidence-1",
                            "status": "REVIEW_REQUIRED",
                        }
                    ),
                ),
                "runtime_cost": (
                    MappingProxyType({"cost_state": "WITHIN_LIMIT"}),
                ),
            }
        ),
        source_artifact_ids=("evidence-1", "portfolio-1", "report-1"),
    )


def _intake_payload(items):
    return {
        "confirmed": True,
        "correlation_id": "corr-stage-8",
        "freshness_classification": "REQUIRES_CHECK",
        "items": items,
        "licensing_status": "REQUIRES_REVIEW",
        "operator_id": "operator-1",
        "request_id": "intake-1",
        "source_classification": "CLASS_B",
        "trust_classification": "UNTRUSTED",
    }


def _file_item(item_id, kind, name, media_type):
    return {
        "content_sha256": _DIGEST,
        "display_name": name,
        "item_id": item_id,
        "kind": kind,
        "media_type": media_type,
        "size_bytes": 128,
        "source_reference": "",
    }


def _action_payload(action="REQUEST_REANALYSIS"):
    return {
        "action": action,
        "confirmed": True,
        "correlation_id": "corr-stage-8",
        "operator_id": "operator-1",
        "reason": "Registered evidence requires another deterministic review.",
        "request_id": "action-1",
        "target_artifact_id": "evidence-1",
    }


def _application():
    return FCFWebConsoleApplication(
        _snapshot(),
        registered_operator_ids=("operator-1",),
        approved_url_hosts=("research.example",),
    )


def test_d1_boundary_is_permanently_fail_closed():
    assert FCF_WEB_CONSOLE_BOUNDARY.paper_only is True
    assert FCF_WEB_CONSOLE_BOUNDARY.loopback_only is True
    assert FCF_WEB_CONSOLE_BOUNDARY.registered_evidence_authority is True
    assert FCF_WEB_CONSOLE_BOUNDARY.network_retrieval_allowed is False
    assert FCF_WEB_CONSOLE_BOUNDARY.model_invocation_allowed is False
    assert FCF_WEB_CONSOLE_BOUNDARY.financial_execution_allowed is False


def test_d1_product_routes_cover_every_required_surface():
    paths = tuple(route.path for route in FCF_WEB_CONSOLE_ROUTES)
    assert paths == (
        "/",
        "/intake",
        "/conversation",
        "/workflows",
        "/evidence",
        "/models",
        "/risk",
        "/portfolio",
        "/paper-portfolio",
        "/reports",
        "/operator-review",
        "/operations",
    )


def test_d1_snapshot_is_immutable():
    snapshot = _snapshot()
    with pytest.raises(TypeError):
        snapshot.sections["new"] = ()
    with pytest.raises(TypeError):
        snapshot.sections["runtime_cost"][0]["cost_state"] = "CHANGED"


@pytest.mark.parametrize(
    ("kind", "name", "media_type"),
    (
        ("PDF", "research.pdf", "application/pdf"),
        (
            "EXCEL",
            "fundamentals.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ),
        ("EXCEL", "legacy.xls", "application/vnd.ms-excel"),
        ("CSV", "prices.csv", "text/csv"),
        ("JSON", "evidence.json", "application/json"),
        ("LOCAL_FILE", "notes.txt", "text/plain"),
    ),
)
def test_d2_supported_file_intake_is_quarantined(kind, name, media_type):
    receipt = GovernedIntakeService(("research.example",)).validate(
        _intake_payload([_file_item("item-1", kind, name, media_type)]),
        "127.0.0.1",
    )
    assert receipt.status == "QUARANTINED_PENDING_EVIDENCE_REGISTRATION"
    assert receipt.evidence_registered is False
    assert receipt.authoritative_input is False


def test_d2_text_url_and_multi_file_intake_remain_non_authoritative():
    items = [
        _file_item("item-pdf", "PDF", "research.pdf", "application/pdf"),
        _file_item("item-csv", "CSV", "prices.csv", "text/csv"),
        {
            "content_sha256": "b" * 64,
            "display_name": "operator-text",
            "item_id": "item-text",
            "kind": "TEXT",
            "media_type": "text/plain",
            "size_bytes": 42,
            "source_reference": "",
        },
        {
            "content_sha256": "c" * 64,
            "display_name": "approved-research-url",
            "item_id": "item-url",
            "kind": "URL",
            "media_type": "text/uri-list",
            "size_bytes": 36,
            "source_reference": "https://research.example/evidence",
        },
    ]
    receipt = GovernedIntakeService(("research.example",)).validate(
        _intake_payload(items),
        "127.0.0.1",
    )
    assert len(receipt.descriptors) == 4
    assert receipt.network_retrieval_performed is False


def test_d2_intake_rejects_wrong_extension_and_credential_like_url():
    service = GovernedIntakeService()
    with pytest.raises(ValueError, match="extension"):
        service.validate(
            _intake_payload(
                [_file_item("item-1", "PDF", "payload.exe", "application/pdf")]
            ),
            "127.0.0.1",
        )
    url_item = {
        "content_sha256": _DIGEST,
        "display_name": "approved-url",
        "item_id": "url-1",
        "kind": "URL",
        "media_type": "text/uri-list",
        "size_bytes": 40,
        "source_reference": "https://research.example/data?api_key=value",
    }
    with pytest.raises(ValueError, match="credential-like"):
        service.validate(_intake_payload([url_item]), "127.0.0.1")


def test_d2_intake_rejects_url_host_outside_allowlist():
    url_item = {
        "content_sha256": _DIGEST,
        "display_name": "approved-url",
        "item_id": "url-1",
        "kind": "URL",
        "media_type": "text/uri-list",
        "size_bytes": 40,
        "source_reference": "https://outside.example/data",
    }
    with pytest.raises(ValueError, match="approved allowlist"):
        GovernedIntakeService(("research.example",)).validate(
            _intake_payload([url_item]), "127.0.0.1"
        )


def test_d2_intake_requires_loopback_confirmation_and_governance():
    service = GovernedIntakeService()
    payload = _intake_payload(
        [_file_item("item-1", "JSON", "data.json", "application/json")]
    )
    with pytest.raises(ValueError, match="exactly 127.0.0.1"):
        service.validate(payload, "::1")
    payload["confirmed"] = False
    with pytest.raises(ValueError, match="confirmation"):
        service.validate(payload, "127.0.0.1")


@pytest.mark.parametrize("action", tuple(action.value for action in ConsoleAction))
def test_d3_all_controlled_actions_create_requests_only(action):
    receipt = GovernedConsoleActionService(("operator-1",)).validate(
        _action_payload(action),
        "127.0.0.1",
    )
    assert receipt.status == "VALIDATED_OPERATOR_REQUEST"
    assert receipt.automatic_transition_allowed is False
    assert receipt.authority_mutated is False
    assert receipt.execution_performed is False


def test_d3_actions_require_identity_reason_confirmation_and_loopback():
    service = GovernedConsoleActionService(("operator-1",))
    for field_name in ("operator_id", "reason"):
        payload = _action_payload()
        payload[field_name] = ""
        with pytest.raises(ValueError, match=field_name):
            service.validate(payload, "127.0.0.1")
    payload = _action_payload()
    payload["confirmed"] = False
    with pytest.raises(ValueError, match="confirmation"):
        service.validate(payload, "127.0.0.1")
    with pytest.raises(ValueError, match="exactly 127.0.0.1"):
        service.validate(_action_payload(), "localhost")


def test_d4_overview_exposes_health_cost_and_authorities():
    response = _application().dispatch("GET", "/")
    body = response.body.decode("utf-8")
    assert response.status == 200
    assert "Registered Evidence authority" in body
    assert "Deterministic Engine" in body
    assert "Cost records" in body
    assert "AI" in body and "Advisory only" in body


def test_d4_model_risk_and_workflow_views_render_mapping_proxy_payloads():
    application = _application()
    models = application.dispatch("GET", "/models").body.decode("utf-8")
    workflows = application.dispatch("GET", "/workflows").body.decode("utf-8")
    assert "MODEL_DRIFT" in models
    assert "VISIBLE" in models
    assert "OPERATOR_REVIEW_REQUIRED" in workflows
    assert "prompt-v1" in workflows


def test_d5_portfolio_paper_report_and_operator_surfaces_are_present():
    application = _application()
    portfolio = application.dispatch("GET", "/portfolio").body.decode("utf-8")
    paper = application.dispatch("GET", "/paper-portfolio").body.decode("utf-8")
    report = application.dispatch("GET", "/reports").body.decode("utf-8")
    review = application.dispatch("GET", "/operator-review").body.decode("utf-8")
    assert "DETERMINISTIC_ENGINE" in portfolio
    assert "BTC-USD" in paper
    assert "evidence-1" in report
    assert "Approve for Research Archive" in review
    assert "Override with Reason" in review


def test_d5_intake_conversation_and_operations_are_product_ui_pages():
    application = _application()
    intake = application.dispatch("GET", "/intake").body.decode("utf-8")
    conversation = application.dispatch("GET", "/conversation").body.decode("utf-8")
    operations = application.dispatch("GET", "/operations").body.decode("utf-8")
    assert 'type="file" multiple' in intake
    assert "Approved URL" in intake
    assert "Controlled research request" in conversation
    assert "Request Start" in operations
    assert "Request Stop" in operations
    assert "ONE-CLICK-LOCAL-OPERATIONS-APP-1" in operations


def test_d6_loopback_api_validates_intake_and_operator_requests():
    application = _application()
    intake = application.dispatch(
        "POST",
        "/api/intake/validate",
        _intake_payload(
            [_file_item("item-1", "CSV", "prices.csv", "text/csv")]
        ),
    )
    action = application.dispatch(
        "POST",
        "/api/operator/request",
        _action_payload(),
    )
    assert intake.status == 200
    assert json.loads(intake.body)["evidence_registered"] is False
    assert action.status == 200
    assert json.loads(action.body)["authority_mutated"] is False


def test_d6_non_loopback_unknown_and_write_page_requests_fail_closed():
    application = _application()
    assert application.dispatch("GET", "/", peer_host="::1").status == 403
    assert application.dispatch("GET", "/missing").status == 404
    assert application.dispatch("POST", "/portfolio").status == 405


def test_d6_health_head_and_existing_read_model_integration():
    read_model = ConsoleReadModel(
        correlation_id="corr-existing-model",
        candidates=(),
        sections=MappingProxyType({"paper_validation": ({"status": "PASS"},)}),
        source_artifact_ids=("paper-1",),
    )
    snapshot = WebConsoleSnapshot.from_console_read_model(read_model)
    application = FCFWebConsoleApplication(snapshot)
    health = json.loads(application.dispatch("GET", "/health").body)
    head = application.dispatch("HEAD", "/reports")
    assert health["calculation_authority"] == "Deterministic Engine"
    assert health["evidence_authority"] == "Registered Evidence"
    assert head.status == 200 and head.body == b""


def test_d6_acceptance_closes_d1_d6_without_starting_stage_9():
    acceptance = build_fcf_web_console_acceptance()
    assert acceptance.status == "D1_D6_ACCEPTED"
    assert "PDF" in acceptance.delivered_input_kinds
    assert "STOP_WORKFLOW" in acceptance.delivered_actions
    assert acceptance.deferred_stage == "ONE-CLICK-LOCAL-OPERATIONS-APP-1"


def test_d6_exact_loopback_http_adapter_serves_ui_and_json_api():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        port = int(handle.getsockname()[1])
    server = create_fcf_web_console_server(
        FCFWebConsoleServerConfig(port=port),
        _application(),
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    deadline = time.monotonic() + 3.0
    while (
        server.lifecycle_state is not RuntimeLifecycleState.SERVING
        and time.monotonic() < deadline
    ):
        time.sleep(0.01)
    try:
        connection = HTTPConnection("127.0.0.1", port, timeout=3.0)
        connection.request("GET", "/health", headers={"Host": f"127.0.0.1:{port}"})
        response = connection.getresponse()
        health = json.loads(response.read())
        connection.close()
        assert response.status == 200
        assert health["host_scope"] == "loopback-only"

        body = json.dumps(_action_payload()).encode("utf-8")
        connection = HTTPConnection("127.0.0.1", port, timeout=3.0)
        connection.request(
            "POST",
            "/api/operator/request",
            body=body,
            headers={
                "Content-Type": "application/json",
                "Host": f"127.0.0.1:{port}",
                "Origin": f"http://127.0.0.1:{port}",
            },
        )
        response = connection.getresponse()
        receipt = json.loads(response.read())
        connection.close()
        assert response.status == 200
        assert receipt["execution_performed"] is False
        assert receipt["operator_attested"] is True
    finally:
        server.shutdown()
        thread.join(timeout=3.0)
        server.server_close()


def test_d3_unregistered_operator_is_rejected():
    with pytest.raises(ValueError, match="registered Operator attestation"):
        GovernedConsoleActionService().validate(
            _action_payload(),
            "127.0.0.1",
        )


def test_d4_html_security_headers_use_nonce_and_block_framing():
    response = _application().dispatch("GET", "/")
    headers = dict(response.headers)
    policy = headers["Content-Security-Policy"]
    body = response.body.decode("utf-8")
    assert headers["X-Frame-Options"] == "DENY"
    assert "frame-ancestors 'none'" in policy
    assert "unsafe-inline" not in policy
    assert "script-src 'nonce-" in policy
    assert '<script nonce="' in body
