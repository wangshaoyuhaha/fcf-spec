"""Tests for the governed AI version registry index."""

from copy import deepcopy
import hashlib

import pytest

from fcf.sidecars.ai_prompt_model_version_registry import (
    build_registry_index,
    build_version_record,
    get_record_by_id,
    get_records_by_kind,
    validate_registry_index,
)


def _hash(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _record(
    *,
    kind: str,
    label: str,
    research_run_id: str,
) -> dict[str, object]:
    versions = {
        "prompt_version": "prompt-v1",
        "model_version": "model-v1",
        "contract_version": "contract-v1",
        "registry_version": "registry-v1",
    }

    if kind == "PROMPT":
        versions["prompt_version"] = label
    elif kind == "MODEL":
        versions["model_version"] = label
    elif kind == "CONTRACT":
        versions["contract_version"] = label
    elif kind == "REGISTRY":
        versions["registry_version"] = label

    return build_version_record(
        record_kind=kind,
        record_status="REVIEW_REQUIRED",
        prompt_version=versions["prompt_version"],
        model_version=versions["model_version"],
        contract_version=versions["contract_version"],
        registry_version=versions["registry_version"],
        correlation_id="corr-001",
        research_run_id=research_run_id,
        source_artifact_ids=[f"artifact-{research_run_id}"],
        validation_baseline_id="baseline-001",
        content_hash=_hash(label),
    )


def _records() -> list[dict[str, object]]:
    return [
        _record(
            kind="MODEL",
            label="model-v2",
            research_run_id="run-002",
        ),
        _record(
            kind="PROMPT",
            label="prompt-v2",
            research_run_id="run-001",
        ),
    ]


def test_registry_index_is_valid() -> None:
    index = build_registry_index(_records())

    assert validate_registry_index(index) == []
    assert index["record_count"] == 2
    assert index["registry_index_id"].startswith(
        "version-index-"
    )
    assert len(str(index["registry_index_hash"])) == 64


def test_registry_index_is_deterministic() -> None:
    first = build_registry_index(_records())
    second = build_registry_index(list(reversed(_records())))

    assert first["registry_index_id"] == second[
        "registry_index_id"
    ]
    assert first["registry_index_hash"] == second[
        "registry_index_hash"
    ]
    assert first["registry_entry_ids"] == second[
        "registry_entry_ids"
    ]


def test_registry_index_does_not_mutate_records() -> None:
    records = _records()
    before = deepcopy(records)

    build_registry_index(records)

    assert records == before


def test_registry_index_summarizes_kinds() -> None:
    index = build_registry_index(_records())

    assert index["kind_summary"] == {
        "MODEL": 1,
        "PROMPT": 1,
    }
    assert index["status_summary"] == {
        "REVIEW_REQUIRED": 2,
    }


def test_lookup_by_registry_entry_id_returns_copy() -> None:
    index = build_registry_index(_records())
    entry_id = index["registry_entry_ids"][0]

    found = get_record_by_id(index, entry_id)

    assert found is not None
    assert found["registry_entry_id"] == entry_id

    found["record_status"] = "BLOCKED"
    assert index["records"][0]["record_status"] == (
        "REVIEW_REQUIRED"
    )


def test_lookup_by_kind_returns_matching_records() -> None:
    index = build_registry_index(_records())

    records = get_records_by_kind(index, "PROMPT")

    assert len(records) == 1
    assert records[0]["record_kind"] == "PROMPT"


def test_duplicate_registry_entry_id_is_rejected() -> None:
    record = _record(
        kind="PROMPT",
        label="prompt-v2",
        research_run_id="run-001",
    )

    with pytest.raises(
        ValueError,
        match="duplicate_registry_entry_id",
    ):
        build_registry_index([record, deepcopy(record)])


def test_duplicate_version_key_is_rejected() -> None:
    first = _record(
        kind="PROMPT",
        label="prompt-v2",
        research_run_id="run-001",
    )
    second = _record(
        kind="PROMPT",
        label="prompt-v2",
        research_run_id="run-999",
    )

    with pytest.raises(
        ValueError,
        match="duplicate_version_key",
    ):
        build_registry_index([first, second])


def test_empty_registry_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="empty_registry_records",
    ):
        build_registry_index([])


def test_registry_index_is_safety_locked() -> None:
    index = build_registry_index(_records())

    assert index["human_review_required"] is True
    assert index["archive_required"] is True
    assert index["model_execution_allowed"] is False
    assert index["automatic_activation_allowed"] is False
    assert index["automatic_promotion_allowed"] is False
    assert index["automatic_rollback_allowed"] is False
    assert index["source_mutation_allowed"] is False
    assert index["real_trading_allowed"] is False
    assert index["real_execution_allowed"] is False
