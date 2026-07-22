from __future__ import annotations

from .contracts import (
    BTCPerpetualPaperEvidenceReference,
    BTCPerpetualPaperSignalEvidenceSeparationContract,
)


def build_btc_perpetual_paper_signal_evidence_separation_contract(
    references: tuple[BTCPerpetualPaperEvidenceReference, ...],
    *,
    created_at_utc: str,
    contract_id: str = "btc-perpetual-paper-signal-evidence-separation-v1",
) -> BTCPerpetualPaperSignalEvidenceSeparationContract:
    return BTCPerpetualPaperSignalEvidenceSeparationContract(
        contract_id=contract_id,
        references=references,
        created_at_utc=created_at_utc,
    )
