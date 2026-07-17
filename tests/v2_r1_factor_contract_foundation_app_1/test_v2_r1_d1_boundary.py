import pytest

from apps.v2_r1_factor_contract_foundation_app_1 import (
    V2R1FactorContractBoundary,
    V2_R1_FACTOR_CONTRACT_BOUNDARY,
)


def test_d1_boundary_preserves_all_authorities_and_prohibitions():
    boundary = V2_R1_FACTOR_CONTRACT_BOUNDARY

    assert boundary.paper_only is True
    assert boundary.local_only is True
    assert boundary.loopback_only is True
    assert boundary.sidecar_only is True
    assert boundary.registered_artifact_only is True
    assert boundary.read_only_presentation is True
    assert boundary.operator_review_required is True
    assert boundary.deterministic_engine_authority_preserved is True
    assert boundary.registered_evidence_authority_preserved is True
    assert boundary.ai_advisory_only is True
    assert boundary.live_data_allowed is False
    assert boundary.network_access_allowed is False
    assert boundary.credential_access_allowed is False
    assert boundary.model_invocation_allowed is False
    assert boundary.prompt_execution_allowed is False
    assert boundary.factor_calculation_allowed is False
    assert boundary.official_scoring_allowed is False
    assert boundary.automatic_activation_allowed is False
    assert boundary.order_path_allowed is False
    assert boundary.real_execution_allowed is False


def test_d1_boundary_fails_closed_when_prohibited_capability_is_enabled():
    with pytest.raises(ValueError, match="prohibited capability"):
        V2R1FactorContractBoundary(network_access_allowed=True)

    with pytest.raises(ValueError, match="authority boundary"):
        V2R1FactorContractBoundary(operator_review_required=False)
