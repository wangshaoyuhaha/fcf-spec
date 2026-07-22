from __future__ import annotations

import hashlib
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import instant
from apps.fcp_0077_a_share_trusted_data_supply_chain_coverage_evidence_matrix_app_1 import (
    RegisteredImplementationEvidence,
    build_coverage_matrix,
    coverage_requirements,
    current_repository_evidence,
)
from apps.fcp_0078_a_share_publication_availability_clock_contract_app_1 import (
    publication_clock_implementation_evidence,
)

from .contracts import (
    AdjustmentFactorRevision,
    CorporateActionRevision,
    PriceLineageResolution,
    PriceQueryPolicy,
    RawPriceReference,
)


_CONTRACT_PATH = (
    "apps/fcp_0079_a_share_corporate_action_query_policy_lineage_contract_app_1/"
    "contracts.py"
)


def _validate_chain(records: tuple[object, ...], identity_name: str) -> None:
    by_hash = {item.record_hash: item for item in records}
    identities = tuple((getattr(item, identity_name), item.revision_number) for item in records)
    if len(by_hash) != len(records) or len(set(identities)) != len(identities):
        raise ValueError("revision identities and hashes must be unique")
    for item in records:
        if item.revision_number == 0:
            continue
        predecessor = by_hash.get(item.revises_record_hash)
        if predecessor is None:
            raise ValueError("revision predecessor is not registered")
        if getattr(predecessor, identity_name) != getattr(item, identity_name):
            raise ValueError("revision predecessor belongs to another identity")
        if predecessor.revision_number != item.revision_number - 1:
            raise ValueError("revision numbers must be contiguous")
        previous_time = (
            predecessor.observable_at_utc
            if isinstance(predecessor, CorporateActionRevision)
            else predecessor.factor_available_at_utc
        )
        current_time = (
            item.observable_at_utc
            if isinstance(item, CorporateActionRevision)
            else item.factor_available_at_utc
        )
        if instant(previous_time, "previous_revision_time") >= instant(
            current_time,
            "current_revision_time",
        ):
            raise ValueError("revision time must follow predecessor")


def resolve_price_lineage(
    actions: tuple[CorporateActionRevision, ...],
    factors: tuple[AdjustmentFactorRevision, ...],
    *,
    raw_price: RawPriceReference,
    policy: PriceQueryPolicy,
    evaluated_at_utc: str,
) -> PriceLineageResolution:
    if not isinstance(actions, tuple) or not all(isinstance(item, CorporateActionRevision) for item in actions):
        raise TypeError("actions must contain CorporateActionRevision")
    if not isinstance(factors, tuple) or not all(isinstance(item, AdjustmentFactorRevision) for item in factors):
        raise TypeError("factors must contain AdjustmentFactorRevision")
    if not isinstance(raw_price, RawPriceReference) or not isinstance(policy, PriceQueryPolicy):
        raise TypeError("raw_price and policy must be typed contracts")
    _validate_chain(actions, "action_id")
    _validate_chain(factors, "factor_id")
    evaluated = instant(evaluated_at_utc, "evaluated_at_utc")
    if instant(raw_price.revision_at_utc, "revision_at_utc") > evaluated:
        raise ValueError("raw price revision is not observable at query time")
    matching_actions = tuple(
        item
        for item in actions
        if item.instrument_id == raw_price.instrument_id
        and item.effective_date <= raw_price.trade_date
        and instant(item.observable_at_utc, "observable_at_utc") <= evaluated
    )
    selected_by_action = {}
    for item in sorted(matching_actions, key=lambda value: (value.action_id, value.revision_number, value.record_hash)):
        selected_by_action[item.action_id] = item
    selected_actions = tuple(
        item for item in selected_by_action.values() if item.revision_state != "CANCELLED"
    )
    action_hashes = tuple(sorted(item.record_hash for item in selected_actions))
    if policy.price_view == "RAW":
        return PriceLineageResolution(
            raw_price=raw_price,
            policy=policy,
            evaluated_at_utc=evaluated_at_utc,
            resolution_state="RAW_RESOLVED",
            selected_action_hashes=action_hashes,
            selected_factor=None,
        )
    observable_factors = tuple(
        sorted(
            (
                item
                for item in factors
                if item.instrument_id == raw_price.instrument_id
                and item.trade_date == raw_price.trade_date
                and item.revision_state != "CANCELLED"
                and instant(item.factor_available_at_utc, "factor_available_at_utc") <= evaluated
            ),
            key=lambda item: (item.revision_number, item.factor_available_at_utc, item.record_hash),
        )
    )
    if not observable_factors:
        return PriceLineageResolution(
            raw_price=raw_price,
            policy=policy,
            evaluated_at_utc=evaluated_at_utc,
            resolution_state="FACTOR_NOT_OBSERVABLE",
            selected_action_hashes=action_hashes,
            selected_factor=None,
        )
    selected_factor = observable_factors[-1]
    if selected_factor.action_record_hashes != action_hashes:
        return PriceLineageResolution(
            raw_price=raw_price,
            policy=policy,
            evaluated_at_utc=evaluated_at_utc,
            resolution_state="ACTION_LINEAGE_MISMATCH",
            selected_action_hashes=action_hashes,
            selected_factor=None,
        )
    return PriceLineageResolution(
        raw_price=raw_price,
        policy=policy,
        evaluated_at_utc=evaluated_at_utc,
        resolution_state="ADJUSTED_RESOLVED",
        selected_action_hashes=action_hashes,
        selected_factor=selected_factor,
    )


def price_lineage_implementation_evidence(
    repository_root: str | Path,
    *,
    observed_at_utc: str,
) -> RegisteredImplementationEvidence:
    root = Path(repository_root).resolve()
    path = root.joinpath(*_CONTRACT_PATH.split("/"))
    resolved = path.resolve(strict=True)
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("price lineage evidence escapes repository root") from exc
    if resolved.is_symlink() or not resolved.is_file():
        raise ValueError("price lineage evidence must be a regular tracked file")
    return RegisteredImplementationEvidence(
        component_id="gap089-corporate-action-query-policy-lineage",
        gap_id="V2-FR-GAP-089",
        repository_path=_CONTRACT_PATH,
        artifact_sha256=hashlib.sha256(resolved.read_bytes()).hexdigest(),
        capabilities=("CORPORATE_ACTION_LINEAGE", "QUERY_POLICY_LINEAGE"),
        observed_at_utc=observed_at_utc,
    )


def build_augmented_coverage_matrix(
    repository_root: str | Path,
    *,
    evaluated_at_utc: str,
):
    return build_coverage_matrix(
        repository_root,
        coverage_requirements(),
        current_repository_evidence(repository_root, observed_at_utc=evaluated_at_utc)
        + (
            publication_clock_implementation_evidence(
                repository_root,
                observed_at_utc=evaluated_at_utc,
            ),
            price_lineage_implementation_evidence(
                repository_root,
                observed_at_utc=evaluated_at_utc,
            ),
        ),
        evaluated_at_utc=evaluated_at_utc,
    )
