import hashlib
import json
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from apps.v2_r2_historical_factor_baseline_app_1.contracts import utc

from .contracts import FactorDefinition, FactorRegistryPolicy


@dataclass(frozen=True)
class FactorRegistryEvidence:
    registry_id: str
    registry_version: str
    state: str
    definition_keys: tuple[str, ...]
    definition_hashes: Mapping[str, str]
    reason_codes: tuple[str, ...]
    evaluated_at_utc: str
    operator_review_required: bool
    evidence_hash: str

    def __post_init__(self) -> None:
        if self.state not in {"REGISTRY_READY", "BLOCKED"}:
            raise ValueError("invalid factor registry evidence state")
        if self.operator_review_required is not True:
            raise ValueError("factor registry evidence requires Operator review")
        if len(self.evidence_hash) != 64 or any(
            character not in "0123456789abcdef" for character in self.evidence_hash
        ):
            raise ValueError("evidence_hash must be lowercase SHA-256")
        object.__setattr__(
            self,
            "definition_hashes",
            MappingProxyType(dict(sorted(self.definition_hashes.items()))),
        )


def _definition_payload(definition: FactorDefinition) -> dict[str, object]:
    return {
        "asset_scopes": definition.asset_scopes,
        "calculation_spec_hash": definition.calculation_spec_hash,
        "dependency_factor_refs": definition.dependency_factor_refs,
        "factor_id": definition.factor_id,
        "family": definition.family,
        "input_field_ids": definition.input_field_ids,
        "lifecycle": definition.lifecycle,
        "maximum_lookback": definition.maximum_lookback,
        "minimum_lookback": definition.minimum_lookback,
        "output_unit": definition.output_unit,
        "source_type": definition.source_type,
        "version": definition.version,
    }


def _digest(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def _has_cycle(definitions: tuple[FactorDefinition, ...]) -> bool:
    graph = {
        item.natural_key: tuple(item.dependency_factor_refs) for item in definitions
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> bool:
        if node in visiting:
            return True
        if node in visited:
            return False
        visiting.add(node)
        if any(visit(dependency) for dependency in graph.get(node, ())):
            return True
        visiting.remove(node)
        visited.add(node)
        return False

    return any(visit(node) for node in graph)


def build_factor_registry(
    definitions: tuple[FactorDefinition, ...],
    policy: FactorRegistryPolicy,
    *,
    as_of_utc: str,
) -> FactorRegistryEvidence:
    evaluated = utc(as_of_utc, "as_of_utc")
    ordered = tuple(sorted(definitions, key=lambda item: item.natural_key))
    keys = tuple(item.natural_key for item in ordered)
    key_set = set(keys)
    reasons: list[str] = []
    if not ordered:
        reasons.append("EMPTY_REGISTRY_BLOCKED")
    elif len(ordered) > policy.maximum_definitions:
        reasons.append("REGISTRY_CAPACITY_BLOCKED")
    elif len(key_set) != len(keys):
        reasons.append("DUPLICATE_FACTOR_NATURAL_KEY")
    elif any(item.family not in policy.allowed_families for item in ordered):
        reasons.append("FACTOR_FAMILY_NOT_ALLOWED")
    elif any(item.lifecycle not in policy.allowed_lifecycles for item in ordered):
        reasons.append("FACTOR_LIFECYCLE_NOT_ALLOWED")
    elif not policy.dependencies_allowed and any(item.dependency_factor_refs for item in ordered):
        reasons.append("DEPENDENCIES_NOT_ALLOWED")
    elif any(
        dependency == item.natural_key
        for item in ordered
        for dependency in item.dependency_factor_refs
    ):
        reasons.append("SELF_DEPENDENCY_BLOCKED")
    elif any(
        dependency not in key_set
        for item in ordered
        for dependency in item.dependency_factor_refs
    ):
        reasons.append("UNREGISTERED_DEPENDENCY_BLOCKED")
    elif _has_cycle(ordered):
        reasons.append("DEPENDENCY_CYCLE_BLOCKED")
    else:
        reasons.append("REGISTERED_LOCAL_FACTOR_REGISTRY_READY")
    state = "REGISTRY_READY" if reasons[-1].endswith("READY") else "BLOCKED"
    hashes = {
        item.natural_key: _digest(_definition_payload(item)) for item in ordered
    }
    payload = {
        "definition_hashes": hashes,
        "definition_keys": keys,
        "evaluated_at_utc": evaluated,
        "reason_codes": reasons,
        "registry_id": policy.registry_id,
        "registry_version": policy.registry_version,
        "state": state,
    }
    return FactorRegistryEvidence(
        policy.registry_id,
        policy.registry_version,
        state,
        keys,
        hashes,
        tuple(reasons),
        evaluated,
        True,
        _digest(payload),
    )
