from dataclasses import replace
from types import MappingProxyType
import pytest
from apps.multi_model_workflow_app_1 import *

def _model(mid,roles=("ANALYST",),health="HEALTHY"):return ModelMetadata(mid,"v1",roles,health,2)
def _prompt():return PromptIdentity("prompt-a","v1")
def _policy(role="ANALYST",primary="model-a",fallbacks=("model-b",)):return ModelRolePolicy(role,"policy-a",primary,fallbacks,_prompt(),1000,1,3)
def _request(roles=("ANALYST",),cost=10):return WorkflowRequest("workflow-a","correlation-a","config-a",roles,("evidence-a",),cost)
def _receipt(mid="model-a",role="ANALYST",status=AdvisoryStatus.SUCCESS,conclusion="BUY",cost=2,**u):
    payload=MappingProxyType({"conclusion":conclusion,"narrative":"advisory-only"});raw=b"registered-advisory";v=dict(receipt_id=f"receipt-{mid}",workflow_id="workflow-a",role=role,model_id=mid,model_version="v1",prompt=_prompt(),status=status,content_sha256=__import__('hashlib').sha256(raw).hexdigest(),evidence_ids=("evidence-a",),declared_cost_units=cost,latency_ms=10,advisory_payload=payload);v.update(u);return AdvisoryReceipt(**v)
def _service():return MultiModelWorkflowService(MultiModelRegistry((_model("model-a"),_model("model-b")),(_policy(),)))

def test_d1_boundary_rejects_invocation_prompt_credentials_and_execution():
    for field in ("live_model_invocation_allowed","prompt_execution_allowed","model_credential_allowed","external_automatic_routing_allowed","real_execution_allowed"):
        with pytest.raises(ValueError,match="prohibited workflow"):replace(MULTI_MODEL_BOUNDARY,**{field:True})
def test_d1_model_and_receipt_reject_live_capabilities():
    with pytest.raises(ValueError,match="invocation or credentials"):_model("model-a",health="HEALTHY").__class__("m","v1",("A",),"HEALTHY",1,True,False)
    with pytest.raises(ValueError,match="without invocation"):_receipt(live_invocation_performed=True)
def test_d2_route_plan_is_policy_ordered_and_missing_role_fails_closed():
    registry=MultiModelRegistry((_model("model-a"),_model("model-b")),(_policy(),));assert registry.plan(_request())[0].ordered_model_ids==("model-a","model-b")
    with pytest.raises(ValueError,match="missing role policy"):registry.plan(_request(("RISK",)))
def test_d3_primary_success_is_preserved_as_advisory():
    o=_service().evaluate(_request(),(_receipt(),));assert o.status=="READY_FOR_OPERATOR_REVIEW" and o.selected_receipts[0].model_id=="model-a"
def test_d4_timeout_uses_registered_fallback_receipt():
    o=_service().evaluate(_request(),(_receipt(status=AdvisoryStatus.TIMEOUT),_receipt("model-b")));assert o.selected_receipts[0].model_id=="model-b" and not o.reason_codes
def test_d4_missing_results_and_cost_violation_block():
    assert _service().evaluate(_request(),()).status=="BLOCKED"
    assert "workflow-cost-exceeded" in _service().evaluate(_request(cost=1),(_receipt(),)).reason_codes
def test_d5_disagreement_is_visible_and_outputs_are_immutable():
    models=(_model("a",("ANALYST",)),_model("b",("RISK",)));policies=(_policy("ANALYST","a",()),_policy("RISK","b",()))
    service=MultiModelWorkflowService(MultiModelRegistry(models,policies));o=service.evaluate(_request(("ANALYST","RISK")),(_receipt("a"),_receipt("b",role="RISK",conclusion="SELL")))
    assert o.disagreement is DisagreementClass.MATERIAL_DISAGREEMENT and o.status=="DEGRADED"
    p=service.build_review_packet(o);assert len(p.payload["original_outputs"])==2
    with pytest.raises(TypeError):p.payload["status"]="tampered"
def test_d6_acceptance_preserves_advisory_operator_boundary():
    s=_service();o=s.evaluate(_request(),(_receipt(),));assert validate_workflow_acceptance(o,s.build_review_packet(o))=="PASS"
