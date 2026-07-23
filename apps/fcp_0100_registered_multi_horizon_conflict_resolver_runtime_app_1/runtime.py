from __future__ import annotations

import hashlib
import json

from .contracts import (
    RESULT_GROUPS,
    RUNTIME_SCHEMA_VERSION,
    RegisteredConflictArtifact,
    RegisteredConflictSet,
    RegisteredConflictSnapshot,
    RegisteredHorizonResult,
    instant,
    utc,
)


TOP_LEVEL_FIELDS = {
    "conflict_sets",
    "registry_id",
    "registry_version",
    "schema_version",
}
SET_FIELDS = {
    "conflict_set_id",
    "instrument_id",
    "market_id",
    "results",
    "thesis_direction",
}
RESULT_FIELDS = {
    "available_at_utc",
    "correlation_id",
    "evidence_hashes",
    "evidence_state",
    "expires_at_utc",
    "hard_risk_block",
    "horizon_id",
    "invalidation_ids",
    "result_id",
    "signal_direction",
    "state_hash",
}


def _closed(value: object, fields: set[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{name} must use the closed registered schema")
    return value


def _group(
    result: RegisteredHorizonResult,
    thesis_direction: str,
    as_of_utc: str,
) -> str:
    if result.hard_risk_block or result.evidence_state == "BLOCKED":
        return "BLOCKED"
    if result.evidence_state == "MISSING":
        return "MISSING"
    if result.evidence_state == "STALE" or instant(as_of_utc) >= instant(
        result.expires_at_utc
    ):
        return "STALE"
    if result.signal_direction in {"NEUTRAL", "UNKNOWN"}:
        return "NEUTRAL"
    if result.signal_direction == thesis_direction:
        return "SUPPORTING"
    return "OPPOSING"


def load_registered_conflict_registry(
    content: bytes,
    artifact: RegisteredConflictArtifact,
    *,
    as_of_utc: str,
) -> RegisteredConflictSnapshot:
    if type(content) is not bytes:
        raise TypeError("content must be exact bytes")
    if len(content) != artifact.byte_length:
        raise ValueError("registered conflict artifact byte length mismatch")
    if hashlib.sha256(content).hexdigest() != artifact.artifact_hash:
        raise ValueError("registered conflict artifact hash mismatch")
    try:
        payload = json.loads(content.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("registered conflict artifact must be ASCII JSON") from exc
    payload = _closed(payload, TOP_LEVEL_FIELDS, "registry")
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError("registered conflict schema version mismatch")
    raw_sets = payload["conflict_sets"]
    if type(raw_sets) is not list or not raw_sets:
        raise ValueError("conflict registry must be a nonempty list")
    sets = []
    for raw_set in raw_sets:
        conflict_set = _closed(raw_set, SET_FIELDS, "conflict set")
        raw_results = conflict_set["results"]
        if type(raw_results) is not list:
            raise ValueError("conflict results must be a list")
        sets.append(
            RegisteredConflictSet(
                **{
                    **conflict_set,
                    "results": tuple(
                        RegisteredHorizonResult(
                            **{
                                **_closed(raw, RESULT_FIELDS, "horizon result"),
                                "evidence_hashes": tuple(raw["evidence_hashes"]),
                                "invalidation_ids": tuple(raw["invalidation_ids"]),
                            }
                        )
                        for raw in raw_results
                    ),
                }
            )
        )
    if len({item.conflict_set_id for item in sets}) != len(sets):
        raise ValueError("conflict set identities must be unique")
    if len({item.set_hash for item in sets}) != len(sets):
        raise ValueError("conflict set hashes must be unique")
    as_of = utc(as_of_utc, "as_of_utc")
    if any(
        instant(as_of) < instant(result.available_at_utc)
        for item in sets
        for result in item.results
    ):
        raise ValueError("as_of_utc cannot precede registered availability")
    grouped: dict[str, dict[str, tuple[str, ...]]] = {}
    rows: dict[str, tuple[tuple[str, str, str], ...]] = {}
    conflicting = []
    for item in sets:
        buckets: dict[str, list[str]] = {group: [] for group in RESULT_GROUPS}
        view_rows = []
        for result in item.results:
            group = _group(result, item.thesis_direction, as_of)
            buckets[group].append(result.result_id)
            view_rows.append((result.horizon_id, group, result.result_id))
        grouped[item.conflict_set_id] = {
            group: tuple(buckets[group]) for group in RESULT_GROUPS
        }
        rows[item.conflict_set_id] = tuple(view_rows)
        if buckets["SUPPORTING"] and buckets["OPPOSING"]:
            conflicting.append(item.conflict_set_id)
    return RegisteredConflictSnapshot(
        artifact_id=artifact.artifact_id,
        artifact_hash=artifact.artifact_hash,
        registry_id=payload["registry_id"],
        registry_version=payload["registry_version"],
        set_hashes={item.conflict_set_id: item.set_hash for item in sets},
        grouped_result_ids=grouped,
        presentation_rows=rows,
        conflicting_set_ids=tuple(conflicting),
        as_of_utc=as_of,
    )
