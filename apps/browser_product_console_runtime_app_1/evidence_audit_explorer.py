from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Tuple

_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
_FILTER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]*$")
_ROUTE = re.compile(r"^[a-z][a-z0-9_]*$")
_SHA = re.compile(r"^[0-9a-f]{64}$")


def _text(value: object, name: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f"{name} is required")
    return result


def _identity(value: object, name: str) -> str:
    result = _text(value, name)
    if not _ID.fullmatch(result):
        raise ValueError(f"{name} contains a prohibited character")
    return result


def _filters(value: object, name: str) -> Tuple[str, ...]:
    if value is None:
        return ()
    raw = (value,) if isinstance(value, str) else tuple(value)
    result = tuple(_text(item, name) for item in raw)
    if any(not _FILTER.fullmatch(item) for item in result):
        raise ValueError(f"{name} contains a prohibited value")
    if len(set(result)) != len(result):
        raise ValueError(f"{name} values must be unique")
    return tuple(sorted(result))


class EvidenceIntegrityState(str, Enum):
    VERIFIED = "VERIFIED"
    MISSING = "MISSING"
    INCOMPLETE = "INCOMPLETE"
    REJECTED = "REJECTED"
    TAMPERED = "TAMPERED"


class EvidenceRelation(str, Enum):
    CORRELATES_WITH = "CORRELATES_WITH"
    DERIVED_FROM = "DERIVED_FROM"
    VALIDATES = "VALIDATES"
    REVIEWS = "REVIEWS"
    ARCHIVES = "ARCHIVES"
    CONTRADICTS = "CONTRADICTS"


class EvidenceExplorerRole(str, Enum):
    EVIDENCE_READER = "EVIDENCE_READER"
    OPERATOR_REVIEWER = "OPERATOR_REVIEWER"
    GOVERNANCE_REVIEWER = "GOVERNANCE_REVIEWER"
    AUDIT_READER = "AUDIT_READER"


@dataclass(frozen=True)
class EvidenceAuditExplorerBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_authority: bool = True
    registered_evidence_authority: bool = True
    ai_advisory_only: bool = True
    evidence_mutation_allowed: bool = False
    source_artifact_mutation_allowed: bool = False
    record_deletion_allowed: bool = False
    command_dispatch_allowed: bool = False
    workflow_dispatch_allowed: bool = False
    external_data_fetch_allowed: bool = False
    external_network_binding_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    automatic_model_activation_allowed: bool = False
    automatic_prompt_activation_allowed: bool = False
    automatic_learning_activation_allowed: bool = False
    automatic_archive_allowed: bool = False
    real_execution_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_authority,
            self.registered_evidence_authority,
            self.ai_advisory_only,
        )
        if not all(required):
            raise ValueError("explorer authority flags must remain enabled")
        prohibited = (
            self.evidence_mutation_allowed,
            self.source_artifact_mutation_allowed,
            self.record_deletion_allowed,
            self.command_dispatch_allowed,
            self.workflow_dispatch_allowed,
            self.external_data_fetch_allowed,
            self.external_network_binding_allowed,
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_model_activation_allowed,
            self.automatic_prompt_activation_allowed,
            self.automatic_learning_activation_allowed,
            self.automatic_archive_allowed,
            self.real_execution_allowed,
        )
        if any(prohibited):
            raise ValueError("prohibited explorer capability cannot be enabled")


@dataclass(frozen=True)
class EvidenceArtifactNode:
    artifact_id: str
    artifact_type: str
    correlation_id: str
    relative_path: str
    content_sha256: str
    integrity_state: EvidenceIntegrityState
    payload_keys: Tuple[str, ...] = ()
    risk_flags: Tuple[str, ...] = ()
    contradiction_codes: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "artifact_id", _identity(self.artifact_id, "artifact_id"))
        object.__setattr__(self, "artifact_type", _identity(self.artifact_type, "artifact_type"))
        object.__setattr__(self, "correlation_id", _identity(self.correlation_id, "correlation_id"))
        path = _text(self.relative_path, "relative_path")
        if path.startswith(("/", "\\")) or any(x in path for x in ("..", "?", "#", "\x00")):
            raise ValueError("relative_path contains a prohibited token")
        digest = _text(self.content_sha256, "content_sha256").lower()
        if not _SHA.fullmatch(digest):
            raise ValueError("content_sha256 must be a SHA-256 digest")
        try:
            state = self.integrity_state if isinstance(self.integrity_state, EvidenceIntegrityState) else EvidenceIntegrityState(str(self.integrity_state))
        except ValueError as exc:
            raise ValueError("unsupported evidence integrity state") from exc
        object.__setattr__(self, "relative_path", path)
        object.__setattr__(self, "content_sha256", digest)
        object.__setattr__(self, "integrity_state", state)
        object.__setattr__(self, "payload_keys", _filters(self.payload_keys, "payload_keys"))
        object.__setattr__(self, "risk_flags", _filters(self.risk_flags, "risk_flags"))
        object.__setattr__(self, "contradiction_codes", _filters(self.contradiction_codes, "contradiction_codes"))


@dataclass(frozen=True)
class EvidenceRelationship:
    source_artifact_id: str
    target_artifact_id: str
    relation: EvidenceRelation
    correlation_id: str

    def __post_init__(self) -> None:
        source = _identity(self.source_artifact_id, "source_artifact_id")
        target = _identity(self.target_artifact_id, "target_artifact_id")
        if source == target:
            raise ValueError("evidence relationship cannot reference itself")
        try:
            relation = self.relation if isinstance(self.relation, EvidenceRelation) else EvidenceRelation(str(self.relation))
        except ValueError as exc:
            raise ValueError("unsupported evidence relationship") from exc
        object.__setattr__(self, "source_artifact_id", source)
        object.__setattr__(self, "target_artifact_id", target)
        object.__setattr__(self, "relation", relation)
        object.__setattr__(self, "correlation_id", _identity(self.correlation_id, "correlation_id"))


@dataclass(frozen=True)
class EvidenceAuditQuery:
    correlation_id: str | None = None
    artifact_ids: Tuple[str, ...] = ()
    artifact_types: Tuple[str, ...] = ()
    integrity_states: Tuple[EvidenceIntegrityState, ...] = ()
    risk_flags: Tuple[str, ...] = ()
    contradiction_codes: Tuple[str, ...] = ()
    offset: int = 0
    limit: int = 100
    sort_order: str = "ASC"

    def __post_init__(self) -> None:
        correlation_id = None if self.correlation_id is None else _identity(self.correlation_id, "correlation_id")
        states = []
        for value in self.integrity_states:
            try:
                states.append(value if isinstance(value, EvidenceIntegrityState) else EvidenceIntegrityState(str(value)))
            except ValueError as exc:
                raise ValueError("unsupported integrity state filter") from exc
        offset, limit = int(self.offset), int(self.limit)
        if offset < 0:
            raise ValueError("offset must be non-negative")
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        order = _text(self.sort_order, "sort_order").upper()
        if order not in {"ASC", "DESC"}:
            raise ValueError("sort_order must be ASC or DESC")
        object.__setattr__(self, "correlation_id", correlation_id)
        object.__setattr__(self, "artifact_ids", _filters(self.artifact_ids, "artifact_ids"))
        object.__setattr__(self, "artifact_types", _filters(self.artifact_types, "artifact_types"))
        object.__setattr__(self, "integrity_states", tuple(sorted(set(states), key=lambda item: item.value)))
        object.__setattr__(self, "risk_flags", _filters(self.risk_flags, "risk_flags"))
        object.__setattr__(self, "contradiction_codes", _filters(self.contradiction_codes, "contradiction_codes"))
        object.__setattr__(self, "offset", offset)
        object.__setattr__(self, "limit", limit)
        object.__setattr__(self, "sort_order", order)

    @classmethod
    def from_mapping(cls, values: Mapping[str, object]) -> "EvidenceAuditQuery":
        if not isinstance(values, Mapping):
            raise ValueError("query values must be a mapping")
        allowed = {
            "correlation_id", "artifact_ids", "artifact_types",
            "integrity_states", "risk_flags", "contradiction_codes",
            "offset", "limit", "sort_order",
        }
        unknown = sorted(set(values) - allowed)
        if unknown:
            raise ValueError("unsupported query parameter: " + ",".join(unknown))
        raw_states = values.get("integrity_states", ())
        states = (raw_states,) if isinstance(raw_states, str) else tuple(raw_states)
        return cls(
            correlation_id=values.get("correlation_id"),
            artifact_ids=values.get("artifact_ids", ()),
            artifact_types=values.get("artifact_types", ()),
            integrity_states=states,
            risk_flags=values.get("risk_flags", ()),
            contradiction_codes=values.get("contradiction_codes", ()),
            offset=int(values.get("offset", 0)),
            limit=int(values.get("limit", 100)),
            sort_order=str(values.get("sort_order", "ASC")),
        )


@dataclass(frozen=True)
class EvidenceAuditExplorerRoute:
    route_id: str
    path: str
    title: str
    navigation_order: int
    role: EvidenceExplorerRole
    evidence_capabilities: Tuple[str, ...]
    read_only: bool = True
    operator_review_required: bool = True
    ai_advisory_only: bool = True

    def __post_init__(self) -> None:
        route_id = _text(self.route_id, "route_id")
        if not _ROUTE.fullmatch(route_id):
            raise ValueError("route_id must use lower snake case")
        path = _text(self.path, "path")
        if not path.startswith("/evidence") or path.endswith("/") or any(x in path for x in ("?", "#", "..", "//")):
            raise ValueError("invalid Evidence Audit Explorer route")
        try:
            role = self.role if isinstance(self.role, EvidenceExplorerRole) else EvidenceExplorerRole(str(self.role))
        except ValueError as exc:
            raise ValueError("unsupported explorer role") from exc
        capabilities = _filters(self.evidence_capabilities, "evidence_capabilities")
        if not capabilities:
            raise ValueError("evidence_capabilities must not be empty")
        if not self.read_only or not self.operator_review_required or not self.ai_advisory_only:
            raise ValueError("explorer route authority mismatch")
        order = int(self.navigation_order)
        if order < 0:
            raise ValueError("navigation_order must be non-negative")
        object.__setattr__(self, "route_id", route_id)
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "title", _text(self.title, "title"))
        object.__setattr__(self, "navigation_order", order)
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "evidence_capabilities", capabilities)


@dataclass(frozen=True)
class EvidenceAuditExplorerRouteRegistry:
    schema_version: str
    routes: Tuple[EvidenceAuditExplorerRoute, ...]

    def __post_init__(self) -> None:
        if self.schema_version != "fcf.browser_console.evidence_audit.routes.v1":
            raise ValueError("unsupported explorer route schema")
        routes = tuple(self.routes)
        if not routes:
            raise ValueError("explorer route registry is empty")
        if len({r.route_id for r in routes}) != len(routes):
            raise ValueError("route_id values must be unique")
        if len({r.path for r in routes}) != len(routes):
            raise ValueError("explorer paths must be unique")
        if tuple(r.navigation_order for r in routes) != tuple(range(len(routes))):
            raise ValueError("navigation_order must be contiguous and deterministic")
        object.__setattr__(self, "routes", routes)

    def by_path(self, path: str) -> EvidenceAuditExplorerRoute:
        normalized = _text(path, "path")
        for route in self.routes:
            if route.path == normalized:
                return route
        raise KeyError(normalized)

    def navigation(self) -> Tuple[Tuple[str, str], ...]:
        return tuple((route.path, route.title) for route in self.routes)


BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_BOUNDARY = EvidenceAuditExplorerBoundary()

BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_ROUTES = (
    EvidenceAuditExplorerRoute("evidence_overview", "/evidence", "Evidence Overview", 0, EvidenceExplorerRole.EVIDENCE_READER, ("registered_evidence_summary", "integrity_state_summary")),
    EvidenceAuditExplorerRoute("evidence_artifacts", "/evidence/artifacts", "Registered Artifacts", 1, EvidenceExplorerRole.EVIDENCE_READER, ("registered_artifact_identity", "registered_path", "content_sha256")),
    EvidenceAuditExplorerRoute("evidence_lineage", "/evidence/lineage", "Correlation Lineage", 2, EvidenceExplorerRole.EVIDENCE_READER, ("correlation_lineage", "provenance_relationships")),
    EvidenceAuditExplorerRoute("evidence_risk", "/evidence/risk", "Risk and Contradictions", 3, EvidenceExplorerRole.EVIDENCE_READER, ("risk_flags", "contradiction_evidence", "ai_evidence")),
    EvidenceAuditExplorerRoute("evidence_validation", "/evidence/validation", "Validation Evidence", 4, EvidenceExplorerRole.EVIDENCE_READER, ("paper_validation", "shadow_observation")),
    EvidenceAuditExplorerRoute("evidence_review", "/evidence/review", "Operator Review Evidence", 5, EvidenceExplorerRole.OPERATOR_REVIEWER, ("operator_review", "governance_evidence")),
    EvidenceAuditExplorerRoute("evidence_archive", "/evidence/archive", "Archive Evidence", 6, EvidenceExplorerRole.AUDIT_READER, ("report_archive", "audit_receipt", "manifest")),
)

EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY = EvidenceAuditExplorerRouteRegistry(
    "fcf.browser_console.evidence_audit.routes.v1",
    BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_ROUTES,
)


@dataclass(frozen=True)
class EvidenceAuditExplorerContract:
    schema_version: str
    boundary: EvidenceAuditExplorerBoundary
    route_registry: EvidenceAuditExplorerRouteRegistry
    allowed_http_methods: Tuple[str, ...]
    allowed_query_parameters: Tuple[str, ...]

    def __post_init__(self) -> None:
        if self.schema_version != "fcf.browser_console.evidence_audit.contract.v1":
            raise ValueError("unsupported explorer contract schema")
        methods = tuple(_text(item, "method").upper() for item in self.allowed_http_methods)
        if methods != ("GET", "HEAD"):
            raise ValueError("explorer methods must remain GET and HEAD")
        expected = (
            "artifact_ids", "artifact_types", "contradiction_codes",
            "correlation_id", "integrity_states", "limit", "offset",
            "risk_flags", "sort_order",
        )
        parameters = tuple(sorted(_text(item, "query_parameter") for item in self.allowed_query_parameters))
        if parameters != expected:
            raise ValueError("explorer query parameter contract mismatch")
        if self.boundary != BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_BOUNDARY:
            raise ValueError("explorer boundary authority mismatch")
        if self.route_registry != EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY:
            raise ValueError("explorer route registry mismatch")
        object.__setattr__(self, "allowed_http_methods", methods)
        object.__setattr__(self, "allowed_query_parameters", parameters)


BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_CONTRACT = EvidenceAuditExplorerContract(
    "fcf.browser_console.evidence_audit.contract.v1",
    BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_BOUNDARY,
    EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY,
    ("GET", "HEAD"),
    (
        "correlation_id", "artifact_ids", "artifact_types",
        "integrity_states", "risk_flags", "contradiction_codes",
        "offset", "limit", "sort_order",
    ),
)
