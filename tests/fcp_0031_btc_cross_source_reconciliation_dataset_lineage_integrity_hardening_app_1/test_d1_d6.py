from dataclasses import replace

import pytest

from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1 import (
    BTCCrossSourceFinding,
    BTCCrossSourceReconciliationPolicy,
    reconcile_canonical_btc_observation_sets,
)
from tests.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1.test_d1_d6 import (
    dataset,
    trade,
)


def reconciliation_result(*, mismatch=False):
    price = "65001" if mismatch else "65000"
    return reconcile_canonical_btc_observation_sets(
        (
            dataset("a", (trade("a"),)),
            dataset("b", (trade("b", price),)),
        ),
        BTCCrossSourceReconciliationPolicy("lineage-v1"),
    )


def test_exact_result_preserves_ordered_dataset_lineage_and_hash():
    first = reconciliation_result()
    second = reconciliation_result()

    assert first.dataset_ids == ("dataset-a", "dataset-b")
    assert len(first.dataset_ids) == len(first.dataset_hashes)
    assert first.result_hash == second.result_hash


@pytest.mark.parametrize("comparison_key", [1, True, (), " "])
def test_finding_rejects_non_text_or_blank_comparison_key(comparison_key):
    with pytest.raises(ValueError, match="nonempty text"):
        BTCCrossSourceFinding(
            "AUDIT",
            "WARN",
            ("dataset-a",),
            comparison_key=comparison_key,
        )


@pytest.mark.parametrize(
    "dataset_ids",
    [
        ("dataset-b", "dataset-a"),
        ("dataset-a", "dataset-a"),
        ("dataset-a",),
    ],
)
def test_result_rejects_noncanonical_dataset_identity_pairs(dataset_ids):
    result = reconciliation_result()

    with pytest.raises(ValueError, match="ordered dataset identity"):
        replace(result, dataset_ids=dataset_ids)


def test_result_rejects_finding_lineage_outside_registered_inputs():
    result = reconciliation_result(mismatch=True)
    foreign = replace(result.findings[0], dataset_ids=("foreign-dataset",))
    findings = tuple(sorted((foreign, *result.findings[1:]), key=lambda item: item.finding_hash))

    with pytest.raises(ValueError, match="lineage is not registered"):
        replace(result, findings=findings)


def test_result_hash_commits_to_dataset_identity_pairs():
    result = reconciliation_result()
    changed = replace(result, dataset_ids=("dataset-a", "dataset-c"))

    assert changed.result_hash != result.result_hash
