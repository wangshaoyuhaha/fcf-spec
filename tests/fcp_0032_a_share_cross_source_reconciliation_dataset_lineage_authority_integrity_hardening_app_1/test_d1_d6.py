from dataclasses import replace
from decimal import Decimal

import pytest

from apps.fcp_0021_a_share_cross_source_quality_reconciliation_app_1 import (
    reconcile_canonical_a_share_daily_datasets,
)
from tests.fcp_0021_a_share_cross_source_quality_reconciliation_app_1.test_d1_d6 import (
    _dataset,
    _observation,
    _policy,
)


def reconciliation_result(*, mismatch=False):
    close = Decimal("11.1") if mismatch else Decimal("11")
    return reconcile_canonical_a_share_daily_datasets(
        (
            _dataset("a"),
            _dataset(
                "b",
                (_observation(raw_close=close, source_artifact_sha256="b" * 64),),
            ),
        ),
        _policy(),
    )


def test_exact_result_preserves_lineage_authorities_and_hash():
    first = reconciliation_result()
    second = reconciliation_result()

    assert first.dataset_ids == ("dataset-a", "dataset-b")
    assert first.calculation_authority == "DETERMINISTIC_ENGINE"
    assert first.evidence_authority == "REGISTERED_EVIDENCE"
    assert first.ai_role == "ADVISORY_ONLY"
    assert first.result_hash == second.result_hash


@pytest.mark.parametrize(
    "dataset_ids",
    [
        ("dataset-b", "dataset-a"),
        ("dataset-a", "dataset-a"),
        ("dataset-a",),
    ],
)
def test_result_rejects_noncanonical_dataset_identity_pairs(dataset_ids):
    with pytest.raises(ValueError, match="ordered dataset identity"):
        replace(reconciliation_result(), dataset_ids=dataset_ids)


def test_result_rejects_finding_lineage_outside_registered_inputs():
    result = reconciliation_result(mismatch=True)
    foreign = replace(result.findings[0], dataset_ids=("foreign-dataset",))

    with pytest.raises(ValueError, match="lineage is not registered"):
        replace(result, findings=(foreign,))


@pytest.mark.parametrize(
    "field,value",
    [
        ("calculation_authority", "BROKER"),
        ("evidence_authority", "UNREGISTERED"),
        ("ai_role", "DECISION"),
    ],
)
def test_result_rejects_authority_substitution(field, value):
    with pytest.raises(ValueError, match="authority identities are immutable"):
        replace(reconciliation_result(), **{field: value})


def test_result_hash_commits_to_dataset_identity_pairs():
    result = reconciliation_result()
    changed = replace(result, dataset_ids=("dataset-a", "dataset-c"))

    assert changed.result_hash != result.result_hash
