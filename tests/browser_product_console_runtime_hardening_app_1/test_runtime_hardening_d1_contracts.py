from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BROWSER_PRODUCT_CONSOLE_RUNTIME_BOUNDARY,
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_BOUNDARY,
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_CONTRACT,
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS,
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_THREATS,
    REQUIRED_RUNTIME_HARDENING_THREAT_IDS,
    ConsoleRuntimeConfig,
    RuntimeHardeningBoundary,
    RuntimeHardeningContract,
    RuntimeHardeningLimits,
)


def test_d1_boundary_preserves_required_authorities():
    boundary = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_BOUNDARY
    )

    assert boundary.paper_only
    assert boundary.local_only
    assert boundary.loopback_only
    assert boundary.sidecar_only
    assert boundary.registered_artifact_only
    assert boundary.read_only_presentation
    assert boundary.operator_review_required
    assert boundary.deterministic_authority
    assert boundary.registered_evidence_authority
    assert boundary.ai_advisory_only
    assert boundary.fail_closed_required


@pytest.mark.parametrize(
    "field_name",
    (
        "paper_only",
        "local_only",
        "loopback_only",
        "sidecar_only",
        "registered_artifact_only",
        "read_only_presentation",
        "operator_review_required",
        "deterministic_authority",
        "registered_evidence_authority",
        "ai_advisory_only",
        "fail_closed_required",
    ),
)
def test_d1_boundary_rejects_disabled_authority(
    field_name,
):
    with pytest.raises(
        ValueError,
        match="must remain enabled",
    ):
        RuntimeHardeningBoundary(
            **{field_name: False}
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "core_mutation_allowed",
        "p48_creation_allowed",
        "product_capability_expansion_allowed",
        "evidence_mutation_allowed",
        "source_artifact_mutation_allowed",
        "record_deletion_allowed",
        "command_dispatch_allowed",
        "workflow_dispatch_allowed",
        "external_data_fetch_allowed",
        "external_network_binding_allowed",
        "remote_browser_access_allowed",
        "credential_access_allowed",
        "broker_or_exchange_connection_allowed",
        "account_balance_position_wallet_access_allowed",
        "order_path_allowed",
        "real_execution_allowed",
        "automatic_approval_allowed",
        "automatic_promotion_allowed",
        "automatic_baseline_replacement_allowed",
        "automatic_model_activation_allowed",
        "automatic_prompt_activation_allowed",
        "automatic_learning_activation_allowed",
        "automatic_archive_allowed",
    ),
)
def test_d1_boundary_rejects_prohibited_capability(
    field_name,
):
    with pytest.raises(
        ValueError,
        match="prohibited runtime hardening",
    ):
        RuntimeHardeningBoundary(
            **{field_name: True}
        )


def test_d1_limits_are_bounded_and_read_only():
    limits = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_LIMITS
    )

    assert limits.request_target_max_bytes == 4096
    assert limits.header_line_max_bytes == 8192
    assert limits.header_count_max == 64
    assert limits.request_body_max_bytes == 0
    assert limits.socket_timeout_seconds == 5.0
    assert limits.max_concurrent_requests == 32
    assert limits.artifact_max_bytes == 16 * 1024 * 1024
    assert limits.shutdown_timeout_seconds == 5.0


@pytest.mark.parametrize(
    "values",
    (
        {"request_target_max_bytes": 0},
        {"header_line_max_bytes": 999999},
        {"header_count_max": True},
        {"request_body_max_bytes": 1},
        {"socket_timeout_seconds": 0},
        {"max_concurrent_requests": 0},
        {"artifact_max_bytes": 100},
        {"shutdown_timeout_seconds": 31},
    ),
)
def test_d1_limits_reject_unsafe_values(values):
    with pytest.raises(ValueError):
        RuntimeHardeningLimits(**values)


def test_d1_threat_registry_is_deterministic():
    threat_ids = tuple(
        item.threat_id
        for item in (
            BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_THREATS
        )
    )

    assert threat_ids == (
        REQUIRED_RUNTIME_HARDENING_THREAT_IDS
    )
    assert len(threat_ids) == len(set(threat_ids)) == 17


def test_d1_threat_controls_cover_delivery_stages():
    controls = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_THREATS
    )

    assert {
        item.detection_stage
        for item in controls
    } == {
        "D2",
        "D3",
        "D4",
        "D5",
    }

    assert {
        item.category
        for item in controls
    } == {
        "ARTIFACT",
        "HTTP",
        "LIFECYCLE",
        "NETWORK",
        "RESOURCE",
    }


def test_d1_contract_is_contract_only():
    contract = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_CONTRACT
    )

    assert contract.status == "IMPLEMENTED"
    assert contract.allowed_http_methods == (
        "GET",
        "HEAD",
    )
    assert contract.runtime_behavior_modified is False
    assert contract.new_product_capability_added is False
    assert contract.successor_phase == (
        "BROWSER-PRODUCT-CONSOLE-"
        "INTEGRATION-ACCEPTANCE-APP-1"
    )


def test_d1_contract_rejects_missing_threat():
    contract = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_CONTRACT
    )

    with pytest.raises(
        ValueError,
        match="threat controls changed",
    ):
        RuntimeHardeningContract(
            app_id=contract.app_id,
            stage_id=contract.stage_id,
            schema_version=contract.schema_version,
            status=contract.status,
            boundary=contract.boundary,
            limits=contract.limits,
            allowed_http_methods=(
                contract.allowed_http_methods
            ),
            required_security_headers=(
                contract.required_security_headers
            ),
            threat_controls=(
                contract.threat_controls[:-1]
            ),
            successor_phase=(
                contract.successor_phase
            ),
        )


def test_d1_security_headers_match_console():
    contract = (
        BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_CONTRACT
    )

    assert contract.required_security_headers == (
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


def test_d1_existing_runtime_remains_authoritative(
    tmp_path,
):
    boundary = BROWSER_PRODUCT_CONSOLE_RUNTIME_BOUNDARY

    assert boundary.paper_only
    assert boundary.local_only
    assert boundary.loopback_only
    assert boundary.read_only_presentation
    assert boundary.operator_review_required

    config = ConsoleRuntimeConfig(
        allowed_root=Path(tmp_path)
    )

    assert config.host == "127.0.0.1"
    assert config.port == 8765
