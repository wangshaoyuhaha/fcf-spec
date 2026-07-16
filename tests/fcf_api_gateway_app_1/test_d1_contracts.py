from dataclasses import replace
from types import MappingProxyType
import pytest
from apps.fcf_api_gateway_app_1 import *


def test_d1_boundary_rejects_external_credentials_and_execution():
    for field in ("external_binding_allowed", "credential_material_allowed", "public_api_allowed", "order_path_allowed", "real_execution_allowed"):
        with pytest.raises(ValueError, match="prohibited API gateway"):
            replace(API_GATEWAY_BOUNDARY, **{field: True})


def test_d1_principal_is_registered_role_metadata_without_secret():
    principal=LocalPrincipal("operator-console", ("reviewer", "reader", "reader"))
    assert principal.roles == ("READER", "REVIEWER")
    with pytest.raises(ValueError, match="credential material"):
        replace(principal, credential_material_present=True)


def test_d1_route_is_read_only_canonical_and_bounded():
    route=RouteContract("research-read", "/v1/research/read", "reader", "policy-a", "request-v1", "response-v1", True, 10)
    assert route.required_role == "READER"
    with pytest.raises(ValueError, match="canonical"):
        replace(route, path="/admin")
    with pytest.raises(ValueError, match="read-only"):
        replace(route, read_only=False)


def test_d1_request_requires_immutable_payload_loopback_and_utc():
    request=ApiGatewayRequest("request-a", "correlation-a", "research-read", "operator-console", "2026-07-16T12:00:00Z", "request-v1", 1, MappingProxyType({"query_id":"query-a"}), "idem-a")
    assert request.peer_host == "127.0.0.1"
    with pytest.raises(TypeError, match="immutable"):
        replace(request, payload={})
    with pytest.raises(ValueError, match="exactly 127.0.0.1"):
        replace(request, peer_host="localhost")


def test_d1_blocked_response_requires_reason_and_review():
    response=ApiGatewayResponse("request-a", "correlation-a", ApiResponseStatus.BLOCKED, MappingProxyType({}), ("policy-blocked",))
    assert response.reason_codes == ("policy-blocked",)
    with pytest.raises(ValueError, match="requires a reason"):
        replace(response, reason_codes=())
