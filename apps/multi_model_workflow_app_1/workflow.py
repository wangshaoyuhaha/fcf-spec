from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Iterable, Mapping


_ID=re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_SHA=re.compile(r"^[0-9a-f]{64}$")
def _id(v:object,n:str)->str:
    s=str(v).strip()
    if _ID.fullmatch(s) is None:raise ValueError(f"{n} must be a safe identifier")
    return s


@dataclass(frozen=True)
class MultiModelBoundary:
    paper_only:bool=True;local_only:bool=True;sidecar_only:bool=True
    registered_receipt_only:bool=True;operator_review_required:bool=True
    deterministic_authority_preserved:bool=True;registered_evidence_authority_preserved:bool=True
    ai_advisory_only:bool=True;live_model_invocation_allowed:bool=False
    prompt_execution_allowed:bool=False;model_credential_allowed:bool=False
    external_automatic_routing_allowed:bool=False;automatic_activation_allowed:bool=False
    real_execution_allowed:bool=False
    def __post_init__(self)->None:
        if not all((self.paper_only,self.local_only,self.sidecar_only,self.registered_receipt_only,self.operator_review_required,self.deterministic_authority_preserved,self.registered_evidence_authority_preserved,self.ai_advisory_only)):raise ValueError("workflow authority flags must remain enabled")
        if any((self.live_model_invocation_allowed,self.prompt_execution_allowed,self.model_credential_allowed,self.external_automatic_routing_allowed,self.automatic_activation_allowed,self.real_execution_allowed)):raise ValueError("prohibited workflow capability cannot be enabled")
MULTI_MODEL_BOUNDARY=MultiModelBoundary()


@dataclass(frozen=True)
class PromptIdentity:
    prompt_id:str;prompt_version:str
    def __post_init__(self)->None:
        object.__setattr__(self,"prompt_id",_id(self.prompt_id,"prompt_id"));object.__setattr__(self,"prompt_version",_id(self.prompt_version,"prompt_version"))


@dataclass(frozen=True)
class ModelMetadata:
    model_id:str;model_version:str;roles:tuple[str,...];health_status:str;cost_units_per_receipt:int
    live_invocation_enabled:bool=False;credential_material_present:bool=False
    def __post_init__(self)->None:
        object.__setattr__(self,"model_id",_id(self.model_id,"model_id"));object.__setattr__(self,"model_version",_id(self.model_version,"model_version"))
        roles=tuple(sorted({_id(x,"role").upper() for x in self.roles}));
        if not roles:raise ValueError("model roles must not be empty")
        object.__setattr__(self,"roles",roles);object.__setattr__(self,"health_status",_id(self.health_status,"health_status").upper())
        if self.cost_units_per_receipt<0:raise ValueError("model cost must be non-negative")
        if self.live_invocation_enabled or self.credential_material_present:raise ValueError("model metadata cannot enable invocation or credentials")


@dataclass(frozen=True)
class ModelRolePolicy:
    role:str;policy_id:str;primary_model_id:str;fallback_model_ids:tuple[str,...]
    prompt:PromptIdentity;timeout_ms:int;max_retries:int;max_cost_units:int
    def __post_init__(self)->None:
        object.__setattr__(self,"role",_id(self.role,"role").upper())
        for n in ("policy_id","primary_model_id"):object.__setattr__(self,n,_id(getattr(self,n),n))
        object.__setattr__(self,"fallback_model_ids",tuple(dict.fromkeys(_id(x,"fallback_model_id") for x in self.fallback_model_ids)))
        if self.primary_model_id in self.fallback_model_ids:raise ValueError("primary model cannot be its own fallback")
        if self.timeout_ms<1 or self.max_retries<0 or self.max_cost_units<0:raise ValueError("route bounds are invalid")


@dataclass(frozen=True)
class WorkflowRequest:
    workflow_id:str;correlation_id:str;config_snapshot_id:str
    required_roles:tuple[str,...];evidence_ids:tuple[str,...];max_total_cost_units:int
    operator_review_required:bool=True
    def __post_init__(self)->None:
        for n in ("workflow_id","correlation_id","config_snapshot_id"):object.__setattr__(self,n,_id(getattr(self,n),n))
        object.__setattr__(self,"required_roles",tuple(sorted({_id(x,"required_role").upper() for x in self.required_roles})))
        object.__setattr__(self,"evidence_ids",tuple(sorted({_id(x,"evidence_id") for x in self.evidence_ids})))
        if not self.required_roles or not self.evidence_ids or self.max_total_cost_units<0:raise ValueError("workflow request is incomplete")
        if self.operator_review_required is not True:raise ValueError("operator_review_required must be true")


@dataclass(frozen=True)
class RoutePlan:
    role:str;policy_id:str;ordered_model_ids:tuple[str,...];prompt:PromptIdentity
    timeout_ms:int;max_retries:int;max_cost_units:int


class MultiModelRegistry:
    def __init__(self,models:Iterable[ModelMetadata],policies:Iterable[ModelRolePolicy])->None:
        ms=tuple(models);ps=tuple(policies)
        if not ms or not ps or not all(isinstance(x,ModelMetadata) for x in ms) or not all(isinstance(x,ModelRolePolicy) for x in ps):raise ValueError("registry requires model and policy contracts")
        if len({x.model_id for x in ms})!=len(ms) or len({x.role for x in ps})!=len(ps):raise ValueError("duplicate model or role policy")
        self._models=MappingProxyType({x.model_id:x for x in ms});self._policies=MappingProxyType({x.role:x for x in ps})
        for p in ps:
            for mid in (p.primary_model_id,)+p.fallback_model_ids:
                m=self._models.get(mid)
                if m is None or p.role not in m.roles:raise ValueError("route references an ineligible model")
    def plan(self,request:WorkflowRequest)->tuple[RoutePlan,...]:
        plans=[]
        for role in request.required_roles:
            p=self._policies.get(role)
            if p is None:raise ValueError(f"missing role policy: {role}")
            plans.append(RoutePlan(role,p.policy_id,(p.primary_model_id,)+p.fallback_model_ids,p.prompt,p.timeout_ms,p.max_retries,p.max_cost_units))
        return tuple(plans)
    def model(self,mid:str)->ModelMetadata:return self._models[mid]


class AdvisoryStatus(str,Enum):SUCCESS="SUCCESS";TIMEOUT="TIMEOUT";ERROR="ERROR"
@dataclass(frozen=True)
class AdvisoryReceipt:
    receipt_id:str;workflow_id:str;role:str;model_id:str;model_version:str
    prompt:PromptIdentity;status:AdvisoryStatus;content_sha256:str
    evidence_ids:tuple[str,...];declared_cost_units:int;latency_ms:int
    advisory_payload:Mapping[str,object];live_invocation_performed:bool=False;prompt_executed:bool=False
    def __post_init__(self)->None:
        for n in ("receipt_id","workflow_id","model_id","model_version"):object.__setattr__(self,n,_id(getattr(self,n),n))
        object.__setattr__(self,"role",_id(self.role,"role").upper());object.__setattr__(self,"status",AdvisoryStatus(self.status))
        d=str(self.content_sha256).lower()
        if _SHA.fullmatch(d) is None:raise ValueError("content_sha256 must be a SHA-256 digest")
        object.__setattr__(self,"content_sha256",d);object.__setattr__(self,"evidence_ids",tuple(sorted({_id(x,"evidence_id") for x in self.evidence_ids})))
        if self.declared_cost_units<0 or self.latency_ms<0:raise ValueError("receipt metrics must be non-negative")
        if not isinstance(self.advisory_payload,MappingProxyType):raise TypeError("advisory payload must be immutable")
        if self.live_invocation_performed or self.prompt_executed:raise ValueError("receipt must be imported without invocation or Prompt execution")


class DisagreementClass(str,Enum):CONSENSUS="CONSENSUS";MINOR_DISAGREEMENT="MINOR_DISAGREEMENT";MATERIAL_DISAGREEMENT="MATERIAL_DISAGREEMENT";INSUFFICIENT_EVIDENCE="INSUFFICIENT_EVIDENCE"
@dataclass(frozen=True)
class WorkflowOutcome:
    request:WorkflowRequest;plans:tuple[RoutePlan,...];selected_receipts:tuple[AdvisoryReceipt,...]
    disagreement:DisagreementClass;status:str;total_cost_units:int;reason_codes:tuple[str,...]
    operator_review_required:bool=True;automatic_activation_allowed:bool=False
@dataclass(frozen=True)
class WorkflowReviewPacket:payload:Mapping[str,object]


class MultiModelWorkflowService:
    def __init__(self,registry:MultiModelRegistry)->None:self._registry=registry
    def evaluate(self,request:WorkflowRequest,receipts:Iterable[AdvisoryReceipt])->WorkflowOutcome:
        plans=self._registry.plan(request);items=tuple(receipts);selected=[];reasons=[]
        for plan in plans:
            candidates=[x for x in items if x.workflow_id==request.workflow_id and x.role==plan.role and x.model_id in plan.ordered_model_ids]
            candidates.sort(key=lambda x:plan.ordered_model_ids.index(x.model_id))
            chosen=next((x for x in candidates if x.status is AdvisoryStatus.SUCCESS and x.prompt==plan.prompt),None)
            if chosen is None:reasons.append(f"role-{plan.role.lower()}-unavailable")
            else:
                model=self._registry.model(chosen.model_id)
                if chosen.model_version!=model.model_version or chosen.declared_cost_units>plan.max_cost_units:reasons.append(f"role-{plan.role.lower()}-receipt-invalid")
                else:selected.append(chosen)
        total=sum(x.declared_cost_units for x in selected)
        if total>request.max_total_cost_units:reasons.append("workflow-cost-exceeded")
        conclusions=[str(x.advisory_payload.get("conclusion","")).strip().upper() for x in selected]
        if not selected or any(not x for x in conclusions):disagreement=DisagreementClass.INSUFFICIENT_EVIDENCE
        elif len(set(conclusions))==1:disagreement=DisagreementClass.CONSENSUS
        elif len(set(conclusions))==2:disagreement=DisagreementClass.MATERIAL_DISAGREEMENT
        else:disagreement=DisagreementClass.MINOR_DISAGREEMENT
        status="BLOCKED" if reasons else ("DEGRADED" if disagreement is not DisagreementClass.CONSENSUS else "READY_FOR_OPERATOR_REVIEW")
        return WorkflowOutcome(request,plans,tuple(selected),disagreement,status,total,tuple(sorted(reasons)))
    def build_review_packet(self,o:WorkflowOutcome)->WorkflowReviewPacket:
        outputs=tuple(MappingProxyType({"content_sha256":x.content_sha256,"evidence_ids":x.evidence_ids,"model_id":x.model_id,"model_version":x.model_version,"payload":x.advisory_payload,"prompt_id":x.prompt.prompt_id,"prompt_version":x.prompt.prompt_version,"role":x.role,"status":x.status.value}) for x in o.selected_receipts)
        return WorkflowReviewPacket(MappingProxyType({"automatic_activation_allowed":False,"disagreement":o.disagreement.value,"operator_review_required":True,"original_outputs":outputs,"reason_codes":o.reason_codes,"status":o.status,"total_cost_units":o.total_cost_units,"workflow_id":o.request.workflow_id}))


def validate_workflow_acceptance(o:WorkflowOutcome,p:WorkflowReviewPacket)->str:
    if p.payload["workflow_id"]!=o.request.workflow_id or p.payload["status"]!=o.status:raise ValueError("workflow acceptance linkage failed")
    if p.payload["automatic_activation_allowed"] or MULTI_MODEL_BOUNDARY.live_model_invocation_allowed or MULTI_MODEL_BOUNDARY.real_execution_allowed:raise ValueError("workflow acceptance boundary failed")
    return "PASS"
