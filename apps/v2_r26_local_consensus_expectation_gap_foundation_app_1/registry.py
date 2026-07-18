from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import (
    ExpectationGapRecord,
    RegisteredActualObservation,
    RegisteredConsensusSnapshot,
)


@dataclass(frozen=True)
class LocalConsensusExpectationGapRegistry:
    consensus_snapshots: tuple[RegisteredConsensusSnapshot, ...] = ()
    actual_observations: tuple[RegisteredActualObservation, ...] = ()
    gap_records: tuple[ExpectationGapRecord, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000:
            raise ValueError("consensus expectation registry capacity is invalid")
        snapshots = tuple(self.consensus_snapshots)
        actuals = tuple(self.actual_observations)
        gaps = tuple(self.gap_records)
        if len(snapshots) + len(actuals) + len(gaps) > self.capacity:
            raise ValueError("consensus expectation registry capacity exceeded")
        for values, identity, digest, message in (
            (snapshots, "snapshot_id", "snapshot_hash", "consensus snapshot"),
            (actuals, "observation_id", "observation_hash", "actual observation"),
            (gaps, "gap_id", "gap_hash", "expectation gap"),
        ):
            if len({getattr(item, identity) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} id is prohibited")
            if len({getattr(item, digest) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} hash is prohibited")
        groups: dict[tuple[str, str, str, str], list[RegisteredConsensusSnapshot]] = {}
        for snapshot in snapshots:
            key = (
                snapshot.subject_id,
                snapshot.metric_id,
                snapshot.market,
                snapshot.horizon,
            )
            groups.setdefault(key, []).append(snapshot)
        for group in groups.values():
            ordered = sorted(group, key=lambda item: item.revision_number)
            if [item.revision_number for item in ordered] != list(range(len(ordered))):
                raise ValueError("consensus revisions must be contiguous from zero")
            for previous, current in zip(ordered, ordered[1:]):
                if current.revises_snapshot_hash != previous.snapshot_hash:
                    raise ValueError("consensus revision predecessor is invalid")
        snapshot_hashes = {item.snapshot_hash for item in snapshots}
        actual_hashes = {item.observation_hash for item in actuals}
        for gap in gaps:
            if gap.consensus.snapshot_hash not in snapshot_hashes:
                raise ValueError("gap consensus must be registered")
            if gap.actual.observation_hash not in actual_hashes:
                raise ValueError("gap actual observation must be registered")
        object.__setattr__(self, "consensus_snapshots", snapshots)
        object.__setattr__(self, "actual_observations", actuals)
        object.__setattr__(self, "gap_records", gaps)

    def append_consensus(
        self, snapshot: RegisteredConsensusSnapshot
    ) -> LocalConsensusExpectationGapRegistry:
        if not isinstance(snapshot, RegisteredConsensusSnapshot):
            raise ValueError("registry accepts RegisteredConsensusSnapshot only")
        return replace(self, consensus_snapshots=(*self.consensus_snapshots, snapshot))

    def append_actual(
        self, actual: RegisteredActualObservation
    ) -> LocalConsensusExpectationGapRegistry:
        if not isinstance(actual, RegisteredActualObservation):
            raise ValueError("registry accepts RegisteredActualObservation only")
        return replace(self, actual_observations=(*self.actual_observations, actual))

    def append_gap(
        self, gap: ExpectationGapRecord
    ) -> LocalConsensusExpectationGapRegistry:
        if not isinstance(gap, ExpectationGapRecord):
            raise ValueError("registry accepts ExpectationGapRecord only")
        return replace(self, gap_records=(*self.gap_records, gap))
