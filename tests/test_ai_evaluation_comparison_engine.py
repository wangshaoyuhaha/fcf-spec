import sys
from copy import deepcopy
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[1] / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from fcf.sidecars.ai_evaluation_comparison import (
    APP_ID,
    ENGINE_VERSION,
    compare_expected_observed,
)


def test_engine_returns_matched_for_equal_results() -> None:
    expected = {"label": "PASS", "score": 1}
    observed = {"score": 1, "label": "PASS"}

    report = compare_expected_observed(expected, observed)

    assert report["app_id"] == APP_ID
    assert report["engine_version"] == ENGINE_VERSION
    assert report["comparison_status"] == "MATCHED"
    assert report["matched_fields"] == ["label", "score"]
    assert report["difference_field_count"] == 0


def test_engine_returns_mismatch_when_no_fields_match() -> None:
    report = compare_expected_observed(
        {"label": "PASS", "score": 1},
        {"label": "FAIL", "score": 2},
    )

    assert report["comparison_status"] == "MISMATCH"
    assert report["matched_field_count"] == 0
    assert report["mismatched_fields"] == ["label", "score"]


def test_engine_returns_partial_match() -> None:
    report = compare_expected_observed(
        {"label": "PASS", "score": 1},
        {"label": "PASS", "score": 2},
    )

    assert report["comparison_status"] == "PARTIAL_MATCH"
    assert report["matched_fields"] == ["label"]
    assert report["mismatched_fields"] == ["score"]


def test_engine_detects_missing_expected_field() -> None:
    report = compare_expected_observed(
        {"label": "PASS"},
        {"label": "PASS", "reason": "registered"},
    )

    assert report["comparison_status"] == "PARTIAL_MATCH"
    assert report["missing_expected_fields"] == ["reason"]


def test_engine_detects_missing_observed_field() -> None:
    report = compare_expected_observed(
        {"label": "PASS", "reason": "registered"},
        {"label": "PASS"},
    )

    assert report["comparison_status"] == "PARTIAL_MATCH"
    assert report["missing_observed_fields"] == ["reason"]


def test_engine_compares_nested_mappings_deterministically() -> None:
    expected = {
        "details": {
            "score": 1,
            "flags": ["A", "B"],
        }
    }
    observed = {
        "details": {
            "flags": ["A", "B"],
            "score": 1,
        }
    }

    report = compare_expected_observed(expected, observed)

    assert report["comparison_status"] == "MATCHED"


def test_engine_supports_explicit_field_selection() -> None:
    report = compare_expected_observed(
        {"label": "PASS", "score": 1},
        {"label": "PASS", "score": 999},
        comparison_fields=["label"],
    )

    assert report["comparison_status"] == "MATCHED"
    assert report["compared_field_count"] == 1
    assert report["matched_fields"] == ["label"]


def test_engine_rejects_non_mapping_input() -> None:
    report = compare_expected_observed(
        [],
        {"label": "PASS"},
    )

    assert report["comparison_status"] == "INVALID"
    assert "expected_result_not_mapping" in report["errors"]


def test_engine_rejects_invalid_field_selection() -> None:
    report = compare_expected_observed(
        {"label": "PASS"},
        {"label": "PASS"},
        comparison_fields=["label", "label"],
    )

    assert report["comparison_status"] == "INVALID"
    assert "comparison_fields_duplicate" in report["errors"]


def test_engine_blocks_empty_results() -> None:
    report = compare_expected_observed({}, {})

    assert report["comparison_status"] == "BLOCKED"
    assert report["result_status"] == "BLOCKED"
    assert report["errors"] == ["no_comparison_fields"]


def test_engine_rejects_non_json_safe_values() -> None:
    report = compare_expected_observed(
        {"value": object()},
        {"value": object()},
    )

    assert report["comparison_status"] == "INVALID"
    assert "expected_result_not_json_safe" in report["errors"]
    assert "observed_result_not_json_safe" in report["errors"]


def test_engine_does_not_mutate_sources() -> None:
    expected = {"nested": {"value": [1, 2, 3]}}
    observed = {"nested": {"value": [1, 2, 4]}}
    expected_before = deepcopy(expected)
    observed_before = deepcopy(observed)

    compare_expected_observed(expected, observed)

    assert expected == expected_before
    assert observed == observed_before


def test_engine_preserves_safety_boundary() -> None:
    report = compare_expected_observed(
        {"label": "PASS"},
        {"label": "PASS"},
    )

    assert report["paper_only"] is True
    assert report["local_only"] is True
    assert report["read_only"] is True
    assert report["sidecar_only"] is True
    assert report["operator_review_required"] is True
    assert report["automatic_acceptance_allowed"] is False
    assert report["model_invocation_allowed"] is False
    assert report["prompt_execution_allowed"] is False
    assert report["trade_action_allowed"] is False
    assert report["real_execution_allowed"] is False
    assert report["core_mutation_allowed"] is False


def test_engine_output_is_deterministic() -> None:
    expected = {"b": 2, "a": 1}
    observed = {"a": 1, "b": 3}

    first = compare_expected_observed(expected, observed)
    second = compare_expected_observed(expected, observed)

    assert first == second
    assert [
        item["field"]
        for item in first["field_results"]
    ] == ["a", "b"]