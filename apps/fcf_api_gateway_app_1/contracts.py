from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Mapping


_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")
_PATH = re.compile(r"^/v1/[a-z0-9][a-z0-9/-]{0,126}$")


def _id(value: object, name: str) -> str:
    text = str(value).strip()
    if _ID.fullmatch(text) is None:
        raise ValueError(f"{name} must be a safe identifier")
    return text


def _utc(value: object, name: str) -> str:
    text = str(value).strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{name} must be ISO-8601") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError(f"{name} must be UTC")
    return text


@dataclass(frozen=True)
class ApiGatewayBoundary:
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    read_only_routes_only: bool = True
    operator_review_required: bool = True
    registered_principal_only: bool = True
    external_binding_allowed: bool = False
    credential_material_allowed: bool = False
    public_api_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        if not all((self.local_only, self.loopback_only, self.sidecar_only, self.read_only_routes_only, self.operator_review_required, self.registered_principal_only)):
            raise ValueError("API gateway authority flags must remain enabled")
        if any((self.external_binding_allowed, self.credential_material_allowed, self.public_api_allowed, self.order_path_allowed, self.real_execution_allowed, self.automatic_activation_allowed)):
            raise ValueError("prohibited API gateway capability cannot be enabled")


API_GATEWAY_BOUNDARY = ApiGatewayBoundary()


@dataclass(frozen=True)
class LocalPrincipal:
    principal_id: str
    roles: tuple[str, ...]
    authentication_method: str = "LOOPBACK_PROCESS"
    credential_material_present: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "principal_id", _id(self.principal_id, "principal_id"))
        roles = tuple(sorted({_id(x, "role").upper() for x in self.roles}))
        if not roles:
            raise ValueError("roles must not be empty")
        object.__setattr__(self, "roles", roles)
        if self.authentication_method != "LOOPBACK_PROCESS":
            raise ValueError("authentication_method must be LOOPBACK_PROCESS")
        if self.credential_material_present:
            raise ValueError("credential material must not be present")


@dataclass(frozen=True)
class RouteContract:
    route_id: str
    path: str
    required_role: str
    policy_id: str
    request_schema_id: str
    response_schema_id: str
    idempotency_required: bool
    max_declared_cost_units: int
    read_only: bool = True

    def __post_init__(self) -> None:
        for name in ("route_id", "required_role", "policy_id", "request_schema_id", "response_schema_id"):
            object.__setattr__(self, name, _id(getattr(self, name), name))
        object.__setattr__(self, "required_role", self.required_role.upper())
        if _PATH.fullmatch(self.path) is None:
            raise ValueError("path must be a canonical /v1 path")
        if not isinstance(self.max_declared_cost_units, int) or self.max_declared_cost_units < 0:
            raise ValueError("max_declared_cost_units must be non-negative")
        if self.read_only is not True:
            raise ValueError("API route must remain read-only")


@dataclass(frozen=True)
class ApiGatewayRequest:
    request_id: str
    correlation_id: str
    route_id: str
    principal_id: str
    requested_at_utc: str
    schema_id: str
    declared_cost_units: int
    payload: Mapping[str, object]
    idempotency_key: str | None = None
    peer_host: str = "127.0.0.1"

    def __post_init__(self) -> None:
        for name in ("request_id", "correlation_id", "route_id", "principal_id", "schema_id"):
            object.__setattr__(self, name, _id(getattr(self, name), name))
        object.__setattr__(self, "requested_at_utc", _utc(self.requested_at_utc, "requested_at_utc"))
        if self.idempotency_key is not None:
            object.__setattr__(self, "idempotency_key", _id(self.idempotency_key, "idempotency_key"))
        if not isinstance(self.declared_cost_units, int) or self.declared_cost_units < 0:
            raise ValueError("declared_cost_units must be non-negative")
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("request payload must be immutable")
        if self.peer_host != "127.0.0.1":
            raise ValueError("API request peer must be exactly 127.0.0.1")


class ApiResponseStatus(str, Enum):
    READY_FOR_OPERATOR_REVIEW = "READY_FOR_OPERATOR_REVIEW"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ApiGatewayResponse:
    request_id: str
    correlation_id: str
    status: ApiResponseStatus
    payload: Mapping[str, object]
    reason_codes: tuple[str, ...] = ()
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "status", ApiResponseStatus(self.status))
        object.__setattr__(self, "reason_codes", tuple(sorted({_id(x, "reason_code") for x in self.reason_codes})))
        if not isinstance(self.payload, MappingProxyType):
            raise TypeError("response payload must be immutable")
        if self.status is ApiResponseStatus.BLOCKED and not self.reason_codes:
            raise ValueError("blocked response requires a reason")
        if self.operator_review_required is not True or self.automatic_activation_allowed is not False:
            raise ValueError("response review boundary is invalid")
