from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1 import (
    AShareDailyObservation,
)
from apps.fcp_0021_a_share_cross_source_quality_reconciliation_app_1 import (
    AShareCrossSourceReconciliationPolicy,
    RegisteredCanonicalDailyDataset,
    reconcile_canonical_a_share_daily_datasets,
)


AS_OF = "2026-07-21T10:00:00Z"


def _observation(**changes: object) -> AShareDailyObservation:
    values: dict[str, object] = {
        "instrument_id": "600036.XSHG",
        "trade_date": "2026-07-18",
        "raw_open": Decimal("10"),
        "raw_high": Decimal("12"),
        "raw_low": Decimal("9"),
        "raw_close": Decimal("11"),
        "volume": 1000,
        "amount": Decimal("10500"),
        "adjustment_factor": Decimal("1.25"),
        "factor_version": "factor-v1",
        "factor_available_at_utc": "2026-07-18T08:01:00Z",
        "event_at_utc": "2026-07-18T08:00:00Z",
        "available_at_utc": "2026-07-18T08:01:00Z",
        "first_tradable_at_utc": "2026-07-21T01:30:00Z",
        "ingested_at_utc": "2026-07-18T08:02:00Z",
        "revision_at_utc": "2026-07-18T09:00:00Z",
        "trading_status": "OBSERVED_TRADING",
        "source_artifact_sha256": "a" * 64,
    }
    values.update(changes)
    return AShareDailyObservation(**values)


def _dataset(
    suffix: str,
    observations: tuple[AShareDailyObservation, ...] | None = None,
    **changes: object,
) -> RegisteredCanonicalDailyDataset:
    values: dict[str, object] = {
        "dataset_id": f"dataset-{suffix}",
        "source_id": f"source-{suffix}",
        "observations": observations or (_observation(),),
        "as_of_utc": AS_OF,
    }
    values.update(changes)
    return RegisteredCanonicalDailyDataset(**values)


def _policy(**changes: object) -> AShareCrossSourceReconciliationPolicy:
    values: dict[str, object] = {"policy_id": "cross-source-v1"}
    values.update(changes)
    return AShareCrossSourceReconciliationPolicy(**values)


def _codes(result: object) -> tuple[str, ...]:
    return tuple(item.code for item in result.findings)


def test_identical_registered_datasets_are_consistent_and_reviewable() -> None:
    first = _dataset("a")
    second = _dataset(
        "b",
        (_observation(source_artifact_sha256="b" * 64),),
    )

    result = reconcile_canonical_a_share_daily_datasets((first, second), _policy())

    assert result.quality_state == "CONSISTENT"
    assert result.findings == ()
    assert result.union_key_count == result.overlap_key_count == 1
    assert result.operator_review_required is True
    assert result.source_selected is False


def test_input_order_does_not_change_the_result() -> None:
    first = _dataset("a")
    second = _dataset("b", (_observation(source_artifact_sha256="b" * 64),))
    policy = _policy()

    forward = reconcile_canonical_a_share_daily_datasets((first, second), policy)
    reverse = reconcile_canonical_a_share_daily_datasets((second, first), policy)

    assert forward.result_hash == reverse.result_hash
    assert forward.dataset_hashes == reverse.dataset_hashes


def test_coverage_gap_is_quarantined() -> None:
    missing_key = _observation(
        instrument_id="000001.XSHE",
        source_artifact_sha256="b" * 64,
    )
    result = reconcile_canonical_a_share_daily_datasets(
        (_dataset("a"), _dataset("b", (missing_key,))),
        _policy(),
    )

    assert result.quality_state == "QUARANTINE_REVIEW_REQUIRED"
    assert _codes(result) == ("COVERAGE_GAP", "COVERAGE_GAP")
    assert result.overlap_key_count == 0
    assert result.union_key_count == 2


def test_price_difference_respects_exact_tolerance() -> None:
    first = _dataset("a")
    changed = _dataset(
        "b",
        (_observation(raw_close=Decimal("11.1"), source_artifact_sha256="b" * 64),),
    )
    blocked = reconcile_canonical_a_share_daily_datasets((first, changed), _policy())
    accepted = reconcile_canonical_a_share_daily_datasets(
        (first, changed),
        _policy(price_tolerance=Decimal("0.1")),
    )

    assert _codes(blocked) == ("PRICE_MISMATCH",)
    assert blocked.findings[0].field_name == "raw_close"
    assert accepted.quality_state == "CONSISTENT"


def test_volume_and_amount_differences_respect_tolerances() -> None:
    first = _dataset("a")
    changed = _dataset(
        "b",
        (
            _observation(
                volume=1001,
                amount=Decimal("10500.5"),
                source_artifact_sha256="b" * 64,
            ),
        ),
    )
    blocked = reconcile_canonical_a_share_daily_datasets((first, changed), _policy())
    accepted = reconcile_canonical_a_share_daily_datasets(
        (first, changed),
        _policy(volume_tolerance=1, amount_tolerance=Decimal("0.5")),
    )

    assert set(_codes(blocked)) == {"AMOUNT_MISMATCH", "VOLUME_MISMATCH"}
    assert accepted.quality_state == "CONSISTENT"


@pytest.mark.parametrize(
    ("change", "code"),
    [
        (
            {
                "adjustment_factor": None,
                "factor_version": None,
                "factor_available_at_utc": None,
            },
            "ADJUSTMENT_FACTOR_MISSING",
        ),
        ({"adjustment_factor": Decimal("1.26")}, "ADJUSTMENT_FACTOR_MISMATCH"),
        ({"factor_version": "factor-v2"}, "ADJUSTMENT_FACTOR_MISMATCH"),
        ({"trading_status": "UNKNOWN"}, "TRADING_STATUS_MISMATCH"),
    ],
)
def test_factor_and_status_disagreements_are_quarantined(
    change: dict[str, object], code: str
) -> None:
    change["source_artifact_sha256"] = "b" * 64
    result = reconcile_canonical_a_share_daily_datasets(
        (_dataset("a"), _dataset("b", (_observation(**change),))),
        _policy(),
    )
    assert _codes(result) == (code,)


def test_clock_differences_include_factor_availability() -> None:
    changed = _dataset(
        "b",
        (
            _observation(
                factor_available_at_utc="2026-07-18T08:02:00Z",
                first_tradable_at_utc="2026-07-21T01:31:00Z",
                source_artifact_sha256="b" * 64,
            ),
        ),
    )
    blocked = reconcile_canonical_a_share_daily_datasets(
        (_dataset("a"), changed), _policy(clock_tolerance_seconds=59)
    )
    accepted = reconcile_canonical_a_share_daily_datasets(
        (_dataset("a"), changed), _policy(clock_tolerance_seconds=60)
    )

    assert _codes(blocked) == ("CLOCK_MISMATCH", "CLOCK_MISMATCH")
    assert {item.field_name for item in blocked.findings} == {
        "factor_available_at_utc",
        "first_tradable_at_utc",
    }
    assert accepted.quality_state == "CONSISTENT"


def test_unresolved_rights_and_retention_remain_visible() -> None:
    result = reconcile_canonical_a_share_daily_datasets(
        (
            _dataset("a", rights_state="UNRESOLVED"),
            _dataset("b", retention_state="UNRESOLVED"),
        ),
        _policy(),
    )
    assert set(_codes(result)) == {"RETENTION_UNRESOLVED", "RIGHTS_UNRESOLVED"}


def test_three_sources_are_compared_pairwise() -> None:
    first = _dataset("a")
    second = _dataset(
        "b",
        (_observation(raw_close=Decimal("11.1"), source_artifact_sha256="b" * 64),),
    )
    third = _dataset(
        "c",
        (_observation(raw_close=Decimal("10.9"), source_artifact_sha256="c" * 64),),
    )
    result = reconcile_canonical_a_share_daily_datasets(
        (first, second, third),
        _policy(price_tolerance=Decimal("0.15")),
    )

    assert _codes(result) == ("PRICE_MISMATCH",)
    assert result.findings[0].dataset_ids == ("dataset-b", "dataset-c")


def test_dataset_hash_covers_factor_and_artifact_lineage() -> None:
    baseline = _dataset("a")
    factor_changed = _dataset(
        "a",
        (_observation(adjustment_factor=Decimal("1.26")),),
    )
    artifact_changed = _dataset(
        "a",
        (_observation(source_artifact_sha256="b" * 64),),
    )

    assert len({baseline.dataset_hash, factor_changed.dataset_hash, artifact_changed.dataset_hash}) == 3


def test_dataset_rejects_future_knowledge_and_unordered_rows() -> None:
    with pytest.raises(ValueError, match="knowledge after as_of"):
        _dataset("a", as_of_utc="2026-07-18T08:30:00Z")

    later = _observation(instrument_id="600036.XSHG")
    earlier = _observation(instrument_id="000001.XSHE")
    with pytest.raises(ValueError, match="uniquely and deterministically ordered"):
        _dataset("a", (later, earlier))
    with pytest.raises(ValueError, match="uniquely and deterministically ordered"):
        _dataset("a", (later, later))


@pytest.mark.parametrize(
    "change",
    [
        {"schema_version": "unknown"},
        {"currency": "USD"},
        {"amount_unit": "FEN"},
        {"volume_unit": "LOTS"},
        {"operator_registered": False},
        {"local_only": False},
        {"provider_selected": True},
    ],
)
def test_dataset_compatibility_contract_is_closed(change: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _dataset("a", **change)


@pytest.mark.parametrize(
    "change",
    [
        {"price_tolerance": 0.1},
        {"amount_tolerance": -1},
        {"volume_tolerance": True},
        {"clock_tolerance_seconds": 86401},
        {"operator_registered": False},
        {"source_selection_allowed": True},
    ],
)
def test_policy_is_exact_bounded_and_non_authoritative(change: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        _policy(**change)


def test_reconciliation_rejects_duplicate_or_insufficient_lineage() -> None:
    first = _dataset("a")
    with pytest.raises(ValueError, match="at least two"):
        reconcile_canonical_a_share_daily_datasets((first,), _policy())
    with pytest.raises(ValueError, match="identities must be unique"):
        reconcile_canonical_a_share_daily_datasets((first, _dataset("a")), _policy())
    with pytest.raises(ValueError, match="identities must be unique"):
        reconcile_canonical_a_share_daily_datasets(
            (first, _dataset("b", source_id="source-a")), _policy()
        )


def test_findings_are_immutable_registered_evidence() -> None:
    changed = _dataset(
        "b",
        (_observation(raw_close=Decimal("11.1"), source_artifact_sha256="b" * 64),),
    )
    result = reconcile_canonical_a_share_daily_datasets(
        (_dataset("a"), changed), _policy()
    )
    finding = result.findings[0]

    with pytest.raises(TypeError):
        finding.detail["left"] = "0"
    with pytest.raises(FrozenInstanceError):
        finding.code = "OTHER"
