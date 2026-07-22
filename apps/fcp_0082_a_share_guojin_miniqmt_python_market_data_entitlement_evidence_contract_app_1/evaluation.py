from __future__ import annotations

import hashlib
import json
from datetime import datetime

from .contracts import (
    EVIDENCE_FIELDS,
    MiniQMTEntitlementEvidence,
    MiniQMTEntitlementReviewPacket,
    RegisteredEntitlementEvidenceArtifact,
    reject_secret_keys,
)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key is forbidden")
        result[key] = value
    return result


def load_sanitized_evidence(
    artifact: RegisteredEntitlementEvidenceArtifact,
    raw_bytes: bytes,
) -> MiniQMTEntitlementEvidence:
    if len(raw_bytes) != artifact.byte_length:
        raise ValueError("artifact byte length mismatch")
    if hashlib.sha256(raw_bytes).hexdigest() != artifact.artifact_sha256:
        raise ValueError("artifact SHA-256 mismatch")
    try:
        text = raw_bytes.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("artifact must be ASCII") from exc
    payload = json.loads(text, object_pairs_hook=_unique_object)
    if not isinstance(payload, dict):
        raise ValueError("artifact root must be an object")
    reject_secret_keys(payload)
    if tuple(sorted(payload)) != EVIDENCE_FIELDS:
        raise ValueError("artifact fields must match the closed schema")
    return MiniQMTEntitlementEvidence(**payload)


def evaluate_evidence(
    artifact: RegisteredEntitlementEvidenceArtifact,
    evidence: MiniQMTEntitlementEvidence,
    *,
    as_of_utc: str,
    required_markets: tuple[str, ...] = ("SSE", "SZSE"),
    required_capabilities: tuple[str, ...] = ("DAILY_BAR", "MINUTE_BAR"),
) -> MiniQMTEntitlementReviewPacket:
    now = datetime.fromisoformat(as_of_utc.replace("Z", "+00:00"))
    if not as_of_utc.endswith("Z") or now.utcoffset() is None or now.utcoffset().total_seconds() != 0:
        raise ValueError("as_of_utc must be UTC")
    blockers: list[str] = []
    if evidence.entitlement_declared_state != "GRANTED":
        blockers.append("ENTITLEMENT_NOT_DECLARED_GRANTED")
    if evidence.probe_status != "SUCCEEDED":
        blockers.append("READ_ONLY_PROBE_NOT_SUCCEEDED")
    if evidence.rights_state != "DOCUMENTED":
        blockers.append("RIGHTS_NOT_DOCUMENTED")
    if evidence.retention_state != "DOCUMENTED":
        blockers.append("RETENTION_NOT_DOCUMENTED")
    for market in required_markets:
        if market not in evidence.markets:
            blockers.append(f"MISSING_MARKET_{market}")
    for capability in required_capabilities:
        if capability not in evidence.capabilities:
            blockers.append(f"MISSING_CAPABILITY_{capability}")
    if evidence.expires_at_utc is None:
        blockers.append("EXPIRY_NOT_DECLARED")
    else:
        expiry = datetime.fromisoformat(evidence.expires_at_utc.replace("Z", "+00:00"))
        if expiry <= now:
            blockers.append("EVIDENCE_EXPIRED")
    decision = "OPERATOR_REVIEW_ELIGIBLE" if not blockers else "INSUFFICIENT_EVIDENCE"
    return MiniQMTEntitlementReviewPacket(
        artifact_id=artifact.artifact_id,
        terminal_product=evidence.terminal_product,
        terminal_version=evidence.terminal_version,
        python_module_name=evidence.python_module_name,
        python_module_version=evidence.python_module_version,
        markets=evidence.markets,
        capabilities=evidence.capabilities,
        observed_entitlement_state=evidence.entitlement_declared_state,
        probe_status=evidence.probe_status,
        blockers=tuple(blockers),
        decision_state=decision,
    )


def build_reference_packet() -> MiniQMTEntitlementReviewPacket:
    artifact = RegisteredEntitlementEvidenceArtifact(
        artifact_id="guojin-miniqmt-entitlement-reference",
        artifact_path="local/registered/miniqmt-entitlement-evidence.json",
        artifact_sha256="1" * 64,
        byte_length=512,
    )
    evidence = MiniQMTEntitlementEvidence(
        terminal_product="GUOJIN_MINIQMT",
        terminal_version="2.1.19.0",
        python_module_name="xtquant",
        python_module_version="1.0.0",
        module_file_sha256="2" * 64,
        entitlement_declared_state="GRANTED",
        markets=("SSE", "SZSE"),
        capabilities=("DAILY_BAR", "MINUTE_BAR"),
        clock_semantics="ASIA_SHANGHAI_EXCHANGE_TIME",
        probe_status="SUCCEEDED",
        rights_state="DOCUMENTED",
        retention_state="DOCUMENTED",
        evidence_revision="reference-v1",
        captured_at_utc="2026-07-23T08:00:00Z",
        expires_at_utc="2026-08-23T08:00:00Z",
        supporting_document_sha256="3" * 64,
    )
    return evaluate_evidence(artifact, evidence, as_of_utc="2026-07-23T08:00:00Z")
