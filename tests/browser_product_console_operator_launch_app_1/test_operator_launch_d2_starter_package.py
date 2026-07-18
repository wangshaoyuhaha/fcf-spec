import shutil
from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    STARTER_DATA_CLASSIFICATION,
    STARTER_PACKAGE_STAGE_ID,
    build_console_read_model,
    build_default_operator_launch_profile,
    load_starter_artifact_package,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_d2_default_starter_package_is_registered_and_complete() -> None:
    profile = build_default_operator_launch_profile(project_root=PROJECT_ROOT)
    package, loaded = load_starter_artifact_package(profile)

    assert STARTER_PACKAGE_STAGE_ID == "D2"
    assert package.correlation_id == "corr-operator-launch-demo-v1"
    assert package.artifact_count == 16
    assert package.data_classification == STARTER_DATA_CLASSIFICATION
    assert package.operator_review_required is True
    assert len(loaded.artifacts) == package.artifact_count
    assert {
        "data_snapshot",
        "ranked_watchlist",
        "ai_explanation",
        "paper_validation",
        "shadow_observation",
        "operator_review",
        "report_archive",
        "policy_snapshot",
        "model_governance",
        "factor_governance_projection",
        "audit_receipt",
        "manifest",
    }.issubset(set(package.artifact_types))


def test_d2_starter_package_demonstrates_stocks_and_btc() -> None:
    profile = build_default_operator_launch_profile(project_root=PROJECT_ROOT)
    _, loaded = load_starter_artifact_package(profile)
    model = build_console_read_model(loaded)

    symbols = {candidate.symbol for candidate in model.candidates}
    assert symbols == {"DEMO-600000", "DEMO-AAPL", "DEMO-BTC-USD"}
    assert all(
        "DEMONSTRATION_DATA" in candidate.risk_flags
        for candidate in model.candidates
    )


def test_d2_starter_package_rejects_tampering(tmp_path: Path) -> None:
    source = build_default_operator_launch_profile(
        project_root=PROJECT_ROOT
    ).allowed_root
    copied = tmp_path / "starter"
    shutil.copytree(source, copied)
    (copied / "registered" / "data-snapshot.json").write_text(
        "{}",
        encoding="utf-8",
    )
    profile = build_default_operator_launch_profile(project_root=tmp_path)
    profile = profile.__class__(
        allowed_root=copied,
        index_path=copied / "index.json",
    )

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_starter_artifact_package(profile)


def test_d2_every_payload_is_demonstrative_and_reviewed() -> None:
    profile = build_default_operator_launch_profile(project_root=PROJECT_ROOT)
    _, loaded = load_starter_artifact_package(profile)

    for artifact in loaded.artifacts:
        assert (
            artifact.payload["data_classification"]
            == STARTER_DATA_CLASSIFICATION
        )
        assert artifact.payload["operator_review_required"] is True
