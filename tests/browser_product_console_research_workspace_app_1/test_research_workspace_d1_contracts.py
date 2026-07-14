from dataclasses import replace

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_BOUNDARY,
    BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_CONTRACT,
    BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_ROUTES,
    RESEARCH_WORKSPACE_ROUTE_REGISTRY,
    ResearchWorkspaceRoute,
    ResearchWorkspaceRouteRegistry,
    WorkspaceRole,
)


def test_d1_workspace_boundary_preserves_authority():
    boundary = BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_BOUNDARY

    assert boundary.paper_only is True
    assert boundary.local_only is True
    assert boundary.loopback_only is True
    assert boundary.registered_artifact_only is True
    assert boundary.read_only_presentation is True
    assert boundary.operator_review_required is True
    assert boundary.deterministic_authority is True
    assert boundary.ai_advisory_only is True


def test_d1_workspace_boundary_rejects_write_capability():
    with pytest.raises(
        ValueError,
        match="prohibited research workspace capability",
    ):
        replace(
            BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_BOUNDARY,
            source_mutation_allowed=True,
        )


def test_d1_workspace_roles_do_not_grant_execution_authority():
    boundary = BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_BOUNDARY

    assert boundary.role_based_execution_authority_allowed is False
    assert boundary.command_dispatch_allowed is False
    assert boundary.real_execution_allowed is False


def test_d1_contract_allows_only_get_and_head():
    contract = BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_CONTRACT

    assert contract.allowed_http_methods == ("GET", "HEAD")
    assert contract.route_registry is RESEARCH_WORKSPACE_ROUTE_REGISTRY


def test_d1_route_order_is_complete_and_deterministic():
    routes = BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_ROUTES

    assert tuple(route.navigation_order for route in routes) == tuple(
        range(11)
    )
    assert tuple(route.path for route in routes) == (
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


def test_d1_existing_runtime_routes_are_preserved():
    existing_paths = tuple(
        route.path
        for route in BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_ROUTES
        if route.existing_runtime_route
    )

    assert existing_paths == (
        "/",
        "/stocks",
        "/risk",
        "/validation",
        "/review",
        "/reports",
    )


def test_d1_route_lookup_and_navigation_are_deterministic():
    route = RESEARCH_WORKSPACE_ROUTE_REGISTRY.by_path("/data")

    assert route.workspace_id == "data_workspace"
    assert route.role is WorkspaceRole.RESEARCH_READER
    assert RESEARCH_WORKSPACE_ROUTE_REGISTRY.navigation()[0] == (
        "/",
        "Overview",
    )


def test_d1_role_filter_preserves_registry_order():
    audit_routes = RESEARCH_WORKSPACE_ROUTE_REGISTRY.by_role(
        WorkspaceRole.AUDIT_READER
    )

    assert tuple(route.path for route in audit_routes) == (
        "/reports",
        "/audit",
    )


def test_d1_unknown_route_is_rejected():
    with pytest.raises(KeyError):
        RESEARCH_WORKSPACE_ROUTE_REGISTRY.by_path("/unknown")


def test_d1_route_rejects_non_read_only_configuration():
    with pytest.raises(ValueError, match="must remain read-only"):
        ResearchWorkspaceRoute(
            workspace_id="invalid_workspace",
            path="/invalid",
            title="Invalid",
            navigation_order=0,
            role=WorkspaceRole.RESEARCH_READER,
            source_capabilities=("registered_artifact_index",),
            existing_runtime_route=False,
            read_only=False,
        )


def test_d1_route_rejects_query_or_traversal_tokens():
    with pytest.raises(ValueError, match="prohibited token"):
        ResearchWorkspaceRoute(
            workspace_id="invalid_workspace",
            path="/invalid?write=true",
            title="Invalid",
            navigation_order=0,
            role=WorkspaceRole.RESEARCH_READER,
            source_capabilities=("registered_artifact_index",),
            existing_runtime_route=False,
        )


def test_d1_registry_rejects_duplicate_paths():
    first = BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_ROUTES[0]
    duplicate = replace(
        BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_ROUTES[1],
        path="/",
    )

    with pytest.raises(ValueError, match="workspace paths must be unique"):
        ResearchWorkspaceRouteRegistry(
            schema_version=(
                "fcf.browser_console.research_workspace.routes.v1"
            ),
            routes=(first, duplicate),
        )
