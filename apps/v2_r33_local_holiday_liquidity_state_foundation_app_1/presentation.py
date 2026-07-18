from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalHolidayLiquidityRegistry


@dataclass(frozen=True)
class LocalHolidayLiquidityReadModel:
    payload: Mapping[str, object]


def build_read_model(
    registry: LocalHolidayLiquidityRegistry,
) -> LocalHolidayLiquidityReadModel:
    return LocalHolidayLiquidityReadModel(
        MappingProxyType(
            {
                "observation_count": len(registry.observations),
                "measurement_count": len(registry.measurements),
                "registered_artifact_only": True,
                "operator_review_required": True,
                "fixed_last_three_days_rule": False,
                "fixed_threshold": False,
                "stress_direction": False,
                "factor_activation": False,
                "factor_or_score": False,
                "signal_or_recommendation": False,
                "order_or_execution": False,
            }
        )
    )
