from __future__ import annotations

from dataclasses import dataclass

from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import instant, utc

from .contracts import AnomalyRule
from .detector import AnomalyEvidence


@dataclass(frozen=True)
class ResearchAlertLedger:
    records: tuple[AnomalyEvidence, ...] = ()

    def __post_init__(self) -> None:
        records = tuple(self.records)
        if not all(isinstance(record, AnomalyEvidence) for record in records):
            raise ValueError("ledger accepts AnomalyEvidence only")
        hashes = [record.evidence_hash for record in records]
        if len(hashes) != len(set(hashes)):
            raise ValueError("duplicate anomaly evidence is prohibited")
        natural = [
            (record.rule_id, record.rule_version, record.event_id)
            for record in records
        ]
        if len(natural) != len(set(natural)):
            raise ValueError("duplicate rule event is prohibited")
        object.__setattr__(self, "records", records)

    def register(
        self,
        evidence: AnomalyEvidence,
        rule: AnomalyRule,
    ) -> ResearchAlertLedger:
        if evidence.rule_id != rule.rule_id or evidence.rule_version != rule.rule_version:
            raise ValueError("evidence and rule identity mismatch")
        if evidence.evidence_hash in {record.evidence_hash for record in self.records}:
            raise ValueError("duplicate anomaly evidence is prohibited")
        if evidence.state == "CONFIRMED":
            previous = next(
                (
                    record
                    for record in reversed(self.records)
                    if record.rule_id == rule.rule_id
                    and record.stream_id == evidence.stream_id
                    and record.state == "CONFIRMED"
                ),
                None,
            )
            if previous is not None:
                elapsed = (
                    instant(evidence.observed_at_utc)
                    - instant(previous.observed_at_utc)
                ).total_seconds()
                if elapsed < rule.cooldown_seconds:
                    raise ValueError("anomaly cooldown is active")
        return ResearchAlertLedger(self.records + (evidence,))

    def active(self, *, as_of_utc: str) -> tuple[AnomalyEvidence, ...]:
        as_of = instant(utc(as_of_utc, "as_of_utc"))
        return tuple(
            record for record in self.records if instant(record.expires_at_utc) > as_of
        )
