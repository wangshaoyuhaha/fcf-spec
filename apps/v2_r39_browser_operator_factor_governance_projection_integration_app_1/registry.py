from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import RegisteredBrowserGovernanceProjection


@dataclass(frozen=True)
class RegisteredBrowserGovernanceProjectionRegistry:
    artifacts: tuple[RegisteredBrowserGovernanceProjection, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        artifacts = tuple(self.artifacts)
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000:
            raise ValueError("browser governance registry capacity is invalid")
        if len(artifacts) > self.capacity:
            raise ValueError("browser governance registry capacity exceeded")
        hashes = {item.projection.projection_hash for item in artifacts}
        if len(hashes) != len(artifacts):
            raise ValueError("duplicate browser governance projection is prohibited")
        object.__setattr__(self, "artifacts", artifacts)

    def append(
        self,
        artifact: RegisteredBrowserGovernanceProjection,
    ) -> "RegisteredBrowserGovernanceProjectionRegistry":
        if not isinstance(artifact, RegisteredBrowserGovernanceProjection):
            raise ValueError("registry accepts browser governance projections only")
        return replace(self, artifacts=(*self.artifacts, artifact))
