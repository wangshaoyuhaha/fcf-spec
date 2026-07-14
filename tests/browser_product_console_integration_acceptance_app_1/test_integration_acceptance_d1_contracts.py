import pytest

from apps.browser_product_console_integration_acceptance_app_1 import (
    BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_BOUNDARY,
    BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_CONTRACT,
    INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY,
    INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX,
    REQUIRED_INTEGRATION_ACCEPTANCE_FIXTURE_IDS,
    REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS,
    IntegrationAcceptanceBoundary,
    IntegrationAcceptanceContract,
    IntegrationAcceptanceFixture,
    IntegrationAcceptanceMatrixRow,
)


_REQUIRED_BOUNDARY_FIELDS = (
    "paper_only",
    "local_only",
    "loopback_only",
    "sidecar_only",
    "registered_artifact_only",
    "read_only_presentation",
    "operator_review_required",
    "deterministic_engine_authority",
    "registered_evidence_authority",
    "ai_advisory_only",
    "reproducibility_required",
    "generated_output_restoration_required",
)

_PROHIBITED_BOUNDARY_FIELDS = (
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
)


def test_d1_boundary_preserves_all_required_authorities():
    boundary = (
        BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_BOUNDARY
    )

    for field_name in _REQUIRED_BOUNDARY_FIELDS:
        assert getattr(boundary, field_name) is True


@pytest.mark.parametrize(
    "field_name",
    _REQUIRED_BOUNDARY_FIELDS,
)
def test_d1_boundary_rejects_disabled_authority(
    field_name,
):
    with pytest.raises(
        ValueError,
        match="must remain enabled",
    ):
        IntegrationAcceptanceBoundary(
            **{field_name: False}
        )


@pytest.mark.parametrize(
    "field_name",
    _PROHIBITED_BOUNDARY_FIELDS,
)
def test_d1_boundary_rejects_prohibited_capability(
    field_name,
):
    with pytest.raises(
        ValueError,
        match="prohibited integration acceptance",
    ):
        IntegrationAcceptanceBoundary(
            **{field_name: True}
        )


def test_d1_system_matrix_is_deterministic():
    matrix_ids = tuple(
        row.matrix_id
        for row in INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX
    )

    assert matrix_ids == (
        REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS
    )
    assert len(matrix_ids) == len(set(matrix_ids)) == 8


def test_d1_system_matrix_covers_required_layers():
    assert {
        row.layer
        for row in INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX
    } == {
        "EVIDENCE",
        "OPERATOR",
        "PRODUCT",
        "RUNTIME",
        "WORKSPACE",
    }

    assert {
        row.delivery_stage
        for row in INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX
    } == {
        "D2",
        "D3",
        "D4",
        "D5",
    }


@pytest.mark.parametrize(
    "values",
    (
        {
            "matrix_id": "bad-id",
            "layer": "PRODUCT",
            "subject": "subject",
            "acceptance_dimensions": ("one",),
            "delivery_stage": "D2",
        },
        {
            "matrix_id": "VALID_ID",
            "layer": "UNKNOWN",
            "subject": "subject",
            "acceptance_dimensions": ("one",),
            "delivery_stage": "D2",
        },
        {
            "matrix_id": "VALID_ID",
            "layer": "PRODUCT",
            "subject": "subject",
            "acceptance_dimensions": ("one",),
            "delivery_stage": "D6",
        },
        {
            "matrix_id": "VALID_ID",
            "layer": "PRODUCT",
            "subject": " subject",
            "acceptance_dimensions": ("one",),
            "delivery_stage": "D2",
        },
        {
            "matrix_id": "VALID_ID",
            "layer": "PRODUCT",
            "subject": "subject",
            "acceptance_dimensions": (),
            "delivery_stage": "D2",
        },
    ),
)
def test_d1_system_matrix_rejects_invalid_rows(values):
    with pytest.raises(ValueError):
        IntegrationAcceptanceMatrixRow(**values)


def test_d1_fixture_registry_is_deterministic():
    fixture_ids = tuple(
        fixture.fixture_id
        for fixture in INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY
    )

    assert fixture_ids == (
        REQUIRED_INTEGRATION_ACCEPTANCE_FIXTURE_IDS
    )
    assert len(fixture_ids) == len(set(fixture_ids)) == 6


def test_d1_fixture_registry_preserves_read_only_authority():
    for fixture in INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY:
        assert fixture.deterministic
        assert fixture.read_only
        assert fixture.registered_artifact_only
        assert fixture.operator_review_required
        assert fixture.required_fields


@pytest.mark.parametrize(
    "field_name",
    (
        "deterministic",
        "read_only",
        "registered_artifact_only",
        "operator_review_required",
    ),
)
def test_d1_fixture_rejects_disabled_authority(
    field_name,
):
    values = {
        "fixture_id": "VALID_FIXTURE",
        "source_kind": "STATIC_CONTRACT",
        "purpose": "purpose",
        "required_fields": ("field",),
        field_name: False,
    }

    with pytest.raises(
        ValueError,
        match="fixture flags must remain enabled",
    ):
        IntegrationAcceptanceFixture(**values)


def test_d1_fixture_rejects_unknown_source_kind():
    with pytest.raises(
        ValueError,
        match="unsupported integration acceptance source kind",
    ):
        IntegrationAcceptanceFixture(
            fixture_id="VALID_FIXTURE",
            source_kind="UNKNOWN",
            purpose="purpose",
            required_fields=("field",),
        )


def test_d1_contract_is_contract_only():
    contract = (
        BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_CONTRACT
    )

    assert contract.status == "IMPLEMENTED"
    assert contract.allowed_http_methods == (
        "GET",
        "HEAD",
    )
    assert contract.delivery_order == (
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
    )
    assert contract.successor_policy == (
        "NO_SUCCESSOR_APPROVED"
    )
    assert contract.runtime_behavior_modified is False
    assert contract.product_capability_added is False


def test_d1_contract_preserves_security_headers():
    contract = (
        BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_CONTRACT
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


def test_d1_contract_rejects_matrix_drift():
    contract = (
        BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_CONTRACT
    )

    with pytest.raises(
        ValueError,
        match="system matrix changed",
    ):
        IntegrationAcceptanceContract(
            app_id=contract.app_id,
            stage_id=contract.stage_id,
            schema_version=contract.schema_version,
            status=contract.status,
            boundary=contract.boundary,
            system_matrix=contract.system_matrix[:-1],
            fixture_registry=contract.fixture_registry,
            allowed_http_methods=contract.allowed_http_methods,
            required_security_headers=(
                contract.required_security_headers
            ),
            delivery_order=contract.delivery_order,
            successor_policy=contract.successor_policy,
        )


def test_d1_contract_rejects_fixture_registry_drift():
    contract = (
        BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_CONTRACT
    )

    with pytest.raises(
        ValueError,
        match="fixture registry changed",
    ):
        IntegrationAcceptanceContract(
            app_id=contract.app_id,
            stage_id=contract.stage_id,
            schema_version=contract.schema_version,
            status=contract.status,
            boundary=contract.boundary,
            system_matrix=contract.system_matrix,
            fixture_registry=contract.fixture_registry[:-1],
            allowed_http_methods=contract.allowed_http_methods,
            required_security_headers=(
                contract.required_security_headers
            ),
            delivery_order=contract.delivery_order,
            successor_policy=contract.successor_policy,
        )


@pytest.mark.parametrize(
    "field_name",
    (
        "runtime_behavior_modified",
        "product_capability_added",
    ),
)
def test_d1_contract_rejects_capability_expansion(
    field_name,
):
    contract = (
        BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_CONTRACT
    )

    values = {
        "app_id": contract.app_id,
        "stage_id": contract.stage_id,
        "schema_version": contract.schema_version,
        "status": contract.status,
        "boundary": contract.boundary,
        "system_matrix": contract.system_matrix,
        "fixture_registry": contract.fixture_registry,
        "allowed_http_methods": contract.allowed_http_methods,
        "required_security_headers": (
            contract.required_security_headers
        ),
        "delivery_order": contract.delivery_order,
        "successor_policy": contract.successor_policy,
        field_name: True,
    }

    with pytest.raises(
        ValueError,
        match="D1 must not",
    ):
        IntegrationAcceptanceContract(**values)
