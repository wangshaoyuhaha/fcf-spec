from __future__ import annotations

from itertools import combinations

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    BTCBookDelta,
    BTCBookSnapshot,
    BTCFundingObservation,
    BTCReferencePriceObservation,
    BTCTradeObservation,
    decimal_text,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant

from .contracts import (
    BTCCrossSourceFinding,
    BTCCrossSourceReconciliationPolicy,
    BTCCrossSourceReconciliationResult,
    RegisteredCanonicalBTCObservationSet,
    comparison_key,
    comparison_key_text,
)


def _finding(code, datasets, *, row=None, field_name=None, detail=None):
    return BTCCrossSourceFinding(
        code=code,
        severity="BLOCK",
        dataset_ids=tuple(item.dataset_id for item in datasets),
        comparison_key=comparison_key_text(row) if row is not None else None,
        field_name=field_name,
        detail=detail or {},
    )


def _clock_difference(left: str, right: str) -> int:
    return int(abs((instant(left) - instant(right)).total_seconds()))


def _levels_differ(left, right, policy):
    if len(left) != len(right):
        return True
    return any(
        abs(a.price - b.price) > policy.price_tolerance
        or abs(a.quantity - b.quantity) > policy.quantity_tolerance
        for a, b in zip(left, right)
    )


def reconcile_canonical_btc_observation_sets(datasets, policy):
    rows = tuple(datasets)
    if len(rows) < 2 or not all(isinstance(item, RegisteredCanonicalBTCObservationSet) for item in rows):
        raise ValueError("reconciliation requires at least two typed BTC datasets")
    if not isinstance(policy, BTCCrossSourceReconciliationPolicy):
        raise TypeError("policy must be BTCCrossSourceReconciliationPolicy")
    if len({item.dataset_id for item in rows}) != len(rows) or len({item.source_id for item in rows}) != len(rows):
        raise ValueError("reconciliation dataset and source identities must be unique")
    ordered = tuple(sorted(rows, key=lambda item: item.dataset_id))
    maps = tuple({comparison_key(item): item for item in dataset.observations} for dataset in ordered)
    union = set().union(*(set(item) for item in maps))
    overlap = set.intersection(*(set(item) for item in maps))
    findings = []
    for dataset in ordered:
        if dataset.rights_state == "UNRESOLVED":
            findings.append(_finding("RIGHTS_UNRESOLVED", (dataset,)))
        if dataset.retention_state == "UNRESOLVED":
            findings.append(_finding("RETENTION_UNRESOLVED", (dataset,)))
    for left, right in combinations(ordered, 2):
        if left.venue_semantics_id != right.venue_semantics_id:
            findings.append(
                _finding(
                    "VENUE_SEMANTICS_MISMATCH",
                    (left, right),
                    field_name="venue_semantics_id",
                    detail={
                        "left": left.venue_semantics_id,
                        "right": right.venue_semantics_id,
                    },
                )
            )
    for key in sorted(union):
        missing = tuple(dataset for dataset, mapping in zip(ordered, maps) if key not in mapping)
        if missing:
            sample = next(mapping[key] for mapping in maps if key in mapping)
            findings.append(_finding("COVERAGE_GAP", ordered, row=sample, detail={"missing_dataset_ids": ":".join(item.dataset_id for item in missing)}))
            continue
        observations = tuple(mapping[key] for mapping in maps)
        for left_index, right_index in combinations(range(len(observations)), 2):
            left = observations[left_index]
            right = observations[right_index]
            pair = (ordered[left_index], ordered[right_index])
            if policy.require_same_venue and left.header.venue_id != right.header.venue_id:
                findings.append(_finding("VENUE_MISMATCH", pair, row=left, field_name="venue_id", detail={"left": left.header.venue_id, "right": right.header.venue_id}))
            for field_name in ("received_at_utc", "ingested_at_utc"):
                if _clock_difference(getattr(left.header, field_name), getattr(right.header, field_name)) > policy.clock_tolerance_seconds:
                    findings.append(_finding("CLOCK_MISMATCH", pair, row=left, field_name=field_name))
            if left.header.source_sequence != right.header.source_sequence:
                findings.append(_finding("SEQUENCE_MISMATCH", pair, row=left, field_name="source_sequence", detail={"left": str(left.header.source_sequence), "right": str(right.header.source_sequence)}))
            if isinstance(left, BTCTradeObservation):
                if abs(left.price - right.price) > policy.price_tolerance:
                    findings.append(_finding("PRICE_MISMATCH", pair, row=left, field_name="price", detail={"left": decimal_text(left.price), "right": decimal_text(right.price)}))
                if abs(left.quantity - right.quantity) > policy.quantity_tolerance:
                    findings.append(_finding("QUANTITY_MISMATCH", pair, row=left, field_name="quantity"))
                if left.aggressor_side != right.aggressor_side:
                    findings.append(_finding("SIDE_MISMATCH", pair, row=left, field_name="aggressor_side"))
            elif isinstance(left, BTCBookSnapshot):
                if _levels_differ(left.bids, right.bids, policy) or _levels_differ(left.asks, right.asks, policy):
                    findings.append(_finding("BOOK_MISMATCH", pair, row=left, field_name="levels"))
            elif isinstance(left, BTCBookDelta):
                if left.previous_sequence != right.previous_sequence:
                    findings.append(_finding("PREVIOUS_SEQUENCE_MISMATCH", pair, row=left, field_name="previous_sequence"))
                if _levels_differ(left.bid_updates, right.bid_updates, policy) or _levels_differ(left.ask_updates, right.ask_updates, policy):
                    findings.append(_finding("BOOK_DELTA_MISMATCH", pair, row=left, field_name="updates"))
            elif isinstance(left, BTCReferencePriceObservation):
                if abs(left.mark_price - right.mark_price) > policy.price_tolerance:
                    findings.append(_finding("MARK_PRICE_MISMATCH", pair, row=left, field_name="mark_price"))
                if abs(left.index_price - right.index_price) > policy.price_tolerance:
                    findings.append(_finding("INDEX_PRICE_MISMATCH", pair, row=left, field_name="index_price"))
            elif isinstance(left, BTCFundingObservation):
                if abs(left.funding_rate - right.funding_rate) > policy.funding_rate_tolerance:
                    findings.append(_finding("FUNDING_RATE_MISMATCH", pair, row=left, field_name="funding_rate"))
                if (left.interval_start_utc, left.interval_end_utc) != (right.interval_start_utc, right.interval_end_utc):
                    findings.append(_finding("FUNDING_INTERVAL_MISMATCH", pair, row=left, field_name="funding_interval"))
    findings.sort(key=lambda item: item.finding_hash)
    return BTCCrossSourceReconciliationResult(
        dataset_hashes=tuple(item.dataset_hash for item in ordered),
        policy_hash=policy.policy_hash,
        union_key_count=len(union),
        overlap_key_count=len(overlap),
        findings=tuple(findings),
        quality_state="QUARANTINE_REVIEW_REQUIRED" if findings else "CONSISTENT",
    )
