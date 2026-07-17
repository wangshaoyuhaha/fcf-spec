from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from .ledger import ChannelIndicatorLedger


@dataclass(frozen=True)
class ChannelIndicatorReadModel:
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", MappingProxyType(dict(self.payload)))


def build_read_model(ledger: ChannelIndicatorLedger) -> ChannelIndicatorReadModel:
    ready = sum(item.state == "CHANNEL_READY" for item in ledger.evidence)
    return ChannelIndicatorReadModel(
        {
            "evidence_count": len(ledger.evidence),
            "ready_count": ready,
            "blocked_count": len(ledger.evidence) - ready,
            "breakout_signal": False,
            "prediction": False,
            "score_rank_or_signal": False,
            "recommendation": False,
            "network_access": False,
            "order_or_execution": False,
            "operator_review_required": True,
            "read_only": True,
        }
    )
