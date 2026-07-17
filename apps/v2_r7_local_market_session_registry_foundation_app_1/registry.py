from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import MarketSessionDefinition
from .resolver import SessionResolutionEvidence, resolve_market_session


@dataclass(frozen=True)
class LocalMarketSessionRegistry:
    definitions: tuple[MarketSessionDefinition, ...] = ()
    capacity: int = 1000

    def __post_init__(self) -> None:
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 10000:
            raise ValueError("market session registry capacity is invalid")
        hashes = tuple(item.definition_hash for item in self.definitions)
        natural_keys = tuple(
            (
                item.registry_id,
                item.venue,
                item.trade_date,
                item.calendar_version,
                item.rule_version,
            )
            for item in self.definitions
        )
        if len(set(hashes)) != len(hashes) or len(set(natural_keys)) != len(natural_keys):
            raise ValueError("duplicate market session definition is prohibited")
        if len(self.definitions) > self.capacity:
            raise ValueError("market session registry capacity exceeded")

    def append(self, item: MarketSessionDefinition) -> LocalMarketSessionRegistry:
        if len(self.definitions) >= self.capacity:
            raise ValueError("market session registry capacity exceeded")
        if any(existing.definition_hash == item.definition_hash for existing in self.definitions):
            raise ValueError("duplicate market session definition hash is prohibited")
        natural_key = (
            item.registry_id,
            item.venue,
            item.trade_date,
            item.calendar_version,
            item.rule_version,
        )
        if any(
            (
                existing.registry_id,
                existing.venue,
                existing.trade_date,
                existing.calendar_version,
                existing.rule_version,
            )
            == natural_key
            for existing in self.definitions
        ):
            raise ValueError("duplicate market session natural key is prohibited")
        return replace(self, definitions=(*self.definitions, item))

    def resolve(
        self,
        registry_id: str,
        *,
        observed_at_utc: str,
        as_of_utc: str,
    ) -> SessionResolutionEvidence:
        matches = tuple(item for item in self.definitions if item.registry_id == registry_id)
        if len(matches) != 1:
            raise ValueError("registry id must resolve to exactly one definition")
        return resolve_market_session(
            matches[0], observed_at_utc=observed_at_utc, as_of_utc=as_of_utc
        )
