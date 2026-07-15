from pathlib import Path
from types import MappingProxyType

from apps.browser_product_console_integration_acceptance_app_1 import (
    BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_BOUNDARY,
    BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_CONTRACT,
    INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY,
    INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX,
    REQUIRED_INTEGRATION_ACCEPTANCE_FIXTURE_IDS,
    REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS,
    IntegrationValidationSummary,
    build_browser_console_integration_operator_acceptance,
)
from apps.browser_product_console_runtime_app_1 import (
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_BOUNDARY,
    BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_CONTRACT,
    BrowserProductConsoleApplication,
    ConsoleReadModel,
)


_ROOT = Path(__file__).resolve().parents[2]
_DOC_NAMES = tuple(
    f"BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_APP_1_D{stage}.md"
    for stage in range(1, 7)
)


def _application() -> BrowserProductConsoleApplication:
    return BrowserProductConsoleApplication(
        ConsoleReadModel(
            correlation_id="corr-d6-final-closeout",
            candidates=(),
            sections=MappingProxyType({}),
            source_artifact_ids=(),
            artifact_records=(),
        )
    )


def _validation_summary() -> IntegrationValidationSummary:
    return IntegrationValidationSummary(
        targeted_passed=458,
        targeted_skipped=3,
        full_passed=4222,
        full_skipped=3,
        run_all_checks_passed=True,
        generated_outputs_restored=True,
        exact_changed_files_verified=True,
        diff_check_passed=True,
    )


def test_d6_delivery_chain_and_final_documents_are_complete():
    for name in _DOC_NAMES:
        path = _ROOT / "docs" / name
        assert path.is_file(), name
        content = path.read_text(encoding="ascii")
        assert "P1-P47 frozen" in content
        assert "no P48" in content

    final_path = (
        _ROOT
        / "docs"
        / "BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_APP_1_FINAL.md"
    )
    assert final_path.is_file()
    final_content = final_path.read_text(encoding="ascii")
    assert "READY_FOR_MAIN_MERGE" in final_content
    assert "Operator review mandatory" in final_content
    assert "no tag, release, or deployment" in final_content


def test_d6_contract_matrix_and_fixture_registries_are_final():
    contract = BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_CONTRACT

    assert contract.status == "IMPLEMENTED"
    assert contract.delivery_order == (
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
    )
    assert tuple(
        row.matrix_id for row in INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX
    ) == REQUIRED_INTEGRATION_ACCEPTANCE_MATRIX_IDS
    assert tuple(
        fixture.fixture_id
        for fixture in INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY
    ) == REQUIRED_INTEGRATION_ACCEPTANCE_FIXTURE_IDS
    assert {
        row.delivery_stage
        for row in INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX
    } == {"D2", "D3", "D4", "D5"}


def test_d6_operator_package_is_ready_but_never_auto_approved():
    package = build_browser_console_integration_operator_acceptance(
        _validation_summary()
    )
    payload = package.to_payload()

    assert package.status == "READY_FOR_OPERATOR_REVIEW"
    assert package.ready_for_operator_review is True
    assert package.operator_review_required is True
    assert package.automatic_approval_allowed is False
    assert package.unresolved_items == ()
    assert all(status == "PASSED" for _, status in package.matrix_results)
    assert payload["status"] == "READY_FOR_OPERATOR_REVIEW"
    assert payload["automatic_approval_allowed"] is False


def test_d6_all_authority_boundaries_remain_enforced():
    integration = BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_BOUNDARY
    hardening = BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_BOUNDARY
    hardening_contract = BROWSER_PRODUCT_CONSOLE_RUNTIME_HARDENING_CONTRACT

    assert integration.paper_only is True
    assert integration.local_only is True
    assert integration.loopback_only is True
    assert integration.sidecar_only is True
    assert integration.registered_artifact_only is True
    assert integration.read_only_presentation is True
    assert integration.operator_review_required is True
    assert integration.deterministic_engine_authority is True
    assert integration.registered_evidence_authority is True
    assert integration.ai_advisory_only is True
    assert integration.core_mutation_allowed is False
    assert integration.p48_creation_allowed is False
    assert integration.order_path_allowed is False
    assert integration.real_execution_allowed is False
    assert integration.automatic_approval_allowed is False
    assert integration.automatic_promotion_allowed is False
    assert integration.automatic_learning_activation_allowed is False

    assert hardening.loopback_only is True
    assert hardening.registered_artifact_only is True
    assert hardening.read_only_presentation is True
    assert hardening.operator_review_required is True
    assert hardening.external_network_binding_allowed is False
    assert hardening.real_execution_allowed is False
    assert hardening_contract.allowed_http_methods == ("GET", "HEAD")


def test_d6_integrated_surface_remains_local_and_read_only():
    application = _application()
    health = application.dispatch("GET", "/health")

    assert health.status == 200
    assert b'"mode": "paper-only"' in health.body
    assert b'"host_scope": "loopback-only"' in health.body
    assert b'"operator_review_required": true' in health.body

    for path in (
        "/",
        "/stocks",
        "/data",
        "/runs",
        "/ai-comparison",
        "/validation",
        "/review",
        "/reports",
        "/audit",
        "/evidence",
        "/evidence/artifacts",
        "/evidence/lineage",
        "/evidence/risk",
        "/evidence/validation",
        "/evidence/review",
        "/evidence/archive",
    ):
        get_response = application.dispatch("GET", path)
        head_response = application.dispatch("HEAD", path)

        assert get_response.status == 200, path
        assert head_response.status == 200, path
        assert head_response.body == b"", path
        assert application.dispatch("POST", path).status == 405, path


def test_d6_unknown_traversal_and_malformed_paths_fail_closed():
    application = _application()

    assert application.dispatch("GET", "/unknown").status == 404
    assert application.dispatch("GET", "/../audit").status == 404
    assert application.dispatch("GET", "/%2e%2e/audit").status == 404
    assert application.dispatch("GET", "/evidence?type=%00").status == 400
