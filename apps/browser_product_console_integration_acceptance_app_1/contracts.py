from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Tuple


_IDENTIFIER_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
_ALLOWED_LAYERS = frozenset(
    {
        "EVIDENCE",
        "OPERATOR",
        "PRODUCT",
        "RUNTIME",
        "WORKSPACE",
    }
)
_ALLOWED_STAGES = frozenset({"D2", "D3", "D4", "D5"})
_ALLOWED_SOURCE_KINDS = frozenset(
    {
        "DETERMINISTIC_MODEL",
        "REGISTERED_ARTIFACT",
        "RUNTIME_PROBE",
        "STATIC_CONTRACT",
    }
)


def _single_line_text(
    value: object,
    name: str,
) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be text")

    normalized = value.strip()

    if (
        not normalized
        or normalized != value
        or "\r" in normalized
        or "\n" in normalized
    ):
        raise ValueError(
            f"{name} must be non-empty normalized single-line text"
        )

    return normalized


def _identifier(
    value: object,
    name: str,
) -> str:
    normalized = _single_line_text(
        value,
        name,
    ).upper()

    if not _IDENTIFIER_PATTERN.fullmatch(normalized):
        raise ValueError(
            f"{name} must be an uppercase identifier"
        )

    return normalized


def _text_tuple(
    values: object,
    name: str,
) -> Tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise ValueError(f"{name} must be a tuple of text")

    try:
        normalized = tuple(
            _single_line_text(item, name)
            for item in values
        )
    except TypeError as exc:
        raise ValueError(
            f"{name} must be iterable"
        ) from exc

    if not normalized:
        raise ValueError(f"{name} must not be empty")

    if len(set(normalized)) != len(normalized):
        raise ValueError(
            f"{name} must not contain duplicates"
        )

    return normalized


@dataclass(frozen=True)
class IntegrationAcceptanceBoundary:
    paper_only: bool = True
    local_only: bool = True
    loopback_only: bool = True
    sidecar_only: bool = True
    registered_artifact_only: bool = True
    read_only_presentation: bool = True
    operator_review_required: bool = True
    deterministic_engine_authority: bool = True
    registered_evidence_authority: bool = True
    ai_advisory_only: bool = True
    reproducibility_required: bool = True
    generated_output_restoration_required: bool = True

    core_mutation_allowed: bool = False
    p48_creation_allowed: bool = False
    product_capability_expansion_allowed: bool = False
    evidence_mutation_allowed: bool = False
    source_artifact_mutation_allowed: bool = False
    record_deletion_allowed: bool = False
    command_dispatch_allowed: bool = False
    workflow_dispatch_allowed: bool = False
    external_data_fetch_allowed: bool = False
    external_network_binding_allowed: bool = False
    remote_browser_access_allowed: bool = False
    credential_access_allowed: bool = False
    broker_or_exchange_connection_allowed: bool = False
    account_balance_position_wallet_access_allowed: bool = False
    order_path_allowed: bool = False
    real_execution_allowed: bool = False
    automatic_approval_allowed: bool = False
    automatic_promotion_allowed: bool = False
    automatic_baseline_replacement_allowed: bool = False
    automatic_model_activation_allowed: bool = False
    automatic_prompt_activation_allowed: bool = False
    automatic_learning_activation_allowed: bool = False
    automatic_archive_allowed: bool = False

    def __post_init__(self) -> None:
        required = (
            self.paper_only,
            self.local_only,
            self.loopback_only,
            self.sidecar_only,
            self.registered_artifact_only,
            self.read_only_presentation,
            self.operator_review_required,
            self.deterministic_engine_authority,
            self.registered_evidence_authority,
            self.ai_advisory_only,
            self.reproducibility_required,
            self.generated_output_restoration_required,
        )

        if not all(required):
            raise ValueError(
                "integration acceptance authority flags "
                "must remain enabled"
            )

        prohibited = (
            self.core_mutation_allowed,
            self.p48_creation_allowed,
            self.product_capability_expansion_allowed,
            self.evidence_mutation_allowed,
            self.source_artifact_mutation_allowed,
            self.record_deletion_allowed,
            self.command_dispatch_allowed,
            self.workflow_dispatch_allowed,
            self.external_data_fetch_allowed,
            self.external_network_binding_allowed,
            self.remote_browser_access_allowed,
            self.credential_access_allowed,
            self.broker_or_exchange_connection_allowed,
            self.account_balance_position_wallet_access_allowed,
            self.order_path_allowed,
            self.real_execution_allowed,
            self.automatic_approval_allowed,
            self.automatic_promotion_allowed,
            self.automatic_baseline_replacement_allowed,
            self.automatic_model_activation_allowed,
            self.automatic_prompt_activation_allowed,
            self.automatic_learning_activation_allowed,
            self.automatic_archive_allowed,
        )

        if any(prohibited):
            raise ValueError(
                "prohibited integration acceptance capability "
                "cannot be enabled"
            )


@dataclass(frozen=True)
class IntegrationAcceptanceMatrixRow:
    matrix_id: str
    layer: str
    subject: str
    acceptance_dimensions: Tuple[str, ...]
    delivery_stage: str

    def __post_init__(self) -> None:
        matrix_id = _identifier(
            self.matrix_id,
            "matrix_id",
        )
        layer = _identifier(
            self.layer,
            "layer",
        )
        delivery_stage = _identifier(
            self.delivery_stage,
            "delivery_stage",
        )

        if layer not in _ALLOWED_LAYERS:
            raise ValueError(
                "unsupported integration acceptance layer"
            )

        if delivery_stage not in _ALLOWED_STAGES:
            raise ValueError(
                "unsupported integration acceptance stage"
            )

        object.__setattr__(
            self,
            "matrix_id",
            matrix_id,
        )
        object.__setattr__(
            self,
            "layer",
            layer,
        )
        object.__setattr__(
            self,
            "subject",
            _single_line_text(
                self.subject,
                "subject",
            ),
        )
        object.__setattr__(
            self,
            "acceptance_dimensions",
            _text_tuple(
                self.acceptance_dimensions,
                "acceptance_dimensions",
            ),
        )
        object.__setattr__(
            self,
            "delivery_stage",
            delivery_stage,
        )


@dataclass(frozen=True)
class IntegrationAcceptanceFixture:
    fixture_id: str
    source_kind: str
    purpose: str
    required_fields: Tuple[str, ...]
    deterministic: bool = True
    read_only: bool = True
    registered_artifact_only: bool = True
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        fixture_id = _identifier(
            self.fixture_id,
            "fixture_id",
        )
        source_kind = _identifier(
            self.source_kind,
            "source_kind",
        )

        if source_kind not in _ALLOWED_SOURCE_KINDS:
            raise ValueError(
                "unsupported integration acceptance source kind"
            )

        required_flags = (
            self.deterministic,
            self.read_only,
            self.registered_artifact_only,
            self.operator_review_required,
        )

        if not all(required_flags):
            raise ValueError(
                "integration acceptance fixture flags "
                "must remain enabled"
            )

        object.__setattr__(
            self,
            "fixture_id",
            fixture_id,
        )
        object.__setattr__(
            self,
            "source_kind",
            source_kind,
        )
        object.__setattr__(
            self,
            "purpose",
            _single_line_text(
                self.purpose,
                "purpose",
            ),
        )
        object.__setattr__(
            self,
            "required_fields",
            _text_tuple(
                self.required_fields,
                "required_fields",
            ),
        )


_MATRIX_ROWS = (
    (
        "PRODUCT_CONSOLE_ROUTES",
        "PRODUCT",
        "Browser Product Console route surface",
        (
            "GET and HEAD only",
            "read-only navigation",
            "malformed query rejection",
            "unknown route rejection",
            "security header preservation",
        ),
        "D2",
    ),
    (
        "RESEARCH_WORKSPACE",
        "WORKSPACE",
        "Research Workspace product surface",
        (
            "deterministic workspace rendering",
            "registered artifact presentation",
            "risk and contradiction visibility",
            "Operator review visibility",
        ),
        "D2",
    ),
    (
        "EVIDENCE_AUDIT_EXPLORER",
        "EVIDENCE",
        "Evidence Audit Explorer surface",
        (
            "registered artifact identity",
            "relative path and SHA-256 visibility",
            "correlation lineage",
            "typed relationships",
            "unresolved registered reference visibility",
        ),
        "D2",
    ),
    (
        "RUNTIME_SECURITY",
        "RUNTIME",
        "Loopback runtime security boundary",
        (
            "exact loopback binding",
            "Host validation",
            "bounded HTTP parsing",
            "timeout and concurrency limits",
            "write-method rejection",
        ),
        "D3",
    ),
    (
        "RUNTIME_FAULT_ISOLATION",
        "RUNTIME",
        "Runtime fault isolation boundary",
        (
            "deterministic failure codes",
            "sanitized HTTP 500",
            "bounded diagnostics",
            "subsequent service recovery",
        ),
        "D3",
    ),
    (
        "REGISTERED_EVIDENCE_AUTHORITY",
        "EVIDENCE",
        "Registered Evidence authority boundary",
        (
            "registered-artifact-only loading",
            "allowed-root containment",
            "symbolic path rejection",
            "size bounds",
            "SHA-256 verification",
        ),
        "D4",
    ),
    (
        "DETERMINISTIC_ENGINE_AUTHORITY",
        "PRODUCT",
        "Deterministic Engine authority boundary",
        (
            "calculation authority preservation",
            "AI advisory-only preservation",
            "no automatic promotion",
            "reproducible output",
        ),
        "D4",
    ),
    (
        "OPERATOR_ACCEPTANCE",
        "OPERATOR",
        "Operator acceptance package",
        (
            "Operator review mandatory",
            "read-only acceptance evidence",
            "explicit unresolved states",
            "full regression evidence",
        ),
        "D5",
    ),
)

INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX = tuple(
    IntegrationAcceptanceMatrixRow(*row)
    for row in _MATRIX_ROWS
)

REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS = tuple(
    row[0]
    for row in _MATRIX_ROWS
)


_FIXTURE_ROWS = (
    (
        "ROUTE_ACCEPTANCE_FIXTURE",
        "STATIC_CONTRACT",
        "Exercise canonical product routes and method boundaries",
        (
            "route",
            "method",
            "expected_status",
            "expected_security_headers",
        ),
    ),
    (
        "REGISTERED_EVIDENCE_FIXTURE",
        "REGISTERED_ARTIFACT",
        "Exercise registered evidence identity and integrity presentation",
        (
            "artifact_id",
            "relative_path",
            "sha256",
            "correlation_id",
            "relationship_type",
        ),
    ),
    (
        "NEGATIVE_PATH_FIXTURE",
        "RUNTIME_PROBE",
        "Exercise malformed query, traversal, unknown route, and write rejection",
        (
            "request_target",
            "expected_status",
            "expected_fault_code",
        ),
    ),
    (
        "FAULT_ISOLATION_FIXTURE",
        "RUNTIME_PROBE",
        "Exercise deterministic fault isolation and recovery",
        (
            "fault_source",
            "expected_status",
            "expected_diagnostic_code",
            "recovery_probe",
        ),
    ),
    (
        "AUTHORITY_INVARIANT_FIXTURE",
        "DETERMINISTIC_MODEL",
        "Exercise cross-layer authority and reproducibility invariants",
        (
            "deterministic_engine_authority",
            "registered_evidence_authority",
            "operator_review_required",
            "ai_advisory_only",
        ),
    ),
    (
        "OPERATOR_ACCEPTANCE_FIXTURE",
        "STATIC_CONTRACT",
        "Exercise the final read-only Operator acceptance package",
        (
            "acceptance_matrix",
            "validation_summary",
            "unresolved_items",
            "operator_review_required",
        ),
    ),
)

INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY = tuple(
    IntegrationAcceptanceFixture(*row)
    for row in _FIXTURE_ROWS
)

REQUIRED_INTEGRATION_ACCEPTANCE_FIXTURE_IDS = tuple(
    row[0]
    for row in _FIXTURE_ROWS
)


@dataclass(frozen=True)
class IntegrationAcceptanceContract:
    app_id: str
    stage_id: str
    schema_version: str
    status: str
    boundary: IntegrationAcceptanceBoundary
    system_matrix: Tuple[
        IntegrationAcceptanceMatrixRow,
        ...,
    ]
    fixture_registry: Tuple[
        IntegrationAcceptanceFixture,
        ...,
    ]
    allowed_http_methods: Tuple[str, ...]
    required_security_headers: Tuple[
        Tuple[str, str],
        ...,
    ]
    delivery_order: Tuple[str, ...]
    successor_policy: str
    runtime_behavior_modified: bool = False
    product_capability_added: bool = False

    def __post_init__(self) -> None:
        if self.app_id != (
            "BROWSER-PRODUCT-CONSOLE-"
            "INTEGRATION-ACCEPTANCE-APP-1"
        ):
            raise ValueError(
                "unexpected integration acceptance app_id"
            )

        if self.stage_id != (
            "BROWSER-PRODUCT-CONSOLE-"
            "INTEGRATION-ACCEPTANCE-D1"
        ):
            raise ValueError(
                "unexpected integration acceptance stage_id"
            )

        if self.schema_version != (
            "fcf.browser_console."
            "integration_acceptance.contract.v1"
        ):
            raise ValueError(
                "unsupported integration acceptance schema"
            )

        if self.status != "IMPLEMENTED":
            raise ValueError(
                "integration acceptance D1 status "
                "must be IMPLEMENTED"
            )

        if not isinstance(
            self.boundary,
            IntegrationAcceptanceBoundary,
        ):
            raise ValueError(
                "invalid integration acceptance boundary"
            )

        matrix_ids = tuple(
            row.matrix_id
            for row in self.system_matrix
        )

        if matrix_ids != (
            REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS
        ):
            raise ValueError(
                "integration acceptance system matrix changed"
            )

        fixture_ids = tuple(
            fixture.fixture_id
            for fixture in self.fixture_registry
        )

        if fixture_ids != (
            REQUIRED_INTEGRATION_ACCEPTANCE_FIXTURE_IDS
        ):
            raise ValueError(
                "integration acceptance fixture registry changed"
            )

        if self.allowed_http_methods != (
            "GET",
            "HEAD",
        ):
            raise ValueError(
                "integration acceptance permits GET and HEAD only"
            )

        expected_headers = (
            (
                "Cache-Control",
                "no-store",
            ),
            (
                "X-Content-Type-Options",
                "nosniff",
            ),
            (
                "Content-Security-Policy",
                "default-src 'self'; "
                "style-src 'unsafe-inline'",
            ),
        )

        if self.required_security_headers != expected_headers:
            raise ValueError(
                "required security headers changed"
            )

        expected_delivery_order = (
            "D1",
            "D2",
            "D3",
            "D4",
            "D5",
            "D6",
        )

        if self.delivery_order != expected_delivery_order:
            raise ValueError(
                "integration acceptance delivery order changed"
            )

        if self.successor_policy != (
            "NO_SUCCESSOR_APPROVED"
        ):
            raise ValueError(
                "unexpected integration acceptance successor policy"
            )

        if self.runtime_behavior_modified:
            raise ValueError(
                "D1 must not modify runtime behavior"
            )

        if self.product_capability_added:
            raise ValueError(
                "D1 must not add product capability"
            )


BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_BOUNDARY = (
    IntegrationAcceptanceBoundary()
)

BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_CONTRACT = (
    IntegrationAcceptanceContract(
        app_id=(
            "BROWSER-PRODUCT-CONSOLE-"
            "INTEGRATION-ACCEPTANCE-APP-1"
        ),
        stage_id=(
            "BROWSER-PRODUCT-CONSOLE-"
            "INTEGRATION-ACCEPTANCE-D1"
        ),
        schema_version=(
            "fcf.browser_console."
            "integration_acceptance.contract.v1"
        ),
        status="IMPLEMENTED",
        boundary=(
            BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_BOUNDARY
        ),
        system_matrix=(
            INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX
        ),
        fixture_registry=(
            INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY
        ),
        allowed_http_methods=(
            "GET",
            "HEAD",
        ),
        required_security_headers=(
            (
                "Cache-Control",
                "no-store",
            ),
            (
                "X-Content-Type-Options",
                "nosniff",
            ),
            (
                "Content-Security-Policy",
                "default-src 'self'; "
                "style-src 'unsafe-inline'",
            ),
        ),
        delivery_order=(
            "D1",
            "D2",
            "D3",
            "D4",
            "D5",
            "D6",
        ),
        successor_policy=(
            "NO_SUCCESSOR_APPROVED"
        ),
    )
)
