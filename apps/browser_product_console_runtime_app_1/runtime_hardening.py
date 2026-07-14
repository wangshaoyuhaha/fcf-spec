from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Tuple


_ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9_]*$")
_ALLOWED_CATEGORIES = frozenset(
    {"ARTIFACT", "HTTP", "LIFECYCLE", "NETWORK", "RESOURCE"}
)
_ALLOWED_STAGES = frozenset({"D2", "D3", "D4", "D5"})


def _text(value: object, name: str) -> str:
    normalized = str(value).strip()
    if not normalized or "\r" in normalized or "\n" in normalized:
        raise ValueError(
            f"{name} must be non-empty single-line text"
        )
    return normalized


def _integer(
    value: object,
    name: str,
    low: int,
    high: int,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not low <= value <= high:
        raise ValueError(
            f"{name} must be between {low} and {high}"
        )
    return value


def _number(
    value: object,
    name: str,
    low: float,
    high: float,
) -> float:
    if isinstance(value, bool) or not isinstance(
        value,
        (int, float),
    ):
        raise ValueError(f"{name} must be numeric")
    normalized = float(value)
    if not low <= normalized <= high:
        raise ValueError(
            f"{name} must be between {low} and {high}"
        )
    return normalized


@dataclass(frozen=True)
class RuntimeHardeningBoundary:
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
    fail_closed_required: bool = True

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
            self.deterministic_authority,
            self.registered_evidence_authority,
            self.ai_advisory_only,
            self.fail_closed_required,
        )
        if not all(required):
            raise ValueError(
                "runtime hardening authority flags "
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
                "prohibited runtime hardening capability "
                "cannot be enabled"
            )


@dataclass(frozen=True)
class RuntimeHardeningLimits:
    request_target_max_bytes: int = 4096
    header_line_max_bytes: int = 8192
    header_count_max: int = 64
    request_body_max_bytes: int = 0
    socket_timeout_seconds: float = 5.0
    max_concurrent_requests: int = 32
    artifact_max_bytes: int = 16 * 1024 * 1024
    shutdown_timeout_seconds: float = 5.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "request_target_max_bytes",
            _integer(
                self.request_target_max_bytes,
                "request_target_max_bytes",
                256,
                16384,
            ),
        )
        object.__setattr__(
            self,
            "header_line_max_bytes",
            _integer(
                self.header_line_max_bytes,
                "header_line_max_bytes",
                1024,
                16384,
            ),
        )
        object.__setattr__(
            self,
            "header_count_max",
            _integer(
                self.header_count_max,
                "header_count_max",
                8,
                128,
            ),
        )

        if (
            isinstance(self.request_body_max_bytes, bool)
            or self.request_body_max_bytes != 0
        ):
            raise ValueError(
                "request_body_max_bytes must remain zero"
            )

        object.__setattr__(
            self,
            "socket_timeout_seconds",
            _number(
                self.socket_timeout_seconds,
                "socket_timeout_seconds",
                0.1,
                30.0,
            ),
        )
        object.__setattr__(
            self,
            "max_concurrent_requests",
            _integer(
                self.max_concurrent_requests,
                "max_concurrent_requests",
                1,
                128,
            ),
        )
        object.__setattr__(
            self,
            "artifact_max_bytes",
            _integer(
                self.artifact_max_bytes,
                "artifact_max_bytes",
                1024,
                64 * 1024 * 1024,
            ),
        )
        object.__setattr__(
            self,
            "shutdown_timeout_seconds",
            _number(
                self.shutdown_timeout_seconds,
                "shutdown_timeout_seconds",
                0.1,
                30.0,
            ),
        )


@dataclass(frozen=True)
class RuntimeHardeningThreatControl:
    threat_id: str
    category: str
    protected_surface: str
    required_outcome: str
    detection_stage: str

    def __post_init__(self) -> None:
        threat_id = _text(
            self.threat_id,
            "threat_id",
        ).upper()
        category = _text(
            self.category,
            "category",
        ).upper()
        stage = _text(
            self.detection_stage,
            "detection_stage",
        ).upper()

        if not _ID_PATTERN.fullmatch(threat_id):
            raise ValueError(
                "threat_id must be an uppercase identifier"
            )
        if category not in _ALLOWED_CATEGORIES:
            raise ValueError(
                "unsupported threat category"
            )
        if stage not in _ALLOWED_STAGES:
            raise ValueError(
                "unsupported detection stage"
            )

        object.__setattr__(
            self,
            "threat_id",
            threat_id,
        )
        object.__setattr__(
            self,
            "category",
            category,
        )
        object.__setattr__(
            self,
            "protected_surface",
            _text(
                self.protected_surface,
                "protected_surface",
            ),
        )
        object.__setattr__(
            self,
            "required_outcome",
            _text(
                self.required_outcome,
                "required_outcome",
            ),
        )
        object.__setattr__(
            self,
            "detection_stage",
            stage,
        )


_THREAT_ROWS = (
    (
        "NON_LOOPBACK_BIND",
        "NETWORK",
        "server bind address",
        "reject before serving",
        "D2",
    ),
    (
        "INVALID_HOST_HEADER",
        "NETWORK",
        "HTTP Host authority",
        "reject deterministically",
        "D2",
    ),
    (
        "PORT_COLLISION",
        "LIFECYCLE",
        "server startup",
        "fail closed",
        "D2",
    ),
    (
        "MALFORMED_REQUEST_TARGET",
        "HTTP",
        "request target parser",
        "return HTTP 400",
        "D3",
    ),
    (
        "OVERSIZED_REQUEST_TARGET",
        "RESOURCE",
        "request target parser",
        "reject before dispatch",
        "D3",
    ),
    (
        "UNSUPPORTED_HTTP_METHOD",
        "HTTP",
        "application dispatch",
        "return HTTP 405",
        "D3",
    ),
    (
        "REQUEST_BODY_PRESENT",
        "HTTP",
        "read-only request boundary",
        "reject before dispatch",
        "D3",
    ),
    (
        "REQUEST_TIMEOUT",
        "RESOURCE",
        "socket lifecycle",
        "close bounded connection",
        "D3",
    ),
    (
        "CONCURRENCY_LIMIT_EXCEEDED",
        "RESOURCE",
        "request workers",
        "prevent unbounded growth",
        "D3",
    ),
    (
        "PATH_TRAVERSAL",
        "ARTIFACT",
        "registered artifact path",
        "reject outside-root path",
        "D4",
    ),
    (
        "ENCODED_PATH_TRAVERSAL",
        "ARTIFACT",
        "registered artifact path",
        "reject encoded escape",
        "D4",
    ),
    (
        "SYMLINK_ESCAPE",
        "ARTIFACT",
        "registered artifact path",
        "reject symbolic escape",
        "D4",
    ),
    (
        "UNREGISTERED_ARTIFACT",
        "ARTIFACT",
        "artifact loader",
        "reject unregistered source",
        "D4",
    ),
    (
        "ARTIFACT_SIZE_EXCEEDED",
        "RESOURCE",
        "artifact loader",
        "reject oversized artifact",
        "D4",
    ),
    (
        "ARTIFACT_SHA256_MISMATCH",
        "ARTIFACT",
        "evidence integrity",
        "reject tampered artifact",
        "D4",
    ),
    (
        "STARTUP_FAILURE",
        "LIFECYCLE",
        "runtime coordinator",
        "return failed state",
        "D5",
    ),
    (
        "SHUTDOWN_FAILURE",
        "LIFECYCLE",
        "runtime coordinator",
        "return degraded state",
        "D5",
    ),
)

BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_THREATS = tuple(
    RuntimeHardeningThreatControl(*row)
    for row in _THREAT_ROWS
)

REQUIRED_RUNTIME_HARDENING_THREAT_IDS = tuple(
    row[0]
    for row in _THREAT_ROWS
)

BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_BOUNDARY = (
    RuntimeHardeningBoundary()
)

BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS = (
    RuntimeHardeningLimits()
)


@dataclass(frozen=True)
class RuntimeHardeningContract:
    app_id: str
    stage_id: str
    schema_version: str
    status: str
    boundary: RuntimeHardeningBoundary
    limits: RuntimeHardeningLimits
    allowed_http_methods: Tuple[str, ...]
    required_security_headers: Tuple[
        Tuple[str, str],
        ...,
    ]
    threat_controls: Tuple[
        RuntimeHardeningThreatControl,
        ...,
    ]
    successor_phase: str
    runtime_behavior_modified: bool = False
    new_product_capability_added: bool = False

    def __post_init__(self) -> None:
        if self.app_id != (
            "BROWSER-PRODUCT-CONSOLE-"
            "RUNTIME-HARDENING-APP-1"
        ):
            raise ValueError(
                "unexpected runtime hardening app_id"
            )

        if self.stage_id != (
            "BROWSER-PRODUCT-CONSOLE-"
            "RUNTIME-HARDENING-D1"
        ):
            raise ValueError(
                "unexpected runtime hardening stage_id"
            )

        if self.schema_version != (
            "fcf.browser_console."
            "runtime_hardening.contract.v1"
        ):
            raise ValueError(
                "unsupported runtime hardening contract schema"
            )

        if self.status != "IMPLEMENTED":
            raise ValueError(
                "runtime hardening D1 status "
                "must be IMPLEMENTED"
            )

        if not isinstance(
            self.boundary,
            RuntimeHardeningBoundary,
        ):
            raise ValueError(
                "invalid runtime hardening boundary"
            )

        if not isinstance(
            self.limits,
            RuntimeHardeningLimits,
        ):
            raise ValueError(
                "invalid runtime hardening limits"
            )

        if self.allowed_http_methods != (
            "GET",
            "HEAD",
        ):
            raise ValueError(
                "runtime hardening permits GET and HEAD only"
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

        threat_ids = tuple(
            control.threat_id
            for control in self.threat_controls
        )

        if threat_ids != (
            REQUIRED_RUNTIME_HARDENING_THREAT_IDS
        ):
            raise ValueError(
                "runtime hardening threat controls changed"
            )

        if len(set(threat_ids)) != len(threat_ids):
            raise ValueError(
                "runtime hardening threat IDs must be unique"
            )

        if self.successor_phase != (
            "BROWSER-PRODUCT-CONSOLE-"
            "INTEGRATION-ACCEPTANCE-APP-1"
        ):
            raise ValueError(
                "unexpected successor phase"
            )

        if self.runtime_behavior_modified:
            raise ValueError(
                "D1 must not modify runtime behavior"
            )

        if self.new_product_capability_added:
            raise ValueError(
                "D1 must not add product capability"
            )


BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_CONTRACT = (
    RuntimeHardeningContract(
        app_id=(
            "BROWSER-PRODUCT-CONSOLE-"
            "RUNTIME-HARDENING-APP-1"
        ),
        stage_id=(
            "BROWSER-PRODUCT-CONSOLE-"
            "RUNTIME-HARDENING-D1"
        ),
        schema_version=(
            "fcf.browser_console."
            "runtime_hardening.contract.v1"
        ),
        status="IMPLEMENTED",
        boundary=(
            BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_BOUNDARY
        ),
        limits=(
            BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
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
        threat_controls=(
            BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_THREATS
        ),
        successor_phase=(
            "BROWSER-PRODUCT-CONSOLE-"
            "INTEGRATION-ACCEPTANCE-APP-1"
        ),
    )
)
