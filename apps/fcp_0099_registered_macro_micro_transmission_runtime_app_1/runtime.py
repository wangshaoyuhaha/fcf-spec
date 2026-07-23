from __future__ import annotations

import hashlib
import json

from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    RegisteredTransmissionArtifact,
    RegisteredTransmissionRecord,
    RegisteredTransmissionSnapshot,
    TransmissionChainNode,
    instant,
    utc,
)


TOP_LEVEL_FIELDS = {
    "registry_id",
    "registry_version",
    "schema_version",
    "transmissions",
}
RECORD_FIELDS = {
    "available_at_utc",
    "causal_truth_claimed",
    "chain",
    "contradicting_evidence_hashes",
    "correlation_id",
    "decay_seconds",
    "expected_value_id",
    "expires_at_utc",
    "horizon_id",
    "hypothesized_direction",
    "invalidation_ids",
    "macro_event_id",
    "mechanism_id",
    "observed_value_id",
    "operator_registered",
    "publication_time_utc",
    "regime_ids",
    "source_evidence_hashes",
    "state_hash",
    "supporting_evidence_hashes",
    "surprise_definition_id",
    "transmission_id",
    "transmission_version",
    "uncertainty_bps",
}
NODE_FIELDS = {"level", "subject_id"}


def _closed(value: object, fields: set[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{name} must use the closed registered schema")
    return value


def load_registered_transmission_registry(
    content: bytes,
    artifact: RegisteredTransmissionArtifact,
    *,
    as_of_utc: str,
) -> RegisteredTransmissionSnapshot:
    if type(content) is not bytes:
        raise TypeError("content must be exact bytes")
    if len(content) != artifact.byte_length:
        raise ValueError("registered transmission artifact byte length mismatch")
    if hashlib.sha256(content).hexdigest() != artifact.artifact_hash:
        raise ValueError("registered transmission artifact hash mismatch")
    try:
        payload = json.loads(content.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("registered transmission artifact must be ASCII JSON") from exc
    payload = _closed(payload, TOP_LEVEL_FIELDS, "registry")
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError("registered transmission schema version mismatch")
    raw_records = payload["transmissions"]
    if type(raw_records) is not list or not raw_records:
        raise ValueError("transmission registry must be a nonempty list")
    records = []
    for raw in raw_records:
        record = _closed(raw, RECORD_FIELDS, "transmission record")
        raw_chain = record["chain"]
        if type(raw_chain) is not list:
            raise ValueError("transmission chain must be a list")
        records.append(
            RegisteredTransmissionRecord(
                **{
                    **record,
                    "chain": tuple(
                        TransmissionChainNode(
                            **_closed(node, NODE_FIELDS, "transmission node")
                        )
                        for node in raw_chain
                    ),
                    "source_evidence_hashes": tuple(
                        record["source_evidence_hashes"]
                    ),
                    "supporting_evidence_hashes": tuple(
                        record["supporting_evidence_hashes"]
                    ),
                    "contradicting_evidence_hashes": tuple(
                        record["contradicting_evidence_hashes"]
                    ),
                    "regime_ids": tuple(record["regime_ids"]),
                    "invalidation_ids": tuple(record["invalidation_ids"]),
                }
            )
        )
    identities = tuple(
        (record.transmission_id, record.transmission_version) for record in records
    )
    if len(set(identities)) != len(identities):
        raise ValueError("transmission identities must be unique")
    if len({record.record_hash for record in records}) != len(records):
        raise ValueError("transmission record hashes must be unique")
    as_of = utc(as_of_utc, "as_of_utc")
    if any(instant(as_of) < instant(record.available_at_utc) for record in records):
        raise ValueError("as_of_utc cannot precede registered availability")
    active = tuple(
        record.transmission_id
        for record in records
        if instant(as_of) < instant(record.expires_at_utc)
    )
    expired = tuple(
        record.transmission_id
        for record in records
        if instant(as_of) >= instant(record.expires_at_utc)
    )
    return RegisteredTransmissionSnapshot(
        artifact_id=artifact.artifact_id,
        artifact_hash=artifact.artifact_hash,
        registry_id=payload["registry_id"],
        registry_version=payload["registry_version"],
        record_hashes={
            record.transmission_id: record.record_hash for record in records
        },
        active_transmission_ids=active,
        expired_transmission_ids=expired,
        chain_subjects={
            record.transmission_id: tuple(
                node.subject_id for node in record.chain
            )
            for record in records
        },
        as_of_utc=as_of,
    )
