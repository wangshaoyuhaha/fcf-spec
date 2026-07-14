
import hashlib
import json
from pathlib import Path

import pytest

from apps.browser_product_console_runtime_app_1 import (
    build_console_read_model,
    load_console_artifact_index,
)


def _write_json(path: Path, payload: object) -> str:
    content = json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
    )
    path.write_text(content, encoding="utf-8")
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _candidate(symbol: str, rank: int):
    return {
        "symbol": symbol,
        "name": f"Name {symbol}",
        "rank": rank,
        "total_score": 82.5,
        "score_breakdown": {
            "momentum": 80.0,
            "quality": 85.0,
        },
        "reason_codes": ["volume_expansion"],
        "risk_flags": ["high_volatility"],
        "data_quality_state": "PASS_STRICT",
        "confidence_level": "MEDIUM",
        "operator_review_required": True,
    }


def _index_payload(entries):
    return {
        "schema_version": "fcf.browser_console.artifact_index.v1",
        "correlation_id": "corr-browser-1",
        "entries": entries,
    }


def _entry(artifact_id, artifact_type, relative_path, digest):
    return {
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "correlation_id": "corr-browser-1",
        "relative_path": relative_path,
        "content_sha256": digest,
    }


def test_d2_loads_registered_artifacts_and_builds_read_model(
    tmp_path: Path,
):
    watchlist_digest = _write_json(
        tmp_path / "watchlist.json",
        {"candidates": [_candidate("600001", 2), _candidate("600000", 1)]},
    )
    shadow_digest = _write_json(
        tmp_path / "shadow.json",
        {"status": "REVIEW_PACKET_READY"},
    )
    _write_json(
        tmp_path / "index.json",
        _index_payload(
            [
                _entry(
                    "watchlist-1",
                    "ranked_watchlist",
                    "watchlist.json",
                    watchlist_digest,
                ),
                _entry(
                    "shadow-1",
                    "shadow_observation",
                    "shadow.json",
                    shadow_digest,
                ),
            ]
        ),
    )

    loaded = load_console_artifact_index(
        tmp_path / "index.json",
        tmp_path,
    )
    model = build_console_read_model(loaded)

    assert tuple(item.symbol for item in model.candidates) == (
        "600000",
        "600001",
    )
    assert "shadow_observation" in model.sections
    assert model.operator_review_required is True


def test_d2_rejects_artifact_hash_mismatch(tmp_path: Path):
    _write_json(tmp_path / "watchlist.json", {"candidates": []})
    _write_json(
        tmp_path / "index.json",
        _index_payload(
            [
                _entry(
                    "watchlist-1",
                    "ranked_watchlist",
                    "watchlist.json",
                    "0" * 64,
                )
            ]
        ),
    )

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        load_console_artifact_index(
            tmp_path / "index.json",
            tmp_path,
        )


def test_d2_rejects_path_outside_allowed_root(tmp_path: Path):
    root = tmp_path / "allowed"
    root.mkdir()
    outside = tmp_path / "outside.json"
    digest = _write_json(outside, {"candidates": []})
    _write_json(
        root / "index.json",
        _index_payload(
            [
                _entry(
                    "watchlist-1",
                    "ranked_watchlist",
                    "../outside.json",
                    digest,
                )
            ]
        ),
    )

    with pytest.raises(ValueError, match="outside the allowed root"):
        load_console_artifact_index(
            root / "index.json",
            root,
        )


def test_d2_rejects_duplicate_artifact_ids(tmp_path: Path):
    first_digest = _write_json(tmp_path / "one.json", {"candidates": []})
    second_digest = _write_json(tmp_path / "two.json", {"status": "ok"})
    _write_json(
        tmp_path / "index.json",
        _index_payload(
            [
                _entry(
                    "duplicate",
                    "ranked_watchlist",
                    "one.json",
                    first_digest,
                ),
                _entry(
                    "duplicate",
                    "shadow_observation",
                    "two.json",
                    second_digest,
                ),
            ]
        ),
    )

    with pytest.raises(ValueError, match="artifact_id values must be unique"):
        load_console_artifact_index(
            tmp_path / "index.json",
            tmp_path,
        )


def test_d2_rejects_unsupported_index_schema(tmp_path: Path):
    digest = _write_json(tmp_path / "watchlist.json", {"candidates": []})
    payload = _index_payload(
        [
            _entry(
                "watchlist-1",
                "ranked_watchlist",
                "watchlist.json",
                digest,
            )
        ]
    )
    payload["schema_version"] = "unsupported"
    _write_json(tmp_path / "index.json", payload)

    with pytest.raises(ValueError, match="unsupported artifact index schema"):
        load_console_artifact_index(
            tmp_path / "index.json",
            tmp_path,
        )


def test_d2_read_model_rejects_missing_operator_review(
    tmp_path: Path,
):
    candidate = _candidate("600000", 1)
    candidate["operator_review_required"] = False
    digest = _write_json(
        tmp_path / "watchlist.json",
        {"candidates": [candidate]},
    )
    _write_json(
        tmp_path / "index.json",
        _index_payload(
            [
                _entry(
                    "watchlist-1",
                    "ranked_watchlist",
                    "watchlist.json",
                    digest,
                )
            ]
        ),
    )

    loaded = load_console_artifact_index(
        tmp_path / "index.json",
        tmp_path,
    )

    with pytest.raises(ValueError, match="operator review"):
        build_console_read_model(loaded)
