from __future__ import annotations

from dataclasses import dataclass, field
import re

from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1.contracts import canonical_sha256
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import identifier, utc


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be lowercase SHA-256")
    result = value
    if _SHA256.fullmatch(result) is None:
        raise ValueError(f"{name} must be lowercase SHA-256")
    return result


@dataclass(frozen=True)
class MarketDataReadinessRow:
    market: str
    reconciliation_result_hash: str
    dataset_hashes: tuple[str, ...]
    dataset_ids: tuple[str, ...]
    quality_state: str
    blocking_finding_count: int
    warning_finding_count: int
    union_key_count: int
    overlap_key_count: int
    readiness_state: str
    source_selected: bool = False
    row_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if self.market not in {"A_SHARE", "BTC"}:
            raise ValueError("market is not registered")
        if self.quality_state not in {"CONSISTENT", "QUARANTINE_REVIEW_REQUIRED"}:
            raise ValueError("quality_state is not registered")
        expected = "READY_FOR_OPERATOR_REVIEW" if self.quality_state == "CONSISTENT" else "QUARANTINE_REVIEW_REQUIRED"
        if self.readiness_state != expected:
            raise ValueError("readiness_state and quality_state disagree")
        result_hash = _digest(self.reconciliation_result_hash, "reconciliation_result_hash")
        dataset_hashes = tuple(_digest(item, "dataset_hash") for item in self.dataset_hashes)
        if any(not isinstance(item, str) for item in self.dataset_ids):
            raise ValueError("dataset_id must be text")
        dataset_ids = tuple(identifier(item, "dataset_id") for item in self.dataset_ids)
        if len(dataset_hashes) < 2 or len(dataset_hashes) != len(set(dataset_hashes)):
            raise ValueError("readiness row requires distinct dataset hashes")
        if (
            len(dataset_ids) != len(dataset_hashes)
            or len(dataset_ids) != len(set(dataset_ids))
            or dataset_ids != tuple(sorted(dataset_ids))
        ):
            raise ValueError("readiness row requires ordered dataset identity and digest pairs")
        if self.source_selected is not False:
            raise ValueError("readiness row cannot select a source")
        counts = (self.blocking_finding_count, self.warning_finding_count, self.union_key_count, self.overlap_key_count)
        if any(isinstance(item, bool) or not isinstance(item, int) or item < 0 for item in counts):
            raise ValueError("readiness counts must be nonnegative")
        if self.overlap_key_count > self.union_key_count:
            raise ValueError("readiness coverage counts are inconsistent")
        if (self.quality_state == "QUARANTINE_REVIEW_REQUIRED") != (self.blocking_finding_count > 0):
            raise ValueError("blocking findings and quality_state disagree")
        object.__setattr__(self, "reconciliation_result_hash", result_hash)
        object.__setattr__(self, "dataset_hashes", dataset_hashes)
        object.__setattr__(self, "dataset_ids", dataset_ids)
        object.__setattr__(
            self,
            "row_hash",
            canonical_sha256(
                {
                    "blocking_finding_count": self.blocking_finding_count,
                    "dataset_lineage": list(zip(dataset_ids, dataset_hashes, strict=True)),
                    "market": self.market,
                    "overlap_key_count": self.overlap_key_count,
                    "quality_state": self.quality_state,
                    "readiness_state": self.readiness_state,
                    "reconciliation_result_hash": result_hash,
                    "union_key_count": self.union_key_count,
                    "warning_finding_count": self.warning_finding_count,
                }
            ),
        )


@dataclass(frozen=True)
class CrossMarketDataReadinessPacket:
    rows: tuple[MarketDataReadinessRow, ...]
    as_of_utc: str
    aggregate_state: str
    operator_review_required: bool = True
    source_selected: bool = False
    calculation_authority: str = "DETERMINISTIC_ENGINE"
    evidence_authority: str = "REGISTERED_EVIDENCE"
    ai_role: str = "ADVISORY_ONLY"
    packet_hash: str = field(init=False)

    def __post_init__(self) -> None:
        rows = tuple(self.rows)
        if not all(isinstance(item, MarketDataReadinessRow) for item in rows):
            raise ValueError("packet rows must be typed readiness rows")
        if tuple(item.market for item in rows) != ("A_SHARE", "BTC"):
            raise ValueError("packet requires exact isolated A-share and BTC rows")
        expected = "READY_FOR_OPERATOR_REVIEW" if all(item.readiness_state == "READY_FOR_OPERATOR_REVIEW" for item in rows) else "QUARANTINE_REVIEW_REQUIRED"
        if self.aggregate_state != expected:
            raise ValueError("aggregate_state and market rows disagree")
        if self.operator_review_required is not True or self.source_selected is not False:
            raise ValueError("packet cannot bypass review or select a source")
        if (
            self.calculation_authority != "DETERMINISTIC_ENGINE"
            or self.evidence_authority != "REGISTERED_EVIDENCE"
            or self.ai_role != "ADVISORY_ONLY"
        ):
            raise ValueError("packet authority identities are immutable")
        as_of = utc(self.as_of_utc, "as_of_utc")
        object.__setattr__(self, "rows", rows)
        object.__setattr__(self, "as_of_utc", as_of)
        object.__setattr__(
            self,
            "packet_hash",
            canonical_sha256(
                {
                    "aggregate_state": self.aggregate_state,
                    "as_of_utc": as_of,
                    "row_hashes": [item.row_hash for item in rows],
                }
            ),
        )
