from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from .fixtures import factor_definition, forecast_target_definition


def test_d2_factor_contract_is_immutable_and_complete():
    factor = factor_definition()

    assert isinstance(factor.parameter_schema, MappingProxyType)
    assert isinstance(factor.deterministic_test_vectors[0], MappingProxyType)
    assert factor.point_in_time_required is True
    assert factor.output_range[0] < factor.output_range[1]
    with pytest.raises(TypeError):
        factor.parameter_schema["window"] = 21
    with pytest.raises(FrozenInstanceError):
        factor.factor_id = "changed"


def test_d2_factor_contract_rejects_unsafe_or_incoherent_definitions():
    factor = factor_definition()

    with pytest.raises(ValueError, match="point_in_time_required"):
        replace(factor, point_in_time_required=False)
    with pytest.raises(ValueError, match="must be disjoint"):
        replace(factor, invalid_market_regimes=("normal",))
    with pytest.raises(ValueError, match="lower must be less"):
        replace(factor, output_range=("1", "1"))
    with pytest.raises(ValueError, match="cannot depend on itself"):
        replace(factor, dependency_factor_ids=(factor.factor_id,))


def test_d2_forecast_target_contract_is_explicit_and_fail_closed():
    target = forecast_target_definition()

    assert target.target_id == "target.return.1d"
    assert target.minimum_sample == 100
    assert target.evaluation_metrics == ("mae", "rank-ic")
    with pytest.raises(ValueError, match="minimum_sample"):
        replace(target, minimum_sample=0)
    with pytest.raises(ValueError, match="UTC"):
        replace(target, effective_at_utc="2026-07-17T00:00:00+08:00")
