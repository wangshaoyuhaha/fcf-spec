from __future__ import annotations

import hashlib
from pathlib import Path

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    instant,
)
from apps.fcp_0077_a_share_trusted_data_supply_chain_coverage_evidence_matrix_app_1 import (
    RegisteredImplementationEvidence,
    build_coverage_matrix,
    coverage_requirements,
    current_repository_evidence,
)

from .contracts import PublicationAvailabilityClock, PublicationClockResolution


_CONTRACT_PATH = (
    "apps/fcp_0078_a_share_publication_availability_clock_contract_app_1/"
    "contracts.py"
)


def _validate_revision_chain(records: tuple[PublicationAvailabilityClock, ...]) -> None:
    by_hash = {item.record_hash: item for item in records}
    identities = tuple((item.subject_id, item.revision_number) for item in records)
    if len(set(identities)) != len(identities):
        raise ValueError("subject revision numbers must be unique")
    if len(by_hash) != len(records):
        raise ValueError("publication clock hashes must be unique")
    for item in records:
        if item.revision_number == 0:
            continue
        predecessor = by_hash.get(item.revises_record_hash)
        if predecessor is None:
            raise ValueError("revision predecessor is not registered")
        if predecessor.subject_id != item.subject_id:
            raise ValueError("revision predecessor belongs to another subject")
        if predecessor.source.source_hash != item.source.source_hash:
            raise ValueError("revision predecessor belongs to another source")
        if predecessor.revision_number != item.revision_number - 1:
            raise ValueError("revision numbers must be contiguous")
        if instant(predecessor.revision_at_utc, "revision_at_utc") >= instant(
            item.revision_at_utc,
            "revision_at_utc",
        ):
            raise ValueError("revision time must follow predecessor")


def resolve_publication_clock(
    records: tuple[PublicationAvailabilityClock, ...],
    *,
    subject_id: str,
    evaluated_at_utc: str,
) -> PublicationClockResolution:
    if not isinstance(records, tuple) or not all(
        isinstance(item, PublicationAvailabilityClock) for item in records
    ):
        raise TypeError("records must contain PublicationAvailabilityClock")
    _validate_revision_chain(records)
    evaluated = instant(evaluated_at_utc, "evaluated_at_utc")
    matching = tuple(item for item in records if item.subject_id == subject_id)
    observable = tuple(
        sorted(
            (
                item
                for item in matching
                if instant(item.ingested_at_utc, "ingested_at_utc") <= evaluated
                and instant(item.revision_at_utc, "revision_at_utc") <= evaluated
                and instant(item.source.registered_at_utc, "registered_at_utc")
                <= evaluated
            ),
            key=lambda item: (item.revision_number, item.revision_at_utc, item.record_hash),
        )
    )
    if not observable:
        return PublicationClockResolution(
            subject_id=subject_id,
            evaluated_at_utc=evaluated_at_utc,
            resolution_state="NOT_YET_OBSERVABLE",
            selected_record=None,
            observed_record_hashes=(),
        )
    selected = observable[-1]
    state = (
        "BLOCKED_CANCELLED"
        if selected.revision_state == "CANCELLED"
        else "EXACT_AVAILABLE"
        if selected.publication_state == "EXACT_OBSERVED"
        else "BLOCKED_DATE_ONLY"
        if selected.publication_state == "DATE_ONLY_BLOCKED"
        else "BLOCKED_UNKNOWN"
    )
    return PublicationClockResolution(
        subject_id=subject_id,
        evaluated_at_utc=evaluated_at_utc,
        resolution_state=state,
        selected_record=selected,
        observed_record_hashes=tuple(sorted(item.record_hash for item in observable)),
    )


def publication_clock_implementation_evidence(
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
        raise ValueError("publication clock evidence escapes repository root") from exc
    if resolved.is_symlink() or not resolved.is_file():
        raise ValueError("publication clock evidence must be a regular tracked file")
    return RegisteredImplementationEvidence(
        component_id="gap088-publication-clock-contract",
        gap_id="V2-FR-GAP-088",
        repository_path=_CONTRACT_PATH,
        artifact_sha256=hashlib.sha256(resolved.read_bytes()).hexdigest(),
        capabilities=("PUBLICATION_CLOCK",),
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
        current_repository_evidence(
            repository_root,
            observed_at_utc=evaluated_at_utc,
        )
        + (
            publication_clock_implementation_evidence(
                repository_root,
                observed_at_utc=evaluated_at_utc,
            ),
        ),
        evaluated_at_utc=evaluated_at_utc,
    )
