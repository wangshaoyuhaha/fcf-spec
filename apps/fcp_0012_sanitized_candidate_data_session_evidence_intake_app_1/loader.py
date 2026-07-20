from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .contracts import (
    FORBIDDEN_KEY_FRAGMENTS,
    CandidateSessionEvidence,
    ReadOnlyProbeEvidence,
    RegisteredSessionEvidenceArtifact,
)


TOP_LEVEL_KEYS = frozenset(
    {
        "candidate_id",
        "captured_at_utc",
        "license_class",
        "probe",
        "quota_limit_bytes",
        "quota_used_bytes",
        "remaining_days",
    }
)
PROBE_KEYS = frozenset(
    {
        "first_date",
        "instrument_count",
        "kind",
        "last_date",
        "row_count",
        "status",
    }
)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("sanitized session JSON contains a duplicate key")
        result[key] = value
    return result


def _reject_secret_keys(value: object) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("_", "-")
            if any(fragment in normalized for fragment in FORBIDDEN_KEY_FRAGMENTS):
                raise ValueError("sanitized session JSON contains a forbidden key")
            _reject_secret_keys(child)
    elif isinstance(value, list):
        for child in value:
            _reject_secret_keys(child)


def _integer(value: object, field_name: str) -> int:
    if type(value) is not int:
        raise ValueError(f"{field_name} must be an integer")
    return value


def load_registered_session_evidence(
    file_path: str | Path,
    registration: RegisteredSessionEvidenceArtifact,
) -> CandidateSessionEvidence:
    if not isinstance(registration, RegisteredSessionEvidenceArtifact):
        raise TypeError("registration must be RegisteredSessionEvidenceArtifact")
    path = Path(file_path)
    if path.name != registration.artifact_path or not path.is_file():
        raise FileNotFoundError("registered sanitized session artifact is unavailable")
    raw = path.read_bytes()
    if len(raw) != registration.byte_length:
        raise ValueError("registered session byte length mismatch")
    source_sha256 = hashlib.sha256(raw).hexdigest()
    if source_sha256 != registration.artifact_sha256:
        raise ValueError("registered session SHA-256 mismatch")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("registered session artifact must be ASCII JSON") from exc
    try:
        payload = json.loads(text, object_pairs_hook=_unique_object)
    except json.JSONDecodeError as exc:
        raise ValueError("registered session artifact must be valid JSON") from exc
    if not isinstance(payload, dict) or frozenset(payload) != TOP_LEVEL_KEYS:
        raise ValueError("registered session top-level schema is not exact")
    _reject_secret_keys(payload)
    probe = payload["probe"]
    if not isinstance(probe, dict) or frozenset(probe) != PROBE_KEYS:
        raise ValueError("registered session probe schema is not exact")
    evidence = CandidateSessionEvidence(
        candidate_id=payload["candidate_id"],
        captured_at_utc=payload["captured_at_utc"],
        license_class=payload["license_class"],
        remaining_days=_integer(payload["remaining_days"], "remaining_days"),
        quota_limit_bytes=_integer(payload["quota_limit_bytes"], "quota_limit_bytes"),
        quota_used_bytes=_integer(payload["quota_used_bytes"], "quota_used_bytes"),
        probe=ReadOnlyProbeEvidence(
            kind=probe["kind"],
            status=probe["status"],
            instrument_count=_integer(probe["instrument_count"], "instrument_count"),
            row_count=_integer(probe["row_count"], "row_count"),
            first_date=probe["first_date"],
            last_date=probe["last_date"],
        ),
        source_sha256=source_sha256,
    )
    if evidence.candidate_id != registration.candidate_id:
        raise ValueError("registered session candidate identity mismatch")
    return evidence
