from dataclasses import replace
from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    LAUNCH_STAGE_ID,
    OPERATOR_LAUNCH_APP_ID,
    OPERATOR_LAUNCH_BOUNDARY,
    STARTER_DATA_CLASSIFICATION,
    OperatorLaunchBoundary,
    build_default_operator_launch_profile,
)


def test_d1_boundary_preserves_product_authority() -> None:
    boundary = OPERATOR_LAUNCH_BOUNDARY

    assert OPERATOR_LAUNCH_APP_ID == (
        "BROWSER-PRODUCT-CONSOLE-OPERATOR-LAUNCH-APP-1"
    )
    assert LAUNCH_STAGE_ID == "D1"
    assert boundary.explicit_operator_invocation_required is True
    assert boundary.paper_only is True
    assert boundary.loopback_only is True
    assert boundary.registered_artifact_only is True
    assert boundary.read_only_presentation is True
    assert boundary.operator_review_required is True
    assert boundary.deterministic_authority_preserved is True
    assert boundary.registered_evidence_authority_preserved is True
    assert boundary.ai_advisory_only is True


@pytest.mark.parametrize(
    "field_name",
    (
        "server_autostart_allowed",
        "external_data_fetching_allowed",
        "public_network_binding_allowed",
        "financial_execution_allowed",
        "automatic_learning_activation_allowed",
    ),
)
def test_d1_boundary_rejects_prohibited_capability(field_name: str) -> None:
    with pytest.raises(ValueError, match="prohibited"):
        replace(OperatorLaunchBoundary(), **{field_name: True})


def test_d1_default_profile_is_deterministic(tmp_path: Path) -> None:
    profile = build_default_operator_launch_profile(project_root=tmp_path)

    assert profile.allowed_root == (
        tmp_path / "examples" / "browser_product_console_starter"
    )
    assert profile.index_path == profile.allowed_root / "index.json"
    assert profile.url == "http://127.0.0.1:8765/"
    assert profile.open_browser is True
    assert profile.data_classification == STARTER_DATA_CLASSIFICATION
    assert "Demonstration Data" in profile.title


def test_d1_profile_rejects_privileged_port(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="port"):
        build_default_operator_launch_profile(
            project_root=tmp_path,
            port=80,
        )
