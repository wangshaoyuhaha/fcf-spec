from __future__ import annotations

import json
from decimal import Decimal
from itertools import combinations

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import (
    BTCBookDelta,
    BTCBookSnapshot,
    BTCFundingObservation,
    BTCReferencePriceObservation,
    BTCTradeObservation,
    decimal_text,
)
from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1 import (
    BTCCrossSourceReconciliationPolicy,
    BTCCrossSourceReconciliationResult,
    RegisteredCanonicalBTCObservationSet,
    reconcile_canonical_btc_observation_sets,
)
from apps.fcp_0023_btc_cross_source_venue_quality_reconciliation_app_1.contracts import (
    comparison_key,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant

from .contracts import (
    FIELD_KINDS,
    BTCCrossSourceExactObservationDeltaEvidenceLedger,
    BTCObservationDatasetLineage,
    BTCObservationDeltaEvidenceEntry,
    ledger_fields,
)


def _levels_text(levels: object) -> str:
    return json.dumps(
        [[decimal_text(item.price), decimal_text(item.quantity)] for item in levels],
        ensure_ascii=True,
        separators=(",", ":"),
    )


def _value(observation: object | None, field_name: str) -> str | None:
    if observation is None:
        return None
    header = observation.header
    header_values = {
        "observation_id": header.observation_id,
        "artifact_id": header.artifact_id,
        "venue_id": header.venue_id,
        "source_sequence": str(header.source_sequence),
        "received_at_utc": header.received_at_utc,
        "ingested_at_utc": header.ingested_at_utc,
        "schema_version": str(header.schema_version),
        "header_hash": header.record_hash,
        "observation_hash": observation.observation_hash,
    }
    if field_name in header_values:
        return header_values[field_name]
    value = getattr(observation, field_name)
    if field_name in {"bids", "asks", "bid_updates", "ask_updates"}:
        return _levels_text(value)
    if isinstance(value, Decimal):
        return decimal_text(value)
    return str(value)


def _delta(left: str | None, right: str | None, kind: str) -> str | None:
    if left is None or right is None:
        return None
    if kind == "EXACT_DECIMAL":
        return decimal_text(abs(Decimal(left) - Decimal(right)))
    if kind == "ABS_INTEGER":
        return str(abs(int(left) - int(right)))
    if kind == "ABS_SECONDS":
        return str(round(abs((instant(left) - instant(right)).total_seconds())))
    return None


def _entry(left_dataset, right_dataset, left, right, key, field_name):
    left_value = _value(left, field_name)
    right_value = _value(right, field_name)
    kind = FIELD_KINDS[field_name]
    state = (
        "PAIR_INCOMPLETE"
        if left_value is None or right_value is None
        else "EXACT_MATCH"
        if left_value == right_value
        else "DELTA_PRESENT"
    )
    return BTCObservationDeltaEvidenceEntry(
        left_dataset_id=left_dataset.dataset_id,
        right_dataset_id=right_dataset.dataset_id,
        instrument_id=key[0],
        instrument_kind=key[1],
        observation_kind=key[2],
        event_at_utc=key[3],
        field_name=field_name,
        delta_kind=kind,
        left_value=left_value,
        right_value=right_value,
        delta_value=_delta(left_value, right_value, kind),
        comparison_state=state,
    )


def build_btc_cross_source_exact_observation_delta_evidence_ledger(
    datasets: tuple[RegisteredCanonicalBTCObservationSet, ...],
    policy: BTCCrossSourceReconciliationPolicy,
    result: BTCCrossSourceReconciliationResult,
) -> BTCCrossSourceExactObservationDeltaEvidenceLedger:
    rows = tuple(datasets)
    if len(rows) < 2 or not all(isinstance(item, RegisteredCanonicalBTCObservationSet) for item in rows):
        raise TypeError("ledger requires at least two typed FCP-0023 datasets")
    if not isinstance(policy, BTCCrossSourceReconciliationPolicy):
        raise TypeError("policy must be a typed FCP-0023 policy")
    if not isinstance(result, BTCCrossSourceReconciliationResult):
        raise TypeError("result must be a typed FCP-0023 reconciliation result")
    recomputed = reconcile_canonical_btc_observation_sets(rows, policy)
    if result != recomputed:
        raise ValueError("ledger inputs disagree with FCP-0023 reconciliation evidence")
    ordered = tuple(sorted(rows, key=lambda item: item.dataset_id))
    entries: list[BTCObservationDeltaEvidenceEntry] = []
    pair_key_count = 0
    for left_dataset, right_dataset in combinations(ordered, 2):
        left_rows = {comparison_key(item): item for item in left_dataset.observations}
        right_rows = {comparison_key(item): item for item in right_dataset.observations}
        keys = tuple(sorted(set(left_rows) | set(right_rows)))
        pair_key_count += len(keys)
        for key in keys:
            left = left_rows.get(key)
            right = right_rows.get(key)
            for field_name in ledger_fields(key[2]):
                entries.append(
                    _entry(
                        left_dataset,
                        right_dataset,
                        left,
                        right,
                        key,
                        field_name,
                    )
                )
    evidence = tuple(entries)
    lineage = tuple(
        BTCObservationDatasetLineage(
            dataset_id=item.dataset_id,
            dataset_hash=item.dataset_hash,
            source_id=item.source_id,
            artifact_id=item.artifact.artifact_id,
            artifact_hash=item.artifact.content_sha256,
        )
        for item in ordered
    )
    return BTCCrossSourceExactObservationDeltaEvidenceLedger(
        dataset_lineage=lineage,
        policy_id=policy.policy_id,
        policy_hash=policy.policy_hash,
        reconciliation_result_hash=result.result_hash,
        reconciliation_quality_state=result.quality_state,
        finding_hashes=tuple(item.finding_hash for item in result.findings),
        dataset_pair_count=len(ordered) * (len(ordered) - 1) // 2,
        pair_key_count=pair_key_count,
        entries=evidence,
        exact_match_entry_count=sum(item.comparison_state == "EXACT_MATCH" for item in evidence),
        delta_entry_count=sum(item.comparison_state == "DELTA_PRESENT" for item in evidence),
        incomplete_entry_count=sum(item.comparison_state == "PAIR_INCOMPLETE" for item in evidence),
    )
