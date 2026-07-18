from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .registry import LocalInstitutionalCalendarRegistry


@dataclass(frozen=True)
class LocalInstitutionalCalendarReadModel:
    payload: Mapping[str, object]


def build_read_model(
    registry: LocalInstitutionalCalendarRegistry,
) -> LocalInstitutionalCalendarReadModel:
    event_keys = tuple(
        sorted({(record.calendar_id, record.event_id) for record in registry.records})
    )
    payload = MappingProxyType(
        {
            "record_count": len(registry.records),
            "event_count": len(event_keys),
            "event_keys": event_keys,
            "record_hashes": tuple(record.record_hash for record in registry.records),
            "registered_artifact_only": True,
            "operator_review_required": True,
            "network_source": False,
            "live_calendar_service": False,
            "system_clock_authority": False,
            "recurring_rule_confirmation": False,
            "revision_replacement": False,
            "factor_or_score": False,
            "signal_or_recommendation": False,
            "order_or_execution": False,
        }
    )
    return LocalInstitutionalCalendarReadModel(payload=payload)
