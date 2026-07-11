from pathlib import Path

from apps.ai_comprehensive_report_consumer_activation_app_1 import (
    ACTIVATION_SURFACES,
    PHASE_ID,
    SOURCE_BINDING_PACKAGE,
    build_activation_contract,
    discover_production_entry_point_candidates,
)


def _write_python(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("# deterministic fixture\n", encoding="utf-8")


def test_d1_discovery_classifies_required_surfaces(tmp_path: Path) -> None:
    _write_python(
        tmp_path
        / "apps"
        / "operator_review_app_1"
        / "entry_point.py"
    )
    _write_python(
        tmp_path
        / "apps"
        / "dashboard_status_app_1"
        / "entry_point.py"
    )
    _write_python(
        tmp_path
        / "apps"
        / "report_archive_app_1"
        / "entry_point.py"
    )

    candidates = discover_production_entry_point_candidates(tmp_path)

    assert {candidate.surface for candidate in candidates} == set(
        ACTIVATION_SURFACES
    )
    assert tuple(
        (candidate.surface, candidate.relative_path)
        for candidate in candidates
    ) == tuple(
        sorted(
            (
                candidate.surface,
                candidate.relative_path,
            )
            for candidate in candidates
        )
    )


def test_d1_discovery_excludes_binding_activation_and_tests(
    tmp_path: Path,
) -> None:
    _write_python(
        tmp_path
        / "apps"
        / "ai_comprehensive_report_consumer_binding_app_1"
        / "operator_review_binding.py"
    )
    _write_python(
        tmp_path
        / "apps"
        / "ai_comprehensive_report_consumer_activation_app_1"
        / "ui_activation.py"
    )
    _write_python(
        tmp_path
        / "tests"
        / "report_archive_test.py"
    )

    assert discover_production_entry_point_candidates(tmp_path) == ()


def test_d1_contract_preserves_all_safety_boundaries(
    tmp_path: Path,
) -> None:
    _write_python(
        tmp_path
        / "apps"
        / "operator_review_app_1"
        / "entry_point.py"
    )
    _write_python(
        tmp_path
        / "apps"
        / "dashboard_status_app_1"
        / "entry_point.py"
    )
    _write_python(
        tmp_path
        / "apps"
        / "report_archive_app_1"
        / "entry_point.py"
    )

    contract = build_activation_contract(tmp_path)

    assert contract.phase_id == PHASE_ID
    assert contract.source_binding_package == SOURCE_BINDING_PACKAGE
    assert contract.validate() == ()
    assert contract.paper_only is True
    assert contract.local_only is True
    assert contract.read_only is True
    assert contract.sidecar_only is True
    assert contract.deterministic_only is True
    assert contract.registered_artifacts_only is True
    assert contract.operator_review_required is True
    assert contract.manual_archive_authorization_required is True
    assert contract.frozen_core_mutation_allowed is False
    assert contract.automatic_approval_allowed is False
    assert contract.automatic_archive_allowed is False
    assert contract.archive_write_allowed is False
    assert contract.runtime_model_invocation_allowed is False
    assert contract.prompt_execution_allowed is False
    assert contract.automatic_routing_allowed is False
    assert contract.real_execution_allowed is False


def test_d1_repository_has_all_required_surface_candidates() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    contract = build_activation_contract(repo_root)
    counts = contract.candidate_count_by_surface()

    assert contract.validate() == ()
    assert all(counts[surface] > 0 for surface in ACTIVATION_SURFACES)
    assert all(
        "ai_comprehensive_report_consumer_binding_app_1"
        not in candidate.relative_path
        for candidate in contract.candidates
    )
    assert all(
        "ai_comprehensive_report_consumer_activation_app_1"
        not in candidate.relative_path
        for candidate in contract.candidates
    )
