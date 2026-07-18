import hashlib
import json
from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier, instant, utc

from .contracts import PolicyLanguageChangeRecord, RegisteredPolicyDocumentObservation
from .registry import LocalPolicyLanguageEvidenceRegistry


@dataclass(frozen=True)
class PolicyLanguageEvidenceSnapshot:
    document_series_id: str
    market: str
    evaluated_at_utc: str
    state: str
    documents: tuple[RegisteredPolicyDocumentObservation, ...]
    record: PolicyLanguageChangeRecord | None
    reason_codes: tuple[str, ...]
    operator_review_required: bool
    snapshot_hash: str

    def __post_init__(self) -> None:
        allowed = {"MISSING_DOCUMENT", "MISSING", "STALE", "CONFLICT", "MISSING_COMPARISON", "RESOLVED"}
        if self.state not in allowed or self.operator_review_required is not True:
            raise ValueError("invalid policy language snapshot")


def resolve_policy_language_evidence(
    registry: LocalPolicyLanguageEvidenceRegistry,
    *,
    document_series_id: str,
    market: str,
    as_of_utc: str,
) -> PolicyLanguageEvidenceSnapshot:
    series_id = identifier(document_series_id, "document_series_id")
    market_id = identifier(market, "market")
    evaluated = utc(as_of_utc, "as_of_utc")
    as_of = instant(evaluated)
    documents = tuple(sorted((item for item in registry.documents if item.document_series_id == series_id and item.market == market_id and instant(item.available_at_utc) <= as_of), key=lambda item: (item.available_at_utc, item.document_id)))
    states = {item.document_state for item in documents}
    record = next((item for item in reversed(registry.records) if len(documents) >= 2 and item.prior_document.document_hash == documents[-2].document_hash and item.current_document.document_hash == documents[-1].document_hash and instant(item.available_at_utc) <= as_of), None)
    if not documents:
        state, reasons = "MISSING_DOCUMENT", ["NO_REGISTERED_POLICY_DOCUMENT_AT_AS_OF"]
    elif "CONFLICT" in states:
        state, reasons = "CONFLICT", ["REGISTERED_POLICY_DOCUMENT_IS_CONFLICTED"]
    elif "STALE" in states:
        state, reasons = "STALE", ["REGISTERED_POLICY_DOCUMENT_IS_STALE"]
    elif "MISSING" in states:
        state, reasons = "MISSING", ["REGISTERED_POLICY_DOCUMENT_IS_MISSING"]
    elif len(documents) < 2 or record is None:
        state, reasons = "MISSING_COMPARISON", ["NO_REGISTERED_POLICY_LANGUAGE_COMPARISON_AT_AS_OF"]
    else:
        state, reasons = "RESOLVED", ["REGISTERED_POLICY_LANGUAGE_CHANGE_RESOLVED", "NO_SEMANTIC_DIRECTION", "NO_INDUSTRY_BENEFIT", "NO_POLICY_CAUSATION", "NO_AUTOMATIC_TAXONOMY_MAPPING"]
    payload = {"documents": [item.document_hash for item in documents], "evaluated_at_utc": evaluated, "market": market_id, "reasons": reasons, "record": None if record is None else record.record_hash, "series_id": series_id, "state": state}
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()
    return PolicyLanguageEvidenceSnapshot(series_id, market_id, evaluated, state, documents, record, tuple(reasons), True, digest)
