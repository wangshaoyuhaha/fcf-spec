from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
)
from apps.fcp_0022_btc_local_export_canonicalization_bridge_app_1 import (
    canonicalize_registered_btc_local_export,
)

from .contracts import (
    OBSERVATION_KINDS,
    BTCLocalExportValidationRequest,
    BTCLocalExportValidationResult,
)


def validate_registered_btc_local_export(
    file_path: str | Path,
    request: BTCLocalExportValidationRequest,
) -> BTCLocalExportValidationResult:
    if not isinstance(request, BTCLocalExportValidationRequest):
        raise TypeError("request must be BTCLocalExportValidationRequest")
    path = Path(file_path)
    if path.is_symlink():
        raise ValueError("registered BTC local export must not be a symlink")
    if not path.is_file():
        raise FileNotFoundError("registered BTC local export is not a regular file")
    if path.stat().st_size != request.registration.byte_length:
        raise ValueError("registered BTC local export byte length mismatch")

    bridge = canonicalize_registered_btc_local_export(
        path,
        request.registration,
        request.profile,
        output_artifact_id=request.output_artifact_id,
        as_of_utc=request.as_of_utc,
    )
    headers = tuple(item.header for item in bridge.observations)
    counts = Counter(item.observation_kind for item in headers)
    sequences = tuple(item.source_sequence for item in headers)
    event_times = tuple(item.event_at_utc for item in headers)
    received_times = tuple(item.received_at_utc for item in headers)
    ingested_times = tuple(item.ingested_at_utc for item in headers)
    return BTCLocalExportValidationResult(
        source_artifact_id=request.registration.artifact_id,
        source_artifact_sha256=request.registration.content_sha256,
        source_byte_length=request.registration.byte_length,
        canonical_artifact_id=bridge.canonical_registration.artifact_id,
        canonical_artifact_sha256=bridge.canonical_registration.content_sha256,
        canonical_byte_length=bridge.canonical_registration.byte_length,
        profile_hash=bridge.manifest.profile_hash,
        manifest_hash=bridge.manifest.manifest_hash,
        observation_hashes_sha256=canonical_sha256(
            list(bridge.manifest.observation_hashes)
        ),
        observation_count=len(headers),
        observation_kind_counts=tuple((kind, counts[kind]) for kind in OBSERVATION_KINDS),
        sequence_min=min(sequences),
        sequence_max=max(sequences),
        event_start_utc=min(event_times),
        event_end_utc=max(event_times),
        received_start_utc=min(received_times),
        received_end_utc=max(received_times),
        ingested_start_utc=min(ingested_times),
        ingested_end_utc=max(ingested_times),
        as_of_utc=request.as_of_utc,
        quality_state=bridge.quality_state,
        operator_review_required=bridge.operator_review_required,
    )


def render_validation_json(result: BTCLocalExportValidationResult) -> str:
    if not isinstance(result, BTCLocalExportValidationResult):
        raise TypeError("result must be BTCLocalExportValidationResult")
    return json.dumps(
        result.to_record(),
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ) + "\n"


def build_reference_result() -> BTCLocalExportValidationResult:
    return BTCLocalExportValidationResult(
        source_artifact_id="btc-source-reference-v1",
        source_artifact_sha256=canonical_sha256("source-reference"),
        source_byte_length=1_000,
        canonical_artifact_id="btc-canonical-reference-v1",
        canonical_artifact_sha256=canonical_sha256("canonical-reference"),
        canonical_byte_length=1_200,
        profile_hash=canonical_sha256("profile-reference"),
        manifest_hash=canonical_sha256("manifest-reference"),
        observation_hashes_sha256=canonical_sha256("observation-reference"),
        observation_count=5,
        observation_kind_counts=tuple((kind, 1) for kind in OBSERVATION_KINDS),
        sequence_min=1,
        sequence_max=101,
        event_start_utc="2026-07-21T00:00:09Z",
        event_end_utc="2026-07-21T00:00:09Z",
        received_start_utc="2026-07-21T00:00:10Z",
        received_end_utc="2026-07-21T00:00:10Z",
        ingested_start_utc="2026-07-21T00:00:10Z",
        ingested_end_utc="2026-07-21T00:00:10Z",
        as_of_utc="2026-07-21T00:00:20Z",
    )
