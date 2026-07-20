from __future__ import annotations

import json
from pathlib import Path

from apps.fcp_0012_sanitized_candidate_data_session_evidence_intake_app_1 import (
    load_rqdata_trial_session,
    review_candidate_session_evidence,
)

from .contracts import (
    CandidateEvidenceBundle,
    RegisteredEvidenceReference,
    canonical_json_sha256,
    require_sha256,
)


BUNDLE_REGISTRY = "FCF_REGISTERED_EVIDENCE_FCP_0013_RQDATA_CANDIDATE_BUNDLE.json"


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _load_json(path: Path, *, max_bytes: int = 131072) -> dict[str, object]:
    raw = path.read_bytes()
    if not 1 <= len(raw) <= max_bytes:
        raise ValueError("registered evidence JSON is outside the bounded size")
    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("registered evidence JSON must be ASCII") from exc
    value = json.loads(text, object_pairs_hook=_pairs)
    if not isinstance(value, dict):
        raise ValueError("registered evidence JSON must be an object")
    return value


def _exact_keys(value: dict[str, object], expected: set[str], name: str) -> None:
    if set(value) != expected:
        raise ValueError(f"{name} keys do not match the closed contract")


def load_candidate_evidence_bundle(root: Path) -> CandidateEvidenceBundle:
    registry = _load_json(root / BUNDLE_REGISTRY)
    _exact_keys(
        registry,
        {
            "bundle",
            "evidence_id",
            "network_used_by_sidecar",
            "operator_review_required",
            "provider_selected",
            "retention_state",
            "rights_state",
            "schema_version",
        },
        "bundle registry",
    )
    if registry["schema_version"] != 1 or registry["network_used_by_sidecar"] is not False:
        raise ValueError("bundle registry boundary is invalid")
    if registry["provider_selected"] is not False or registry["operator_review_required"] is not True:
        raise ValueError("bundle registry cannot select a provider")
    bundle = registry["bundle"]
    if not isinstance(bundle, dict):
        raise ValueError("bundle registration must be an object")
    _exact_keys(bundle, {"binding_authority", "bundle_id", "candidate_id", "source_evidence"}, "bundle")
    if bundle["binding_authority"] != "OPERATOR_REGISTERED_LOCAL_EVIDENCE":
        raise ValueError("bundle binding authority is invalid")
    source_rows = bundle["source_evidence"]
    if not isinstance(source_rows, list) or len(source_rows) != 2:
        raise ValueError("bundle must bind exactly two source evidence records")
    sources: dict[str, tuple[dict[str, object], dict[str, object]]] = {}
    for row in source_rows:
        if not isinstance(row, dict):
            raise ValueError("source evidence registration must be an object")
        _exact_keys(row, {"canonical_json_sha256", "evidence_id", "registry_path"}, "source evidence")
        path = root / str(row["registry_path"])
        source = _load_json(path)
        expected_sha = require_sha256(row["canonical_json_sha256"], "canonical_json_sha256")
        if canonical_json_sha256(source) != expected_sha:
            raise ValueError("source evidence canonical digest mismatch")
        if source.get("evidence_id") != row["evidence_id"]:
            raise ValueError("source evidence identity mismatch")
        sources[str(row["evidence_id"])] = (row, source)
    demo_id = "fcp-0007-rqdata-a-share-daily-demo-evidence-v1"
    session_id = "fcp-0012-rqdata-trial-session-evidence-v1"
    if set(sources) != {demo_id, session_id}:
        raise ValueError("bundle source evidence identities are incomplete")
    demo_row, demo = sources[demo_id]
    acceptance = demo.get("acceptance")
    if not isinstance(acceptance, dict) or acceptance.get("schema_state") != "READY_FOR_LOCAL_SCHEMA_REPLAY":
        raise ValueError("registered daily Demo schema evidence is not ready")
    candidate, registration, session = load_rqdata_trial_session(root)
    session_review = review_candidate_session_evidence(candidate, registration, session)
    candidate_id = str(bundle["candidate_id"])
    if candidate.candidate_id != candidate_id:
        raise ValueError("bundle candidate binding does not match session evidence")
    demo_reference = RegisteredEvidenceReference(
        evidence_id=demo_id,
        candidate_id=candidate_id,
        evidence_kind="HISTORICAL_DAILY_DEMO",
        registry_path=str(demo_row["registry_path"]),
        canonical_json_sha256=str(demo_row["canonical_json_sha256"]),
        observed_capabilities=("DAILY_BAR_SCHEMA_REPLAY",),
        observed_from=str(acceptance["date_min"]),
        observed_to=str(acceptance["date_max"]),
        finding_codes=tuple(sorted(str(value) for value in acceptance["finding_codes"])),
    )
    session_row, _ = sources[session_id]
    session_reference = RegisteredEvidenceReference(
        evidence_id=session_id,
        candidate_id=candidate_id,
        evidence_kind="TRIAL_SESSION_PROBE",
        registry_path=str(session_row["registry_path"]),
        canonical_json_sha256=str(session_row["canonical_json_sha256"]),
        observed_capabilities=("DAILY_BAR_READ_ONLY_PROBE",),
        observed_from=str(session.probe.first_date),
        observed_to=str(session.probe.last_date),
        finding_codes=("QUOTA_OBSERVED", "TRIAL_LICENSE_OBSERVED"),
    )
    return CandidateEvidenceBundle(
        bundle_id=str(bundle["bundle_id"]),
        evidence_id=str(registry["evidence_id"]),
        candidate_id=candidate_id,
        references=tuple(sorted((demo_reference, session_reference), key=lambda item: item.evidence_id)),
        missing_evidence_categories=session_review.missing_evidence_categories,
        missing_fields_by_kind=session_review.missing_fields_by_kind,
        license_class=session.license_class,
        remaining_days=session.remaining_days,
        rights_state=str(registry["rights_state"]),
        retention_state=str(registry["retention_state"]),
    )
