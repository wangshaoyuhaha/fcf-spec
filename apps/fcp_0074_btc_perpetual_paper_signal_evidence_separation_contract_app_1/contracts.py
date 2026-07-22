from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import (
    identifier,
    instant,
    utc,
)


EVIDENCE_DOMAIN_ORDER = (
    "REUSABLE_MARKET_SIGNAL",
    "CONTRACT_SEMANTICS",
    "LEVERAGE_MARGIN",
    "COST_FUNDING_EXECUTION",
    "LIQUIDATION_RISK",
    "OUTCOME_ACCOUNTING",
)


@dataclass(frozen=True)
class BTCPerpetualPaperEvidenceReference:
    artifact_id: str
    artifact_hash: str
    domain: str
    observed_at_utc: str
    registered_artifact: bool = True
    eligible_for_signal_reuse: bool = field(init=False)
    derivative_specific: bool = field(init=False)
    reference_hash: str = field(init=False)

    def __post_init__(self) -> None:
        artifact_id = identifier(self.artifact_id, "artifact_id")
        artifact_hash = digest(self.artifact_hash, "artifact_hash")
        if self.domain not in EVIDENCE_DOMAIN_ORDER:
            raise ValueError("evidence domain is not registered")
        observed = utc(self.observed_at_utc, "observed_at_utc")
        if self.registered_artifact is not True:
            raise ValueError("evidence reference must be a registered artifact")
        reusable = self.domain == "REUSABLE_MARKET_SIGNAL"
        object.__setattr__(self, "artifact_id", artifact_id)
        object.__setattr__(self, "artifact_hash", artifact_hash)
        object.__setattr__(self, "observed_at_utc", observed)
        object.__setattr__(self, "eligible_for_signal_reuse", reusable)
        object.__setattr__(self, "derivative_specific", not reusable)
        object.__setattr__(
            self,
            "reference_hash",
            canonical_sha256(
                {
                    "artifact_hash": artifact_hash,
                    "artifact_id": artifact_id,
                    "domain": self.domain,
                    "observed_at_utc": observed,
                }
            ),
        )


@dataclass(frozen=True)
class BTCPerpetualPaperSignalEvidenceSeparationContract:
    contract_id: str
    references: tuple[BTCPerpetualPaperEvidenceReference, ...]
    created_at_utc: str
    complete_domain_coverage: bool = True
    separation_only: bool = True
    signal_calculation_allowed: bool = False
    factor_promotion_allowed: bool = False
    strategy_selection_allowed: bool = False
    profitability_claim_allowed: bool = False
    account_state_allowed: bool = False
    order_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    schema_version: str = "btc-perpetual-paper-signal-evidence-separation-v1"
    reference_hashes: tuple[str, ...] = field(init=False)
    reusable_reference_hashes: tuple[str, ...] = field(init=False)
    derivative_reference_hashes: tuple[str, ...] = field(init=False)
    contract_hash: str = field(init=False)

    def __post_init__(self) -> None:
        contract_id = identifier(self.contract_id, "contract_id")
        references = tuple(self.references)
        if not references or any(
            type(item) is not BTCPerpetualPaperEvidenceReference for item in references
        ):
            raise ValueError("separation contract requires exact typed references")
        domains = tuple(item.domain for item in references)
        grouped = tuple(domain for domain in EVIDENCE_DOMAIN_ORDER if domain in domains)
        first_seen = tuple(dict.fromkeys(domains))
        if first_seen != EVIDENCE_DOMAIN_ORDER or grouped != EVIDENCE_DOMAIN_ORDER:
            raise ValueError("separation contract requires complete closed domain order")
        domain_positions = tuple(EVIDENCE_DOMAIN_ORDER.index(domain) for domain in domains)
        if domain_positions != tuple(sorted(domain_positions)):
            raise ValueError("separation contract references must be grouped by domain order")
        artifact_ids = tuple(item.artifact_id for item in references)
        artifact_hashes = tuple(item.artifact_hash for item in references)
        reference_hashes = tuple(item.reference_hash for item in references)
        if (
            len(set(artifact_ids)) != len(artifact_ids)
            or len(set(artifact_hashes)) != len(artifact_hashes)
            or len(set(reference_hashes)) != len(reference_hashes)
        ):
            raise ValueError("separation contract references must be unique")
        created = utc(self.created_at_utc, "created_at_utc")
        if any(instant(created) < instant(item.observed_at_utc) for item in references):
            raise ValueError("separation contract cannot precede registered evidence")
        forbidden = (
            self.signal_calculation_allowed,
            self.factor_promotion_allowed,
            self.strategy_selection_allowed,
            self.profitability_claim_allowed,
            self.account_state_allowed,
            self.order_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.complete_domain_coverage is not True
            or self.separation_only is not True
            or any(forbidden)
        ):
            raise ValueError("separation contract cannot calculate, promote, select, claim, act, or close")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("separation contract authority identities are immutable")
        if self.schema_version != "btc-perpetual-paper-signal-evidence-separation-v1":
            raise ValueError("schema_version is not registered")
        reusable = tuple(
            item.reference_hash for item in references if item.eligible_for_signal_reuse
        )
        derivative = tuple(
            item.reference_hash for item in references if item.derivative_specific
        )
        if set(reusable).intersection(derivative) or set(reusable).union(derivative) != set(reference_hashes):
            raise ValueError("separation contract reuse partition is invalid")
        object.__setattr__(self, "contract_id", contract_id)
        object.__setattr__(self, "references", references)
        object.__setattr__(self, "created_at_utc", created)
        object.__setattr__(self, "reference_hashes", reference_hashes)
        object.__setattr__(self, "reusable_reference_hashes", reusable)
        object.__setattr__(self, "derivative_reference_hashes", derivative)
        object.__setattr__(
            self,
            "contract_hash",
            canonical_sha256(
                {
                    "contract_id": contract_id,
                    "created_at_utc": created,
                    "domain_order": list(EVIDENCE_DOMAIN_ORDER),
                    "reference_hashes": list(reference_hashes),
                    "schema_version": self.schema_version,
                }
            ),
        )
