from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable, Iterable, Mapping

from .contracts import (
    API_GATEWAY_BOUNDARY, ApiGatewayRequest, ApiGatewayResponse,
    ApiResponseStatus, LocalPrincipal, RouteContract,
)


class LocalPrincipalRegistry:
    def __init__(self, principals: Iterable[LocalPrincipal]) -> None:
        items=tuple(principals)
        if not items or not all(isinstance(x,LocalPrincipal) for x in items): raise ValueError("principal registry requires LocalPrincipal values")
        if len({x.principal_id for x in items}) != len(items): raise ValueError("duplicate principal_id")
        self._items=MappingProxyType({x.principal_id:x for x in items})
    def get(self, key:str)->LocalPrincipal|None: return self._items.get(key)


class RouteRegistry:
    def __init__(self, routes: Iterable[RouteContract]) -> None:
        items=tuple(routes)
        if not items or not all(isinstance(x,RouteContract) for x in items): raise ValueError("route registry requires RouteContract values")
        if len({x.route_id for x in items}) != len(items) or len({x.path for x in items}) != len(items): raise ValueError("duplicate route authority")
        self._items=MappingProxyType({x.route_id:x for x in items})
    def get(self,key:str)->RouteContract|None:return self._items.get(key)


@dataclass(frozen=True)
class SchemaContract:
    schema_id: str
    required_fields: tuple[str,...]
    allowed_fields: tuple[str,...]
    def __post_init__(self)->None:
        required=tuple(sorted(set(self.required_fields))); allowed=tuple(sorted(set(self.allowed_fields)))
        if not set(required)<=set(allowed): raise ValueError("required fields must be allowed")
        object.__setattr__(self,"required_fields",required);object.__setattr__(self,"allowed_fields",allowed)
    def validate(self,payload:Mapping[str,object])->bool:
        keys=set(payload);return set(self.required_fields)<=keys and keys<=set(self.allowed_fields)


@dataclass(frozen=True)
class BudgetPolicy:
    principal_id: str
    max_requests: int
    max_cost_units: int
    def __post_init__(self)->None:
        if self.max_requests<1 or self.max_cost_units<0: raise ValueError("budget limits are invalid")


@dataclass(frozen=True)
class ApiAuditRecord:
    request_id:str
    correlation_id:str
    principal_id:str
    route_id:str
    status:str
    reason_codes:tuple[str,...]
    declared_cost_units:int
    idempotency_replay:bool=False


@dataclass(frozen=True)
class ApiReviewPacket:
    payload:Mapping[str,object]


Handler=Callable[[Mapping[str,object]],Mapping[str,object]]


class ApiGatewayService:
    def __init__(self, principals:LocalPrincipalRegistry, routes:RouteRegistry, schemas:Iterable[SchemaContract], budgets:Iterable[BudgetPolicy], enabled_policy_ids:Iterable[str], handlers:Mapping[str,Handler])->None:
        self._principals=principals;self._routes=routes
        self._schemas={x.schema_id:x for x in schemas};self._budgets={x.principal_id:x for x in budgets}
        self._policies=frozenset(enabled_policy_ids);self._handlers=dict(handlers)
        self._counts:dict[str,tuple[int,int]]={};self._idem:dict[str,tuple[str,ApiGatewayResponse]]={};self._audit:list[ApiAuditRecord]=[]

    @property
    def audit_records(self)->tuple[ApiAuditRecord,...]:return tuple(self._audit)

    def _blocked(self,r:ApiGatewayRequest,*reasons:str)->ApiGatewayResponse:
        response=ApiGatewayResponse(r.request_id,r.correlation_id,ApiResponseStatus.BLOCKED,MappingProxyType({}),tuple(reasons))
        self._audit.append(ApiAuditRecord(r.request_id,r.correlation_id,r.principal_id,r.route_id,response.status.value,response.reason_codes,r.declared_cost_units))
        return response

    def dispatch(self,r:ApiGatewayRequest)->ApiGatewayResponse:
        if not isinstance(r,ApiGatewayRequest):raise TypeError("request must be ApiGatewayRequest")
        principal=self._principals.get(r.principal_id);route=self._routes.get(r.route_id)
        if principal is None:return self._blocked(r,"authentication-failed")
        if route is None:return self._blocked(r,"route-unregistered")
        if route.required_role not in principal.roles:return self._blocked(r,"authorization-failed")
        if route.policy_id not in self._policies:return self._blocked(r,"policy-disabled")
        schema=self._schemas.get(r.schema_id)
        if schema is None or r.schema_id!=route.request_schema_id or not schema.validate(r.payload):return self._blocked(r,"schema-invalid")
        if route.idempotency_required and r.idempotency_key is None:return self._blocked(r,"idempotency-key-required")
        canonical=json.dumps(dict(r.payload),sort_keys=True,separators=(",",":"),ensure_ascii=True).encode("ascii")
        digest=hashlib.sha256(canonical).hexdigest()
        if r.idempotency_key in self._idem:
            old_digest,old_response=self._idem[r.idempotency_key]
            if old_digest!=digest:return self._blocked(r,"idempotency-conflict")
            self._audit.append(ApiAuditRecord(r.request_id,r.correlation_id,r.principal_id,r.route_id,old_response.status.value,(),r.declared_cost_units,True))
            return old_response
        if r.declared_cost_units>route.max_declared_cost_units:return self._blocked(r,"route-cost-exceeded")
        budget=self._budgets.get(r.principal_id)
        if budget is None:return self._blocked(r,"budget-missing")
        count,cost=self._counts.get(r.principal_id,(0,0))
        if count+1>budget.max_requests or cost+r.declared_cost_units>budget.max_cost_units:return self._blocked(r,"budget-exceeded")
        handler=self._handlers.get(route.route_id)
        if handler is None:return self._blocked(r,"handler-unregistered")
        output=handler(r.payload)
        if not isinstance(output,MappingProxyType):return self._blocked(r,"handler-output-not-immutable")
        response=ApiGatewayResponse(r.request_id,r.correlation_id,ApiResponseStatus.READY_FOR_OPERATOR_REVIEW,output)
        self._counts[r.principal_id]=(count+1,cost+r.declared_cost_units)
        if r.idempotency_key:self._idem[r.idempotency_key]=(digest,response)
        self._audit.append(ApiAuditRecord(r.request_id,r.correlation_id,r.principal_id,r.route_id,response.status.value,(),r.declared_cost_units))
        return response

    def build_review_packet(self,response:ApiGatewayResponse)->ApiReviewPacket:
        records=tuple(x for x in self._audit if x.request_id==response.request_id)
        return ApiReviewPacket(MappingProxyType({"automatic_activation_allowed":False,"credential_material_present":False,"operator_review_required":True,"read_only":True,"request_id":response.request_id,"correlation_id":response.correlation_id,"status":response.status.value,"reason_codes":response.reason_codes,"audit_count":len(records)}))


def validate_api_acceptance(response:ApiGatewayResponse,packet:ApiReviewPacket)->str:
    if packet.payload["request_id"]!=response.request_id or packet.payload["status"]!=response.status.value:raise ValueError("API acceptance linkage failed")
    if packet.payload["credential_material_present"] or packet.payload["automatic_activation_allowed"]:raise ValueError("API acceptance boundary failed")
    if API_GATEWAY_BOUNDARY.external_binding_allowed or API_GATEWAY_BOUNDARY.real_execution_allowed:raise ValueError("API runtime boundary failed")
    return "PASS"
