from __future__ import annotations

import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from .evidence_audit_explorer import (
    EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY,
)
from .evidence_audit_graph import (
    build_evidence_artifact_graph,
)
from .web_console import (
    BrowserProductConsoleApplication,
    ConsoleResponse,
)


REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS = (
    "/evidence",
    "/evidence/artifacts",
    "/evidence/lineage",
    "/evidence/risk",
    "/evidence/validation",
    "/evidence/review",
    "/evidence/archive",
)
EVIDENCE_AUDIT_UNSAFE_HTTP_METHODS = (
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
)


@dataclass(frozen=True)
class EvidenceAuditExplorerIntegrationAcceptance:
    status: str
    ok: bool
    route_paths: Tuple[str, ...]
    checks: Mapping[str, bool]
    get_statuses: Mapping[str, int]
    head_statuses: Mapping[str, int]
    write_statuses: Mapping[str, int]
    rejected_query_statuses: Mapping[str, int]
    health_payload: Mapping[str, object]
    paper_only: bool = True
    loopback_only: bool = True
    registered_artifact_only: bool = True
    read_only: bool = True
    operator_review_required: bool = True
    ai_advisory_only: bool = True
    deterministic_engine_authority: bool = True

    def __post_init__(self) -> None:
        if self.status not in {"PASSED", "REJECTED"}:
            raise ValueError(
                "unsupported Evidence Audit integration status"
            )
        if self.ok != (self.status == "PASSED"):
            raise ValueError("status and ok must agree")
        if not self.paper_only or not self.loopback_only:
            raise ValueError(
                "Evidence Audit integration must remain "
                "local paper-only"
            )
        if not self.registered_artifact_only or not self.read_only:
            raise ValueError(
                "Evidence Audit integration must remain "
                "registered-artifact-only and read-only"
            )
        if not self.operator_review_required:
            raise ValueError(
                "Operator review must remain required"
            )
        if not self.ai_advisory_only:
            raise ValueError("AI must remain advisory-only")
        if not self.deterministic_engine_authority:
            raise ValueError(
                "Deterministic Engine authority must remain enabled"
            )

        object.__setattr__(
            self,
            "route_paths",
            tuple(self.route_paths),
        )
        for field_name in (
            "checks",
            "get_statuses",
            "head_statuses",
            "write_statuses",
            "rejected_query_statuses",
            "health_payload",
        ):
            object.__setattr__(
                self,
                field_name,
                MappingProxyType(
                    dict(getattr(self, field_name))
                ),
            )


def _headers(
    response: ConsoleResponse,
) -> Mapping[str, str]:
    return MappingProxyType(dict(response.headers))


def _navigation_is_complete(body: bytes) -> bool:
    document = body.decode("utf-8")
    return all(
        document.count(f'href="{path}"') == 1
        for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS
    )


def _contains_mutating_controls(body: bytes) -> bool:
    document = body.decode("utf-8").lower()
    return any(
        marker in document
        for marker in (
            "<form",
            "<button",
            "method=",
            "<script",
        )
    )


def build_evidence_audit_explorer_integration_acceptance(
    application: BrowserProductConsoleApplication,
) -> EvidenceAuditExplorerIntegrationAcceptance:
    route_paths = tuple(
        route.path
        for route in (
            EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY.routes
        )
    )
    get_responses = {
        path: application.dispatch("GET", path)
        for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS
    }
    head_responses = {
        path: application.dispatch("HEAD", path)
        for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS
    }
    write_responses = {
        f"{method} {path}": application.dispatch(
            method,
            path,
        )
        for method in EVIDENCE_AUDIT_UNSAFE_HTTP_METHODS
        for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS
    }

    rejected_queries = (
        "/evidence?execute=true",
        "/evidence?limit=0",
        "/evidence?limit=1&limit=2",
        "/evidence?artifact_ids=",
        "/evidence?artifact_ids=%ZZ",
    )
    rejected_query_responses = {
        query: application.dispatch("GET", query)
        for query in rejected_queries
    }

    valid_query_path = (
        "/evidence/artifacts"
        "?artifact_types=manifest"
        "&limit=10"
        "&sort_order=ASC"
    )
    valid_query_response = application.dispatch(
        "GET",
        valid_query_path,
    )
    deterministic_query_response = application.dispatch(
        "GET",
        valid_query_path,
    )

    unknown_response = application.dispatch(
        "GET",
        "/evidence/not-registered",
    )
    traversal_response = application.dispatch(
        "GET",
        "/evidence/../audit",
    )
    encoded_traversal_response = application.dispatch(
        "GET",
        "/evidence/%2e%2e/audit",
    )

    health_response = application.dispatch("GET", "/health")
    try:
        health_payload = json.loads(
            health_response.body.decode("utf-8")
        )
    except (UnicodeDecodeError, json.JSONDecodeError):
        health_payload = {}

    graph = build_evidence_artifact_graph(
        application.read_model
    )
    record_ids = tuple(
        sorted(
            record.artifact_id
            for record in application.read_model.artifact_records
        )
    )
    graph_ids = tuple(
        sorted(node.artifact_id for node in graph.nodes)
    )

    get_headers = {
        path: _headers(response)
        for path, response in get_responses.items()
    }

    checks = {
        "route_registry_exact": (
            route_paths
            == REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS
        ),
        "route_registry_unique": (
            len(route_paths) == len(set(route_paths))
        ),
        "all_get_200": all(
            response.status == 200
            for response in get_responses.values()
        ),
        "all_head_200_empty": all(
            response.status == 200
            and response.body == b""
            for response in head_responses.values()
        ),
        "all_write_methods_rejected": all(
            response.status == 405
            for response in write_responses.values()
        ),
        "invalid_queries_rejected": all(
            response.status == 400
            for response in rejected_query_responses.values()
        ),
        "valid_query_accepted": (
            valid_query_response.status == 200
        ),
        "valid_query_deterministic": (
            valid_query_response.body
            == deterministic_query_response.body
        ),
        "unknown_route_rejected": (
            unknown_response.status == 404
        ),
        "plain_traversal_rejected": (
            traversal_response.status == 404
        ),
        "encoded_traversal_rejected": (
            encoded_traversal_response.status == 404
        ),
        "health_status_ok": health_response.status == 200,
        "health_paper_only": (
            health_payload.get("mode") == "paper-only"
        ),
        "health_loopback_only": (
            health_payload.get("host_scope") == "loopback-only"
        ),
        "health_operator_review_required": (
            health_payload.get(
                "operator_review_required"
            )
            is True
        ),
        "registered_artifact_identity_exact": (
            graph_ids == record_ids
        ),
        "registered_sha256_visible": all(
            len(node.content_sha256) == 64
            for node in graph.nodes
        ),
        "graph_registered_artifact_only": (
            graph.registered_artifact_only
            and graph.read_only
        ),
        "security_cache_control": all(
            headers.get("Cache-Control") == "no-store"
            for headers in get_headers.values()
        ),
        "security_content_type_options": all(
            headers.get("X-Content-Type-Options")
            == "nosniff"
            for headers in get_headers.values()
        ),
        "security_content_policy": all(
            headers.get("Content-Security-Policy")
            == "default-src 'self'; style-src 'unsafe-inline'"
            for headers in get_headers.values()
        ),
        "navigation_complete": all(
            _navigation_is_complete(response.body)
            for response in get_responses.values()
        ),
        "no_mutating_controls": all(
            not _contains_mutating_controls(response.body)
            for response in get_responses.values()
        ),
        "head_headers_match_get": all(
            head_responses[path].headers
            == get_responses[path].headers
            for path in REQUIRED_EVIDENCE_AUDIT_EXPLORER_PATHS
        ),
    }

    ok = all(checks.values())
    return EvidenceAuditExplorerIntegrationAcceptance(
        status="PASSED" if ok else "REJECTED",
        ok=ok,
        route_paths=route_paths,
        checks=checks,
        get_statuses={
            path: response.status
            for path, response in get_responses.items()
        },
        head_statuses={
            path: response.status
            for path, response in head_responses.items()
        },
        write_statuses={
            key: response.status
            for key, response in write_responses.items()
        },
        rejected_query_statuses={
            key: response.status
            for key, response in (
                rejected_query_responses.items()
            )
        },
        health_payload=health_payload,
    )
