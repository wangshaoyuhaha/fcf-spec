from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from apps.ai_comprehensive_report_integration_app_1 import (
    SOURCE_APP_ID,
    SOURCE_ARTIFACT_TYPE,
    SOURCE_MODULE,
    build_registered_source_envelope,
    canonical_payload_sha256,
    load_registered_source_from_file,
    load_registered_source_from_mapping,
    validate_registered_source_envelope,
)


def sample_payload() -> dict[str, object]:
    return {
        "report_id": "report-001",
        "correlation_id": "corr-001",
        "risk_flags": ["REVIEW_REQUIRED"],
        "uncertainty_states": ["UNRESOLVED"],
        "original_conclusions": ["NO_AUTOMATIC_CONCLUSION"],
        "operator_review_required": True,
    }


def sample_envelope() -> dict[str, object]:
    return build_registered_source_envelope(
        source_payload=sample_payload(),
        source_artifact_ref=(
            "artifacts/ai_comprehensive_report_synthesis/"
            "report-001.json"
        ),
        source_artifact_version="1.0.0",
        correlation_id="corr-001",
    )


def test_d2_imports_completed_synthesis_package() -> None:
    assert SOURCE_MODULE == "apps.ai_comprehensive_report_synthesis_app_1"


def test_d2_source_identity_constants_are_exact() -> None:
    assert SOURCE_APP_ID == "AI-COMPREHENSIVE-REPORT-SYNTHESIS-APP-1"
    assert (
        SOURCE_ARTIFACT_TYPE
        == "comprehensive_report_synthesis_packet"
    )


def test_d2_canonical_hash_is_deterministic() -> None:
    first = {
        "b": 2,
        "a": 1,
    }
    second = {
        "a": 1,
        "b": 2,
    }

    assert canonical_payload_sha256(first) == canonical_payload_sha256(
        second
    )


def test_d2_builds_registered_source_envelope() -> None:
    envelope = sample_envelope()

    assert envelope["source_app_id"] == SOURCE_APP_ID
    assert envelope["source_module"] == SOURCE_MODULE
    assert envelope["source_artifact_type"] == SOURCE_ARTIFACT_TYPE
    assert envelope["source_artifact_version"] == "1.0.0"
    assert envelope["correlation_id"] == "corr-001"
    assert envelope["operator_review_required"] is True
    assert envelope["source_sha256"] == canonical_payload_sha256(
        sample_payload()
    )


def test_d2_valid_envelope_passes_exact_locks() -> None:
    envelope = sample_envelope()

    result = validate_registered_source_envelope(
        envelope,
        expected_source_artifact_ref=envelope["source_artifact_ref"],
        expected_source_artifact_version="1.0.0",
        expected_correlation_id="corr-001",
        expected_source_sha256=envelope["source_sha256"],
    )

    assert result["ok"] is True
    assert result["errors"] == []
    assert result["source_mutation_performed"] is False
    assert result["runtime_execution_performed"] is False
    assert result["real_execution_performed"] is False


def test_d2_mapping_loader_preserves_input() -> None:
    envelope = sample_envelope()
    original = deepcopy(envelope)

    result = load_registered_source_from_mapping(envelope)

    assert result["ok"] is True
    assert result["registered_source"] == original
    assert result["registered_source"] is not envelope
    assert envelope == original


def test_d2_rejects_artifact_reference_lock_mismatch() -> None:
    envelope = sample_envelope()

    result = validate_registered_source_envelope(
        envelope,
        expected_source_artifact_ref="artifacts/wrong.json",
    )

    assert result["ok"] is False
    assert "SOURCE_ARTIFACT_REF_LOCK_MISMATCH" in result["errors"]


def test_d2_rejects_version_lock_mismatch() -> None:
    envelope = sample_envelope()

    result = validate_registered_source_envelope(
        envelope,
        expected_source_artifact_version="2.0.0",
    )

    assert result["ok"] is False
    assert "SOURCE_ARTIFACT_VERSION_LOCK_MISMATCH" in result["errors"]


def test_d2_rejects_correlation_id_lock_mismatch() -> None:
    envelope = sample_envelope()

    result = validate_registered_source_envelope(
        envelope,
        expected_correlation_id="corr-wrong",
    )

    assert result["ok"] is False
    assert "CORRELATION_ID_LOCK_MISMATCH" in result["errors"]


def test_d2_rejects_sha256_lock_mismatch() -> None:
    envelope = sample_envelope()

    result = validate_registered_source_envelope(
        envelope,
        expected_source_sha256="0" * 64,
    )

    assert result["ok"] is False
    assert "SOURCE_SHA256_LOCK_MISMATCH" in result["errors"]


def test_d2_rejects_payload_hash_tampering() -> None:
    envelope = sample_envelope()
    envelope["source_payload"]["risk_flags"] = []

    result = validate_registered_source_envelope(envelope)

    assert result["ok"] is False
    assert "SOURCE_SHA256_MISMATCH" in result["errors"]


def test_d2_rejects_removed_operator_review_requirement() -> None:
    envelope = sample_envelope()
    envelope["operator_review_required"] = False

    result = validate_registered_source_envelope(envelope)

    assert result["ok"] is False
    assert "OPERATOR_REVIEW_REQUIREMENT_REMOVED" in result["errors"]


def test_d2_rejects_network_source_reference() -> None:
    envelope = sample_envelope()
    envelope["source_artifact_ref"] = "https://example.test/report.json"

    result = validate_registered_source_envelope(envelope)

    assert result["ok"] is False
    assert "NON_LOCAL_SOURCE_ARTIFACT_REF" in result["errors"]


def test_d2_loads_local_json_source_file(tmp_path: Path) -> None:
    envelope = sample_envelope()
    source_file = tmp_path / "registered_source.json"
    source_file.write_text(
        json.dumps(envelope, sort_keys=True),
        encoding="utf-8",
    )

    result = load_registered_source_from_file(
        source_file,
        expected_source_artifact_ref=envelope["source_artifact_ref"],
        expected_source_artifact_version="1.0.0",
        expected_correlation_id="corr-001",
        expected_source_sha256=envelope["source_sha256"],
    )

    assert result["ok"] is True
    assert result["source_file"] == str(source_file)
    assert result["source_file_mode"] == "LOCAL_READ_ONLY_JSON"
    assert result["registered_source"] == envelope


def test_d2_rejects_invalid_json_file(tmp_path: Path) -> None:
    source_file = tmp_path / "invalid.json"
    source_file.write_text("{invalid", encoding="utf-8")

    result = load_registered_source_from_file(source_file)

    assert result["ok"] is False
    assert result["errors"] == ["INVALID_SOURCE_FILE"]


def test_d2_rejects_non_object_json_root(tmp_path: Path) -> None:
    source_file = tmp_path / "list.json"
    source_file.write_text("[]", encoding="utf-8")

    result = load_registered_source_from_file(source_file)

    assert result["ok"] is False
    assert result["errors"] == ["SOURCE_FILE_ROOT_NOT_OBJECT"]


def test_d2_rejects_missing_source_file(tmp_path: Path) -> None:
    result = load_registered_source_from_file(
        tmp_path / "missing.json"
    )

    assert result["ok"] is False
    assert result["errors"] == ["SOURCE_FILE_NOT_FOUND"]
