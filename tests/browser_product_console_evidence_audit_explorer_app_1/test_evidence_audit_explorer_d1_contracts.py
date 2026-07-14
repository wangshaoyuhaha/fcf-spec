import pytest

from apps.browser_product_console_runtime_app_1 import (
    BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_BOUNDARY,
    BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_CONTRACT,
    BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_ROUTES,
    EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY,
    REQUIRED_RESEARCH_WORKSPACE_PATHS,
    EvidenceArtifactNode,
    EvidenceAuditExplorerBoundary,
    EvidenceAuditExplorerRoute,
    EvidenceAuditExplorerRouteRegistry,
    EvidenceAuditQuery,
    EvidenceExplorerRole,
    EvidenceIntegrityState,
    EvidenceRelation,
    EvidenceRelationship,
)


def test_d1_boundary_is_read_only_and_fail_closed():
    boundary = BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_BOUNDARY
    assert boundary.paper_only
    assert boundary.local_only
    assert boundary.loopback_only
    assert boundary.registered_artifact_only
    assert boundary.read_only_presentation
    assert boundary.operator_review_required
    assert boundary.registered_evidence_authority
    assert boundary.ai_advisory_only
    assert not boundary.evidence_mutation_allowed
    assert not boundary.command_dispatch_allowed
    assert not boundary.external_data_fetch_allowed
    assert not boundary.real_execution_allowed


@pytest.mark.parametrize(
    "name",
    (
        "evidence_mutation_allowed",
        "source_artifact_mutation_allowed",
        "record_deletion_allowed",
        "command_dispatch_allowed",
        "workflow_dispatch_allowed",
        "external_data_fetch_allowed",
        "external_network_binding_allowed",
        "automatic_approval_allowed",
        "automatic_promotion_allowed",
        "automatic_baseline_replacement_allowed",
        "automatic_model_activation_allowed",
        "automatic_prompt_activation_allowed",
        "automatic_learning_activation_allowed",
        "automatic_archive_allowed",
        "real_execution_allowed",
    ),
)
def test_d1_boundary_rejects_prohibited_capability(name):
    with pytest.raises(ValueError, match="prohibited explorer"):
        EvidenceAuditExplorerBoundary(**{name: True})


def test_d1_routes_are_exact_and_deterministic():
    assert tuple(route.path for route in BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_ROUTES) == (
        "/evidence",
        "/evidence/artifacts",
        "/evidence/lineage",
        "/evidence/risk",
        "/evidence/validation",
        "/evidence/review",
        "/evidence/archive",
    )
    assert tuple(route.navigation_order for route in BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_ROUTES) == tuple(range(7))
    assert len(EVIDENCE_AUDIT_EXPLORER_ROUTE_REGISTRY.navigation()) == 7


def test_d1_route_rejects_traversal_query_and_duplicate_path():
    for path in (
        "/evidence/../audit",
        "/evidence//risk",
        "/evidence/risk?flag=x",
        "/evidence/risk#fragment",
    ):
        with pytest.raises(ValueError):
            EvidenceAuditExplorerRoute(
                "invalid_route",
                path,
                "Invalid",
                0,
                EvidenceExplorerRole.EVIDENCE_READER,
                ("risk_flags",),
            )
    route = BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_ROUTES[0]
    duplicate_path_route = EvidenceAuditExplorerRoute(
        "duplicate_path",
        route.path,
        "Duplicate Path",
        1,
        EvidenceExplorerRole.EVIDENCE_READER,
        ("registered_evidence_summary",),
    )
    with pytest.raises(ValueError, match="paths must be unique"):
        EvidenceAuditExplorerRouteRegistry(
            "fcf.browser_console.evidence_audit.routes.v1",
            (route, duplicate_path_route),
        )


def test_d1_contract_allows_get_and_head_only():
    contract = BROWSER_PRODUCT_CONSOLE_EVIDENCE_AUDIT_EXPLORER_CONTRACT
    assert contract.allowed_http_methods == ("GET", "HEAD")
    assert contract.allowed_query_parameters == (
        "artifact_ids",
        "artifact_types",
        "contradiction_codes",
        "correlation_id",
        "integrity_states",
        "limit",
        "offset",
        "risk_flags",
        "sort_order",
    )


def test_d1_query_normalizes_deterministically():
    query = EvidenceAuditQuery.from_mapping(
        {
            "correlation_id": "corr-1",
            "artifact_ids": ["artifact-b", "artifact-a"],
            "artifact_types": ["paper_validation", "ai_explanation"],
            "integrity_states": ["TAMPERED", "VERIFIED", "TAMPERED"],
            "risk_flags": ["RISK_B", "RISK_A"],
            "contradiction_codes": ["CONTRA_2", "CONTRA_1"],
            "offset": "10",
            "limit": "25",
            "sort_order": "desc",
        }
    )
    assert query.artifact_ids == ("artifact-a", "artifact-b")
    assert query.artifact_types == ("ai_explanation", "paper_validation")
    assert query.integrity_states == (
        EvidenceIntegrityState.TAMPERED,
        EvidenceIntegrityState.VERIFIED,
    )
    assert query.risk_flags == ("RISK_A", "RISK_B")
    assert query.contradiction_codes == ("CONTRA_1", "CONTRA_2")
    assert query.offset == 10
    assert query.limit == 25
    assert query.sort_order == "DESC"


@pytest.mark.parametrize(
    "values",
    (
        {"execute": "true"},
        {"limit": 0},
        {"limit": 501},
        {"offset": -1},
        {"sort_order": "RANDOM"},
        {"artifact_ids": ["../artifact"]},
    ),
)
def test_d1_query_rejects_unknown_unsafe_or_unbounded_values(values):
    with pytest.raises(ValueError):
        EvidenceAuditQuery.from_mapping(values)


def test_d1_artifact_node_normalizes_and_rejects_tampering_inputs():
    node = EvidenceArtifactNode(
        "artifact-1",
        "ai_explanation",
        "corr-1",
        "registered/artifact-1.json",
        "A" * 64,
        "VERIFIED",
        ("status", "model_name"),
        ("RISK_B", "RISK_A"),
        ("CONTRA_1",),
    )
    assert node.content_sha256 == "a" * 64
    assert node.integrity_state is EvidenceIntegrityState.VERIFIED
    assert node.payload_keys == ("model_name", "status")
    assert node.risk_flags == ("RISK_A", "RISK_B")
    with pytest.raises(ValueError):
        EvidenceArtifactNode(
            "artifact-1",
            "manifest",
            "corr-1",
            "../manifest.json",
            "a" * 64,
            "VERIFIED",
        )
    with pytest.raises(ValueError, match="SHA-256"):
        EvidenceArtifactNode(
            "artifact-1",
            "manifest",
            "corr-1",
            "registered/manifest.json",
            "bad",
            "VERIFIED",
        )


def test_d1_relationship_is_typed_and_rejects_self_link():
    link = EvidenceRelationship(
        "candidate-1",
        "validation-1",
        "VALIDATES",
        "corr-1",
    )
    assert link.relation is EvidenceRelation.VALIDATES
    with pytest.raises(ValueError, match="cannot reference itself"):
        EvidenceRelationship(
            "same-1",
            "same-1",
            "CORRELATES_WITH",
            "corr-1",
        )


def test_d1_existing_workspace_routes_remain_unchanged():
    assert REQUIRED_RESEARCH_WORKSPACE_PATHS == (
        "/",
        "/data",
        "/stocks",
        "/runs",
        "/ai-comparison",
        "/risk",
        "/validation",
        "/review",
        "/reports",
        "/governance",
        "/audit",
    )
