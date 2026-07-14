from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Tuple


_WORKSPACE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


def _require_text(value: object, field_name: str) -> str:
    normalized = str(value).strip()
    if not normalized:
        raise ValueError(f"{field_name} is required")
    return normalized


class WorkspaceRole(str, Enum):
    RESEARCH_READER = "RESEARCH_READER"
    EVIDENCE_REVIEWER = "EVIDENCE_REVIEWER"
    OPERATOR_REVIEWER = "OPERATOR_REVIEWER"
    GOVERNANCE_REVIEWER = "GOVERNANCE_REVIEWER"
    AUDIT_READER = "AUDIT_READER"


@dataclass(frozen=True)
class ResearchWorkspaceBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_authority: bool = True
    ai_advisory_only: bool = True
    route_mutation_allowed: bool = False
    source_mutation_allowed: bool = False
    command_dispatch_allowed: bool = False
    external_navigation_allowed: bool = False
    external_data_fetch_allowed: bool = False
    role_based_execution_authority_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
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
            self.ai_advisory_only,
        )
        if not all(required):
            raise ValueError(
                "research workspace authority flags must remain enabled"
            )

        prohibited = (
            self.route_mutation_allowed,
            self.source_mutation_allowed,
            self.command_dispatch_allowed,
            self.external_navigation_allowed,
            self.external_data_fetch_allowed,
            self.role_based_execution_authority_allowed,
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_learning_activation_allowed,
            self.automatic_archive_allowed,
            self.real_execution_allowed,
        )
        if any(prohibited):
            raise ValueError(
                "prohibited research workspace capability cannot be enabled"
            )


@dataclass(frozen=True)
class ResearchWorkspaceRoute:
    workspace_id: str
    path: str
    title: str
    navigation_order: int
    role: WorkspaceRole
    source_capabilities: Tuple[str, ...]
    existing_runtime_route: bool
    read_only: bool = True
    operator_review_required: bool = True
    ai_advisory_only: bool = True

    def __post_init__(self) -> None:
        workspace_id = _require_text(self.workspace_id, "workspace_id")
        if not _WORKSPACE_ID_PATTERN.fullmatch(workspace_id):
            raise ValueError("workspace_id must use lower snake case")

        path = _require_text(self.path, "path")
        if not path.startswith("/"):
            raise ValueError("workspace path must be absolute")
        if path != "/" and path.endswith("/"):
            raise ValueError("workspace path must not end with /")
        if any(token in path for token in ("?", "#", "..", "//")):
            raise ValueError("workspace path contains a prohibited token")

        title = _require_text(self.title, "title")
        order = int(self.navigation_order)
        if order < 0:
            raise ValueError("navigation_order must be non-negative")

        try:
            role = (
                self.role
                if isinstance(self.role, WorkspaceRole)
                else WorkspaceRole(str(self.role))
            )
        except ValueError as exc:
            raise ValueError("unsupported workspace role") from exc

        capabilities = tuple(
            _require_text(item, "source_capability")
            for item in self.source_capabilities
        )
        if not capabilities:
            raise ValueError("source_capabilities must not be empty")
        if len(set(capabilities)) != len(capabilities):
            raise ValueError("source_capabilities must be unique")

        if not isinstance(self.existing_runtime_route, bool):
            raise ValueError("existing_runtime_route must be boolean")
        if not self.read_only:
            raise ValueError("workspace route must remain read-only")
        if not self.operator_review_required:
            raise ValueError("workspace route must require Operator review")
        if not self.ai_advisory_only:
            raise ValueError("workspace route must keep AI advisory-only")

        object.__setattr__(self, "workspace_id", workspace_id)
        object.__setattr__(self, "path", path)
        object.__setattr__(self, "title", title)
        object.__setattr__(self, "navigation_order", order)
        object.__setattr__(self, "role", role)
        object.__setattr__(self, "source_capabilities", capabilities)


@dataclass(frozen=True)
class ResearchWorkspaceRouteRegistry:
    schema_version: str
    routes: Tuple[ResearchWorkspaceRoute, ...]

    def __post_init__(self) -> None:
        if (
            self.schema_version
            != "fcf.browser_console.research_workspace.routes.v1"
        ):
            raise ValueError("unsupported research workspace route schema")

        routes = tuple(self.routes)
        if not routes:
            raise ValueError("research workspace route registry is empty")

        workspace_ids = tuple(route.workspace_id for route in routes)
        paths = tuple(route.path for route in routes)
        orders = tuple(route.navigation_order for route in routes)

        if len(set(workspace_ids)) != len(workspace_ids):
            raise ValueError("workspace_id values must be unique")
        if len(set(paths)) != len(paths):
            raise ValueError("workspace paths must be unique")
        if orders != tuple(range(len(routes))):
            raise ValueError(
                "navigation_order must be contiguous and deterministic"
            )

        object.__setattr__(self, "routes", routes)

    def by_path(self, path: str) -> ResearchWorkspaceRoute:
        normalized = _require_text(path, "path")
        for route in self.routes:
            if route.path == normalized:
                return route
        raise KeyError(normalized)

    def by_role(
        self,
        role: WorkspaceRole,
    ) -> Tuple[ResearchWorkspaceRoute, ...]:
        normalized = (
            role
            if isinstance(role, WorkspaceRole)
            else WorkspaceRole(str(role))
        )
        return tuple(route for route in self.routes if route.role == normalized)

    def navigation(self) -> Tuple[Tuple[str, str], ...]:
        return tuple((route.path, route.title) for route in self.routes)


BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_BOUNDARY = (
    ResearchWorkspaceBoundary()
)


BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_ROUTES = (
    ResearchWorkspaceRoute(
        workspace_id="overview",
        path="/",
        title="Overview",
        navigation_order=0,
        role=WorkspaceRole.RESEARCH_READER,
        source_capabilities=("registered_artifact_index",),
        existing_runtime_route=True,
    ),
    ResearchWorkspaceRoute(
        workspace_id="data_workspace",
        path="/data",
        title="Data Workspace",
        navigation_order=1,
        role=WorkspaceRole.RESEARCH_READER,
        source_capabilities=("data_snapshot", "data_quality"),
        existing_runtime_route=False,
    ),
    ResearchWorkspaceRoute(
        workspace_id="stock_candidates",
        path="/stocks",
        title="Stock Candidates",
        navigation_order=2,
        role=WorkspaceRole.RESEARCH_READER,
        source_capabilities=("ranked_watchlist",),
        existing_runtime_route=True,
    ),
    ResearchWorkspaceRoute(
        workspace_id="research_runs",
        path="/runs",
        title="Research Runs",
        navigation_order=3,
        role=WorkspaceRole.RESEARCH_READER,
        source_capabilities=("research_run", "workflow_status"),
        existing_runtime_route=False,
    ),
    ResearchWorkspaceRoute(
        workspace_id="ai_comparison",
        path="/ai-comparison",
        title="AI Comparison",
        navigation_order=4,
        role=WorkspaceRole.RESEARCH_READER,
        source_capabilities=("ai_explanation", "ai_evaluation"),
        existing_runtime_route=False,
    ),
    ResearchWorkspaceRoute(
        workspace_id="evidence_and_risk",
        path="/risk",
        title="Evidence and Risk",
        navigation_order=5,
        role=WorkspaceRole.EVIDENCE_REVIEWER,
        source_capabilities=("risk_flags", "contradiction_evidence"),
        existing_runtime_route=True,
    ),
    ResearchWorkspaceRoute(
        workspace_id="paper_and_shadow_validation",
        path="/validation",
        title="Paper and Shadow Validation",
        navigation_order=6,
        role=WorkspaceRole.EVIDENCE_REVIEWER,
        source_capabilities=("paper_validation", "shadow_observation"),
        existing_runtime_route=True,
    ),
    ResearchWorkspaceRoute(
        workspace_id="operator_review",
        path="/review",
        title="Operator Review",
        navigation_order=7,
        role=WorkspaceRole.OPERATOR_REVIEWER,
        source_capabilities=("operator_review",),
        existing_runtime_route=True,
    ),
    ResearchWorkspaceRoute(
        workspace_id="reports_and_archive",
        path="/reports",
        title="Reports and Archive",
        navigation_order=8,
        role=WorkspaceRole.AUDIT_READER,
        source_capabilities=("report_archive",),
        existing_runtime_route=True,
    ),
    ResearchWorkspaceRoute(
        workspace_id="governance",
        path="/governance",
        title="Governance",
        navigation_order=9,
        role=WorkspaceRole.GOVERNANCE_REVIEWER,
        source_capabilities=("model_governance", "policy_snapshot"),
        existing_runtime_route=False,
    ),
    ResearchWorkspaceRoute(
        workspace_id="audit_history",
        path="/audit",
        title="Audit History",
        navigation_order=10,
        role=WorkspaceRole.AUDIT_READER,
        source_capabilities=("audit_receipt", "manifest"),
        existing_runtime_route=False,
    ),
)


RESEARCH_WORKSPACE_ROUTE_REGISTRY = ResearchWorkspaceRouteRegistry(
    schema_version="fcf.browser_console.research_workspace.routes.v1",
    routes=BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_ROUTES,
)


@dataclass(frozen=True)
class ResearchWorkspaceContract:
    schema_version: str
    boundary: ResearchWorkspaceBoundary
    route_registry: ResearchWorkspaceRouteRegistry
    allowed_http_methods: Tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.schema_version
            != "fcf.browser_console.research_workspace.contract.v1"
        ):
            raise ValueError("unsupported research workspace contract schema")
        methods = tuple(
            _require_text(method, "allowed_http_method").upper()
            for method in self.allowed_http_methods
        )
        if methods != ("GET", "HEAD"):
            raise ValueError(
                "research workspace methods must remain GET and HEAD"
            )
        if self.boundary != (
            BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_BOUNDARY
        ):
            raise ValueError("research workspace boundary authority mismatch")
        if self.route_registry != RESEARCH_WORKSPACE_ROUTE_REGISTRY:
            raise ValueError("research workspace route registry mismatch")
        object.__setattr__(self, "allowed_http_methods", methods)


BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_CONTRACT = (
    ResearchWorkspaceContract(
        schema_version=(
            "fcf.browser_console.research_workspace.contract.v1"
        ),
        boundary=BROWSER_PRODUCT_CONSOLE_RESEARCH_WORKSPACE_BOUNDARY,
        route_registry=RESEARCH_WORKSPACE_ROUTE_REGISTRY,
        allowed_http_methods=("GET", "HEAD"),
    )
)
