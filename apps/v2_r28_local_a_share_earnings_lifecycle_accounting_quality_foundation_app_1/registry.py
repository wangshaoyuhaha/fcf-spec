from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import AccountingQualityChallengeRecord, RegisteredAccountingObservation, RegisteredEarningsLifecycleStage


@dataclass(frozen=True)
class LocalEarningsAccountingQualityRegistry:
    stages: tuple[RegisteredEarningsLifecycleStage, ...] = ()
    observations: tuple[RegisteredAccountingObservation, ...] = ()
    challenges: tuple[AccountingQualityChallengeRecord, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000:
            raise ValueError("earnings accounting registry capacity is invalid")
        stages, observations, challenges = tuple(self.stages), tuple(self.observations), tuple(self.challenges)
        if len(stages) + len(observations) + len(challenges) > self.capacity:
            raise ValueError("earnings accounting registry capacity exceeded")
        for values, identity, digest, message in (
            (stages, "stage_id", "stage_hash", "earnings stage"),
            (observations, "observation_id", "observation_hash", "accounting observation"),
            (challenges, "challenge_id", "challenge_hash", "accounting challenge"),
        ):
            if len({getattr(item, identity) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} id is prohibited")
            if len({getattr(item, digest) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} hash is prohibited")
        stage_hashes = {item.stage_hash for item in stages}
        observation_hashes = {item.observation_hash for item in observations}
        if any(item.stage.stage_hash not in stage_hashes for item in observations):
            raise ValueError("accounting observation stage must be registered")
        if any(item.observation.observation_hash not in observation_hashes for item in challenges):
            raise ValueError("accounting challenge observation must be registered")
        object.__setattr__(self, "stages", stages)
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "challenges", challenges)

    def append_stage(self, item: RegisteredEarningsLifecycleStage) -> LocalEarningsAccountingQualityRegistry:
        if not isinstance(item, RegisteredEarningsLifecycleStage):
            raise ValueError("registry accepts RegisteredEarningsLifecycleStage only")
        return replace(self, stages=(*self.stages, item))

    def append_observation(self, item: RegisteredAccountingObservation) -> LocalEarningsAccountingQualityRegistry:
        if not isinstance(item, RegisteredAccountingObservation):
            raise ValueError("registry accepts RegisteredAccountingObservation only")
        return replace(self, observations=(*self.observations, item))

    def append_challenge(self, item: AccountingQualityChallengeRecord) -> LocalEarningsAccountingQualityRegistry:
        if not isinstance(item, AccountingQualityChallengeRecord):
            raise ValueError("registry accepts AccountingQualityChallengeRecord only")
        return replace(self, challenges=(*self.challenges, item))
