from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import (
    IndexFuturesBasisRollRecord,
    RegisteredFuturesCurveObservation,
    RegisteredIndexFuturesContract,
)


@dataclass(frozen=True)
class LocalIndexFuturesBasisRollExpiryRegistry:
    contracts: tuple[RegisteredIndexFuturesContract, ...] = ()
    observations: tuple[RegisteredFuturesCurveObservation, ...] = ()
    records: tuple[IndexFuturesBasisRollRecord, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000:
            raise ValueError("index-futures registry capacity is invalid")
        contracts = tuple(self.contracts)
        observations = tuple(self.observations)
        records = tuple(self.records)
        if len(contracts) + len(observations) + len(records) > self.capacity:
            raise ValueError("index-futures registry capacity exceeded")
        for values, identity, digest, message in (
            (contracts, "contract_id", "contract_hash", "index-futures contract"),
            (observations, "observation_id", "observation_hash", "curve observation"),
            (records, "record_id", "record_hash", "basis-roll record"),
        ):
            if len({getattr(item, identity) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} id is prohibited")
            if len({getattr(item, digest) for item in values}) != len(values):
                raise ValueError(f"duplicate {message} hash is prohibited")
        contract_hashes = {item.contract_hash for item in contracts}
        observation_hashes = {item.observation_hash for item in observations}
        if any(
            item.front_contract.contract_hash not in contract_hashes
            or item.next_contract.contract_hash not in contract_hashes
            for item in observations
        ):
            raise ValueError("curve observation contracts must be registered")
        if any(item.observation.observation_hash not in observation_hashes for item in records):
            raise ValueError("basis-roll observation must be registered")
        object.__setattr__(self, "contracts", contracts)
        object.__setattr__(self, "observations", observations)
        object.__setattr__(self, "records", records)

    def append_contract(
        self, item: RegisteredIndexFuturesContract
    ) -> LocalIndexFuturesBasisRollExpiryRegistry:
        if not isinstance(item, RegisteredIndexFuturesContract):
            raise ValueError("registry accepts RegisteredIndexFuturesContract only")
        return replace(self, contracts=(*self.contracts, item))

    def append_observation(
        self, item: RegisteredFuturesCurveObservation
    ) -> LocalIndexFuturesBasisRollExpiryRegistry:
        if not isinstance(item, RegisteredFuturesCurveObservation):
            raise ValueError("registry accepts RegisteredFuturesCurveObservation only")
        return replace(self, observations=(*self.observations, item))

    def append_record(
        self, item: IndexFuturesBasisRollRecord
    ) -> LocalIndexFuturesBasisRollExpiryRegistry:
        if not isinstance(item, IndexFuturesBasisRollRecord):
            raise ValueError("registry accepts IndexFuturesBasisRollRecord only")
        return replace(self, records=(*self.records, item))
