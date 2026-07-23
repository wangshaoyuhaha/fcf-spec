from __future__ import annotations

import hashlib
import json

from apps.v2_r11_local_factor_registry_foundation_app_1.contracts import (
    FactorDefinition,
    FactorRegistryPolicy,
)
from apps.v2_r11_local_factor_registry_foundation_app_1.registry import (
    build_factor_registry,
)

from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    RegisteredFactorArtifact,
    RegisteredFactorRecord,
    RegisteredFactorRuntimeSnapshot,
)


TOP_LEVEL_FIELDS = {
    "definitions",
    "registry_id",
    "registry_version",
    "schema_version",
}
DEFINITION_FIELDS = {
    "asset_scopes",
    "calculation_spec_hash",
    "dependency_factor_refs",
    "effective_at_utc",
    "factor_id",
    "family",
    "input_field_ids",
    "lifecycle",
    "maximum_lookback",
    "minimum_lookback",
    "output_unit",
    "replacement_factor_ref",
    "retired_at_utc",
    "source_type",
    "version",
}


def _closed_object(value: object, fields: set[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{name} must use the closed registered schema")
    return value


def _topological_order(graph: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    remaining = {key: set(value) for key, value in graph.items()}
    ordered: list[str] = []
    while remaining:
        ready = sorted(key for key, dependencies in remaining.items() if not dependencies)
        if not ready:
            raise ValueError("factor dependency graph contains a cycle")
        ordered.extend(ready)
        for key in ready:
            remaining.pop(key)
        for dependencies in remaining.values():
            dependencies.difference_update(ready)
    return tuple(ordered)


def _invalidation_closure(
    retired: tuple[str, ...],
    reverse_graph: dict[str, tuple[str, ...]],
) -> tuple[str, ...]:
    invalidated = set(retired)
    pending = list(retired)
    while pending:
        dependency = pending.pop()
        for dependent in reverse_graph[dependency]:
            if dependent not in invalidated:
                invalidated.add(dependent)
                pending.append(dependent)
    return tuple(sorted(invalidated))


def load_registered_factor_registry(
    content: bytes,
    artifact: RegisteredFactorArtifact,
    *,
    observed_at_utc: str,
) -> RegisteredFactorRuntimeSnapshot:
    if type(content) is not bytes:
        raise TypeError("content must be exact bytes")
    if len(content) != artifact.byte_length:
        raise ValueError("registered factor artifact byte length mismatch")
    if hashlib.sha256(content).hexdigest() != artifact.artifact_hash:
        raise ValueError("registered factor artifact hash mismatch")
    try:
        payload = json.loads(content.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("registered factor artifact must be ASCII JSON") from exc
    payload = _closed_object(payload, TOP_LEVEL_FIELDS, "registry")
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError("registered factor schema version mismatch")
    definitions = payload["definitions"]
    if type(definitions) is not list or not definitions:
        raise ValueError("registry definitions must be a nonempty list")

    records: list[RegisteredFactorRecord] = []
    for raw in definitions:
        item = _closed_object(raw, DEFINITION_FIELDS, "factor definition")
        definition = FactorDefinition(
            factor_id=item["factor_id"],
            version=item["version"],
            family=item["family"],
            lifecycle=item["lifecycle"],
            source_type=item["source_type"],
            calculation_spec_hash=item["calculation_spec_hash"],
            output_unit=item["output_unit"],
            asset_scopes=tuple(item["asset_scopes"]),
            input_field_ids=tuple(item["input_field_ids"]),
            dependency_factor_refs=tuple(item["dependency_factor_refs"]),
            minimum_lookback=item["minimum_lookback"],
            maximum_lookback=item["maximum_lookback"],
        )
        records.append(
            RegisteredFactorRecord(
                definition=definition,
                effective_at_utc=item["effective_at_utc"],
                retired_at_utc=item["retired_at_utc"],
                replacement_factor_ref=item["replacement_factor_ref"],
            )
        )

    ordered = tuple(sorted(records, key=lambda record: record.definition.natural_key))
    keys = tuple(record.definition.natural_key for record in ordered)
    if len(set(keys)) != len(keys):
        raise ValueError("registered factor natural keys must be unique")
    key_set = set(keys)
    graph = {
        record.definition.natural_key: record.definition.dependency_factor_refs
        for record in ordered
    }
    if any(dependency not in key_set for dependencies in graph.values() for dependency in dependencies):
        raise ValueError("factor dependencies must be registered in the same artifact")
    reverse = {
        key: tuple(sorted(node for node, dependencies in graph.items() if key in dependencies))
        for key in keys
    }
    replacements = {
        record.definition.natural_key: record.replacement_factor_ref
        for record in ordered
        if record.replacement_factor_ref is not None
    }
    if any(value not in key_set for value in replacements.values()):
        raise ValueError("replacement factor must be registered in the same artifact")

    policy = FactorRegistryPolicy(
        registry_id=payload["registry_id"],
        registry_version=payload["registry_version"],
    )
    evidence = build_factor_registry(
        tuple(record.definition for record in ordered),
        policy,
        as_of_utc=observed_at_utc,
    )
    if evidence.state != "REGISTRY_READY":
        raise ValueError("registered factor foundation rejected the artifact")
    topological_order = _topological_order(graph)
    retired = tuple(
        sorted(
            record.definition.natural_key
            for record in ordered
            if record.definition.lifecycle == "RETIRED"
        )
    )
    invalidated = _invalidation_closure(retired, reverse)
    return RegisteredFactorRuntimeSnapshot(
        artifact_id=artifact.artifact_id,
        artifact_hash=artifact.artifact_hash,
        registry_id=policy.registry_id,
        registry_version=policy.registry_version,
        record_hashes={
            record.definition.natural_key: record.record_hash for record in ordered
        },
        dependency_graph=graph,
        reverse_dependency_graph=reverse,
        topological_order=topological_order,
        retired_factor_refs=retired,
        invalidated_factor_refs=invalidated,
        replacement_map=replacements,
        observed_at_utc=observed_at_utc,
    )
