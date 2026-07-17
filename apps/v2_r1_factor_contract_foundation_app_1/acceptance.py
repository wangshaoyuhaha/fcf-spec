from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .boundary import V2_R1_FACTOR_CONTRACT_BOUNDARY
from .registries import FactorRegistry, ForecastTargetRegistry
from .state_sync import StateSyncAnchor


@dataclass(frozen=True)
class V2R1OperatorAcceptance:
    status: str
    factor_count: int
    forecast_target_count: int
    state_sync_count: int
    unresolved_items: tuple[str, ...]
    operator_review_required: bool = True
    automatic_approval_allowed: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "factor_count",
            "forecast_target_count",
            "state_sync_count",
        ):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{field_name} must be a non-negative integer")
        items = tuple(str(item).strip() for item in self.unresolved_items)
        if any(not item for item in items) or len(set(items)) != len(items):
            raise ValueError("unresolved_items must be unique normalized text")
        expected = (
            "READY_FOR_OPERATOR_REVIEW"
            if self.factor_count > 0
            and self.forecast_target_count > 0
            and self.state_sync_count > 0
            and not items
            else "BLOCKED"
        )
        if self.status != expected:
            raise ValueError("Operator acceptance status is inconsistent")
        if (
            self.operator_review_required is not True
            or self.automatic_approval_allowed is not False
        ):
            raise ValueError("Operator acceptance authority changed")
        object.__setattr__(self, "unresolved_items", items)

    def to_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "phase": "V2-R1-FACTOR-CONTRACT-FOUNDATION-APP-1",
                "status": self.status,
                "factor_count": self.factor_count,
                "forecast_target_count": self.forecast_target_count,
                "state_sync_count": self.state_sync_count,
                "unresolved_items": self.unresolved_items,
                "operator_review_required": self.operator_review_required,
                "automatic_approval_allowed": self.automatic_approval_allowed,
                "read_only": V2_R1_FACTOR_CONTRACT_BOUNDARY.read_only_presentation,
                "factor_calculation_allowed": False,
                "official_scoring_allowed": False,
                "automatic_activation_allowed": False,
                "order_path_allowed": False,
                "real_execution_allowed": False,
            }
        )


def build_v2_r1_operator_acceptance(
    factor_registry: FactorRegistry,
    target_registry: ForecastTargetRegistry,
    anchors: tuple[StateSyncAnchor, ...],
    *,
    unresolved_items: tuple[str, ...] = (),
) -> V2R1OperatorAcceptance:
    items = tuple(unresolved_items)
    ready = bool(
        factor_registry.definitions
        and target_registry.definitions
        and anchors
        and not items
    )
    return V2R1OperatorAcceptance(
        status="READY_FOR_OPERATOR_REVIEW" if ready else "BLOCKED",
        factor_count=len(factor_registry.definitions),
        forecast_target_count=len(target_registry.definitions),
        state_sync_count=len(anchors),
        unresolved_items=items,
    )
