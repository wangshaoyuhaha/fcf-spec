from types import MappingProxyType
import pytest
from apps.fcf_api_gateway_app_1 import *


def _route(**u):
    v=dict(route_id="research-read",path="/v1/research/read",required_role="READER",policy_id="policy-a",request_schema_id="request-v1",response_schema_id="response-v1",idempotency_required=True,max_declared_cost_units=5);v.update(u);return RouteContract(**v)
def _request(**u):
    v=dict(request_id="request-a",correlation_id="correlation-a",route_id="research-read",principal_id="console",requested_at_utc="2026-07-16T13:00:00Z",schema_id="request-v1",declared_cost_units=1,payload=MappingProxyType({"query_id":"query-a"}),idempotency_key="idem-a");v.update(u);return ApiGatewayRequest(**v)
def _service(**u):
    v=dict(principals=LocalPrincipalRegistry((LocalPrincipal("console",("READER",)),)),routes=RouteRegistry((_route(),)),schemas=(SchemaContract("request-v1",("query_id",),("query_id",)),),budgets=(BudgetPolicy("console",3,5),),enabled_policy_ids=("policy-a",),handlers=MappingProxyType({"research-read":lambda p:MappingProxyType({"query_id":p["query_id"],"result":"registered-evidence"})}));v.update(u);return ApiGatewayService(**v)


def test_d2_auth_authorization_policy_and_schema_fail_closed():
    assert _service().dispatch(_request(principal_id="missing")).reason_codes==("authentication-failed",)
    principals=LocalPrincipalRegistry((LocalPrincipal("console",("REVIEWER",)),))
    assert _service(principals=principals).dispatch(_request()).reason_codes==("authorization-failed",)
    assert _service(enabled_policy_ids=()).dispatch(_request()).reason_codes==("policy-disabled",)
    assert _service().dispatch(_request(payload=MappingProxyType({"bad":"x"}))).reason_codes==("schema-invalid",)


def test_d3_correlation_idempotency_replay_and_conflict():
    service=_service();first=service.dispatch(_request());second=service.dispatch(_request(request_id="request-b"))
    assert first is second and service.audit_records[-1].idempotency_replay is True
    conflict=service.dispatch(_request(request_id="request-c",payload=MappingProxyType({"query_id":"other"})))
    assert conflict.reason_codes==("idempotency-conflict",)


def test_d3_required_idempotency_key_is_enforced():
    assert _service().dispatch(_request(idempotency_key=None)).reason_codes==("idempotency-key-required",)


def test_d4_route_cost_and_budget_are_enforced():
    assert _service().dispatch(_request(declared_cost_units=6)).reason_codes==("route-cost-exceeded",)
    service=_service(budgets=(BudgetPolicy("console",1,5),));assert service.dispatch(_request()).status is ApiResponseStatus.READY_FOR_OPERATOR_REVIEW
    assert service.dispatch(_request(request_id="b",idempotency_key="idem-b")).reason_codes==("budget-exceeded",)


def test_d5_dispatch_audit_and_review_packet_are_immutable():
    service=_service();response=service.dispatch(_request());packet=service.build_review_packet(response)
    assert response.status is ApiResponseStatus.READY_FOR_OPERATOR_REVIEW
    assert service.audit_records[0].correlation_id=="correlation-a"
    assert packet.payload["read_only"] is True and packet.payload["credential_material_present"] is False
    with pytest.raises(TypeError):packet.payload["status"]="tampered"


def test_d5_unregistered_or_mutable_handler_fails_closed():
    assert _service(handlers=MappingProxyType({})).dispatch(_request()).reason_codes==("handler-unregistered",)
    assert _service(handlers=MappingProxyType({"research-read":lambda p:{}})).dispatch(_request()).reason_codes==("handler-output-not-immutable",)


def test_d6_acceptance_preserves_local_read_only_boundary():
    service=_service();response=service.dispatch(_request());assert validate_api_acceptance(response,service.build_review_packet(response))=="PASS"
