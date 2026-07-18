from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import OperatorFactorGovernanceProjection


@dataclass(frozen=True)
class LocalOperatorFactorGovernanceProjectionRegistry:
    projections: tuple[OperatorFactorGovernanceProjection, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        projections = tuple(self.projections)
        if (
            isinstance(self.capacity, bool)
            or not 1 <= self.capacity <= 100000
            or len(projections) > self.capacity
        ):
            raise ValueError("projection registry capacity is invalid")
        if len({item.projection_id for item in projections}) != len(projections):
            raise ValueError("duplicate projection identity is prohibited")
        if len({item.projection_hash for item in projections}) != len(projections):
            raise ValueError("duplicate projection content is prohibited")
        natural_keys = {
            (item.candidate_id, item.evaluated_at_utc)
            for item in projections
        }
        if len(natural_keys) != len(projections):
            raise ValueError("candidate projection cannot be overwritten at one as-of instant")
        object.__setattr__(self, "projections", projections)

    def append(
        self,
        projection: OperatorFactorGovernanceProjection,
    ) -> "LocalOperatorFactorGovernanceProjectionRegistry":
        if not isinstance(projection, OperatorFactorGovernanceProjection):
            raise ValueError("registry accepts governance projections only")
        return replace(self, projections=(*self.projections, projection))
