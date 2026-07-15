import hashlib
import json
from pathlib import Path

import pytest

from apps.browser_product_console_integration_acceptance_app_1 import (
    BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_BOUNDARY,
    INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY,
    INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX,
)
from apps.browser_product_console_runtime_app_1 import (
    RuntimeHardeningLimits,
    build_browser_console_runtime,
    load_console_artifact_index,
    normalize_registered_relative_path,
    read_runtime_artifact_snapshot,
)


def _json_bytes(payload: object) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
    ).encode("utf-8")


def _write_registered_fixture(root: Path):
    registered = root / "registered"
    registered.mkdir()
    artifacts = (
        (
            "watchlist-d4",
            "ranked_watchlist",
            {
                "candidates": [
                    {
                        "symbol": "BTCUSDT",
                        "name": "Bitcoin Paper Research",
                        "rank": 1,
                        "total_score": 91.25,
                        "score_breakdown": {
                            "momentum": 92.0,
                            "quality": 90.5,
                        },
                        "reason_codes": ["REGISTERED_SIGNAL"],
                        "risk_flags": ["HIGH_VOLATILITY"],
                        "risk_level": "HIGH",
                        "data_quality_state": "PASS_STRICT",
                        "confidence_level": "MEDIUM",
                        "operator_review_required": True,
                    }
                ]
            },
        ),
        (
            "ai-d4",
            "ai_explanation",
            {
                "subject": "registered-advisory-evidence",
                "model_name": "advisory-model",
                "prompt_version": "prompt-v1",
                "evaluation_status": "REVIEW_REQUIRED",
                "risk_flags": ["MODEL_DRIFT"],
                "risk_level": "HIGH",
                "contradiction_codes": ["THESIS_CONFLICT"],
                "contradicts_artifact_id": "watchlist-d4",
            },
        ),
    )
    entries = []
    source_bytes = {}

    for artifact_id, artifact_type, payload in artifacts:
        relative_path = f"registered/{artifact_id}.json"
        content = _json_bytes(payload)
        (root / relative_path).write_bytes(content)
        source_bytes[artifact_id] = content
        entries.append(
            {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "correlation_id": "corr-d4-authority",
                "relative_path": relative_path,
                "content_sha256": hashlib.sha256(content).hexdigest(),
            }
        )

    index_path = root / "index.json"
    index_path.write_bytes(
        _json_bytes(
            {
                "schema_version": (
                    "fcf.browser_console.artifact_index.v1"
                ),
                "correlation_id": "corr-d4-authority",
                "entries": entries,
            }
        )
    )
    return index_path, source_bytes


def test_d4_matrix_and_fixture_cover_authority_invariants():
    rows = tuple(
        row
        for row in INTEGRATION_ACCEPTANCE_SYSTEM_MATRIX
        if row.delivery_stage == "D4"
    )

    assert tuple(row.matrix_id for row in rows) == (
        "REGISTERED_EVIDENCE_AUTHORITY",
        "DETERMINISTIC_ENGINE_AUTHORITY",
    )
    assert any(
        fixture.fixture_id == "AUTHORITY_INVARIANT_FIXTURE"
        and fixture.source_kind == "DETERMINISTIC_MODEL"
        for fixture in INTEGRATION_ACCEPTANCE_FIXTURE_REGISTRY
    )


def test_d4_permanent_authority_boundary_remains_fail_closed():
    boundary = BROWSER_PRODUCT_CONSOLE_INTEGRATION_ACCEPTANCE_BOUNDARY

    assert boundary.deterministic_engine_authority is True
    assert boundary.registered_evidence_authority is True
    assert boundary.operator_review_required is True
    assert boundary.ai_advisory_only is True
    assert boundary.reproducibility_required is True
    assert boundary.evidence_mutation_allowed is False
    assert boundary.source_artifact_mutation_allowed is False
    assert boundary.automatic_promotion_allowed is False
    assert boundary.automatic_model_activation_allowed is False
    assert boundary.automatic_prompt_activation_allowed is False
    assert boundary.automatic_learning_activation_allowed is False


def test_d4_registered_artifact_digest_is_authoritative(tmp_path: Path):
    index_path, source_bytes = _write_registered_fixture(tmp_path)
    loaded = load_console_artifact_index(index_path, tmp_path)

    assert tuple(
        item.registration.artifact_id
        for item in loaded.artifacts
    ) == ("watchlist-d4", "ai-d4")
    assert tuple(
        item.registration.content_sha256
        for item in loaded.artifacts
    ) == tuple(
        hashlib.sha256(source_bytes[artifact_id]).hexdigest()
        for artifact_id in ("watchlist-d4", "ai-d4")
    )

    (tmp_path / "registered" / "ai-d4.json").write_bytes(
        b'{"subject":"tampered"}'
    )

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_console_artifact_index(index_path, tmp_path)


def test_d4_registered_paths_and_size_bounds_fail_closed(tmp_path: Path):
    root = tmp_path / "registered"
    root.mkdir()
    artifact = root / "artifact.json"
    artifact.write_bytes(b"x" * 1025)

    with pytest.raises(ValueError, match="outside the allowed root"):
        read_runtime_artifact_snapshot(
            tmp_path / "outside.json",
            root,
        )

    with pytest.raises(ValueError, match="exceeds size limit"):
        read_runtime_artifact_snapshot(
            artifact,
            root,
            limits=RuntimeHardeningLimits(artifact_max_bytes=1024),
        )

    with pytest.raises(ValueError, match="outside the allowed root"):
        normalize_registered_relative_path("../artifact.json")


def test_d4_registered_inputs_and_product_outputs_are_reproducible(
    tmp_path: Path,
):
    index_path, source_bytes = _write_registered_fixture(tmp_path)
    first_runtime = build_browser_console_runtime(
        allowed_root=tmp_path,
        index_path=index_path,
    )
    second_runtime = build_browser_console_runtime(
        allowed_root=tmp_path,
        index_path=index_path,
    )

    for route in ("/stocks", "/ai-comparison", "/evidence/risk"):
        first = first_runtime.application.dispatch("GET", route)
        second = second_runtime.application.dispatch("GET", route)

        assert first.status == second.status == 200
        assert first.headers == second.headers
        assert first.body == second.body

    assert b"91.25" in first_runtime.application.dispatch(
        "GET",
        "/stocks",
    ).body
    assert b"advisory-model" in first_runtime.application.dispatch(
        "GET",
        "/ai-comparison",
    ).body
    assert b"REVIEW_REQUIRED" in first_runtime.application.dispatch(
        "GET",
        "/ai-comparison",
    ).body

    for artifact_id, expected in source_bytes.items():
        assert (
            tmp_path / "registered" / f"{artifact_id}.json"
        ).read_bytes() == expected


def test_d4_repeated_index_loading_preserves_registered_payloads(
    tmp_path: Path,
):
    index_path, _ = _write_registered_fixture(tmp_path)
    first = load_console_artifact_index(index_path, tmp_path)
    second = load_console_artifact_index(index_path, tmp_path)

    assert first.index == second.index
    assert first.artifacts == second.artifacts
    assert all(
        item.registration.correlation_id == "corr-d4-authority"
        for item in first.artifacts
    )
