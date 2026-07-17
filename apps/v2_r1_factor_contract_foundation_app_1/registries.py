from __future__ import annotations

from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Mapping

from .contracts import (
    ChampionChallengerStatus,
    FactorDefinition,
    FactorLifecycle,
    ForecastTargetDefinition,
    ValidationStatus,
    normalize_identifiers,
    parse_utc_timestamp,
    require_identifier,
    require_utc_timestamp,
)


_ALLOWED_TRANSITIONS = MappingProxyType(
    {
        FactorLifecycle.DRAFT: frozenset({FactorLifecycle.RESEARCH}),
        FactorLifecycle.RESEARCH: frozenset(
            {FactorLifecycle.CHALLENGER, FactorLifecycle.RETIRED}
        ),
        FactorLifecycle.CHALLENGER: frozenset(
            {
                FactorLifecycle.QUALIFIED,
                FactorLifecycle.DEGRADED,
                FactorLifecycle.RETIRED,
            }
        ),
        FactorLifecycle.QUALIFIED: frozenset(
            {
                FactorLifecycle.CHAMPION,
                FactorLifecycle.DEGRADED,
                FactorLifecycle.RETIRED,
            }
        ),
        FactorLifecycle.CHAMPION: frozenset(
            {FactorLifecycle.DEGRADED, FactorLifecycle.RETIRED}
        ),
        FactorLifecycle.DEGRADED: frozenset(
            {FactorLifecycle.CHALLENGER, FactorLifecycle.RETIRED}
        ),
        FactorLifecycle.RETIRED: frozenset(),
    }
)


@dataclass(frozen=True)
class FactorLifecycleEvent:
    event_id: str
    factor_id: str
    from_state: FactorLifecycle
    to_state: FactorLifecycle
    occurred_at_utc: str
    operator_id: str
    evidence_refs: tuple[str, ...]
    replacement_factor_id: str | None = None

    def __post_init__(self) -> None:
        for field_name in ("event_id", "factor_id", "operator_id"):
            object.__setattr__(
                self,
                field_name,
                require_identifier(getattr(self, field_name), field_name),
            )
        try:
            object.__setattr__(self, "from_state", FactorLifecycle(self.from_state))
            object.__setattr__(self, "to_state", FactorLifecycle(self.to_state))
        except (TypeError, ValueError) as exc:
            raise ValueError("lifecycle event state is invalid") from exc
        object.__setattr__(
            self,
            "occurred_at_utc",
            require_utc_timestamp(self.occurred_at_utc, "occurred_at_utc"),
        )
        object.__setattr__(
            self,
            "evidence_refs",
            normalize_identifiers(self.evidence_refs, "evidence_refs", required=True),
        )
        if self.replacement_factor_id is not None:
            replacement = require_identifier(
                self.replacement_factor_id, "replacement_factor_id"
            )
            if replacement == self.factor_id:
                raise ValueError("replacement factor cannot equal factor")
            object.__setattr__(self, "replacement_factor_id", replacement)
        if self.to_state is not FactorLifecycle.RETIRED and (
            self.replacement_factor_id is not None
        ):
            raise ValueError("replacement factor is allowed only for retirement")


@dataclass(frozen=True)
class FactorRegistry:
    definitions: Mapping[str, FactorDefinition] = MappingProxyType({})
    lifecycle_events: tuple[FactorLifecycleEvent, ...] = ()

    def __post_init__(self) -> None:
        normalized: dict[str, FactorDefinition] = {}
        for key, definition in self.definitions.items():
            if not isinstance(definition, FactorDefinition):
                raise ValueError("factor registry accepts FactorDefinition only")
            factor_id = require_identifier(key, "factor registry key")
            if factor_id != definition.factor_id:
                raise ValueError("factor registry key does not match definition")
            normalized[factor_id] = definition
        events = tuple(self.lifecycle_events)
        if not all(isinstance(event, FactorLifecycleEvent) for event in events):
            raise ValueError("invalid lifecycle event")
        if len({event.event_id for event in events}) != len(events):
            raise ValueError("lifecycle event ids must be unique")
        object.__setattr__(
            self,
            "definitions",
            MappingProxyType(dict(sorted(normalized.items()))),
        )
        object.__setattr__(self, "lifecycle_events", events)

    def register(self, definition: FactorDefinition) -> FactorRegistry:
        if not isinstance(definition, FactorDefinition):
            raise ValueError("definition must be FactorDefinition")
        if definition.factor_id in self.definitions:
            raise ValueError("factor id is already registered")
        if definition.lifecycle is not FactorLifecycle.DRAFT:
            raise ValueError("new factors must enter the registry as DRAFT")
        missing_dependencies = set(definition.dependency_factor_ids).difference(
            self.definitions
        )
        if missing_dependencies:
            raise ValueError("factor dependency is not registered")
        updated = dict(self.definitions)
        updated[definition.factor_id] = definition
        return FactorRegistry(updated, self.lifecycle_events)

    def current_lifecycle(self, factor_id: str) -> FactorLifecycle:
        normalized = require_identifier(factor_id, "factor_id")
        if normalized not in self.definitions:
            raise KeyError(normalized)
        lifecycle = self.definitions[normalized].lifecycle
        for event in self.lifecycle_events:
            if event.factor_id == normalized:
                lifecycle = event.to_state
        return lifecycle

    def transition(self, event: FactorLifecycleEvent) -> FactorRegistry:
        if event.factor_id not in self.definitions:
            raise ValueError("factor is not registered")
        if any(item.event_id == event.event_id for item in self.lifecycle_events):
            raise ValueError("lifecycle event id is already registered")
        current = self.current_lifecycle(event.factor_id)
        if event.from_state is not current:
            raise ValueError("lifecycle event does not start at current state")
        if event.to_state not in _ALLOWED_TRANSITIONS[current]:
            raise ValueError("factor lifecycle transition is not allowed")
        definition = self.definitions[event.factor_id]
        if event.to_state in (
            FactorLifecycle.QUALIFIED,
            FactorLifecycle.CHAMPION,
        ) and (
            definition.validation_status is not ValidationStatus.VALIDATED
            or definition.approved_by == "NONE"
        ):
            raise ValueError("qualification requires validation and approval")
        prior_times = (
            parse_utc_timestamp(item.occurred_at_utc)
            for item in self.lifecycle_events
            if item.factor_id == event.factor_id
        )
        if any(
            parse_utc_timestamp(event.occurred_at_utc) < prior_time
            for prior_time in prior_times
        ):
            raise ValueError("lifecycle events must be time ordered")
        if parse_utc_timestamp(event.occurred_at_utc) < parse_utc_timestamp(
            definition.effective_at_utc
        ):
            raise ValueError("lifecycle event precedes factor effective time")
        if event.replacement_factor_id is not None and (
            event.replacement_factor_id not in self.definitions
        ):
            raise ValueError("replacement factor is not registered")
        return FactorRegistry(self.definitions, self.lifecycle_events + (event,))

    def effective_definition(self, factor_id: str) -> FactorDefinition:
        normalized = require_identifier(factor_id, "factor_id")
        definition = self.definitions[normalized]
        lifecycle = self.current_lifecycle(normalized)
        status = definition.champion_challenger_status
        if lifecycle is FactorLifecycle.CHALLENGER:
            status = ChampionChallengerStatus.CHALLENGER
        elif lifecycle is FactorLifecycle.CHAMPION:
            status = ChampionChallengerStatus.CHAMPION
        elif status is not ChampionChallengerStatus.UNASSIGNED:
            status = ChampionChallengerStatus.UNASSIGNED
        retired_at = definition.retired_at_utc
        replacement = definition.replacement_factor_id
        if lifecycle is FactorLifecycle.RETIRED:
            retirement = next(
                event
                for event in reversed(self.lifecycle_events)
                if event.factor_id == normalized
                and event.to_state is FactorLifecycle.RETIRED
            )
            retired_at = retirement.occurred_at_utc
            replacement = retirement.replacement_factor_id
        return replace(
            definition,
            lifecycle=lifecycle,
            champion_challenger_status=status,
            retired_at_utc=retired_at,
            replacement_factor_id=replacement,
        )


@dataclass(frozen=True)
class ForecastTargetRegistry:
    definitions: Mapping[str, ForecastTargetDefinition] = MappingProxyType({})

    def __post_init__(self) -> None:
        normalized: dict[str, ForecastTargetDefinition] = {}
        for key, definition in self.definitions.items():
            if not isinstance(definition, ForecastTargetDefinition):
                raise ValueError("target registry accepts ForecastTargetDefinition only")
            target_id = require_identifier(key, "forecast target registry key")
            if target_id != definition.target_id:
                raise ValueError("forecast target key does not match definition")
            normalized[target_id] = definition
        object.__setattr__(
            self,
            "definitions",
            MappingProxyType(dict(sorted(normalized.items()))),
        )

    def register(
        self, definition: ForecastTargetDefinition
    ) -> ForecastTargetRegistry:
        if not isinstance(definition, ForecastTargetDefinition):
            raise ValueError("definition must be ForecastTargetDefinition")
        if definition.target_id in self.definitions:
            raise ValueError("forecast target id is already registered")
        updated = dict(self.definitions)
        updated[definition.target_id] = definition
        return ForecastTargetRegistry(updated)
