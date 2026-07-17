from dataclasses import dataclass
from decimal import Decimal

from apps.v2_r2_historical_factor_baseline_app_1.contracts import (
    decimal_value,
    identifier,
    instant,
    utc,
)
from apps.v2_r7_local_market_session_registry_foundation_app_1 import SESSION_PHASES


DENOMINATOR_TYPES = ("FREE_FLOAT_SHARES", "TOTAL_SHARES", "VENDOR_TRADABLE_SHARES")
OUTPUT_UNITS = ("FRACTION", "PERCENT")
MAX_QUANTITY = Decimal("1E30")


def _sha256(value: object, name: str) -> str:
    normalized = str(value).strip()
    if len(normalized) != 64 or any(c not in "0123456789abcdef" for c in normalized):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


@dataclass(frozen=True)
class TurnoverPolicy:
    definition_id: str
    definition_version: str
    instrument_id: str
    phase: str
    interval_id: str
    slot_index: int
    denominator_type: str
    output_unit: str
    decimal_places: int = 6
    operator_registered: bool = True
    factor_activation_allowed: bool = False
    scoring_allowed: bool = False

    def __post_init__(self) -> None:
        for name in ("definition_id", "definition_version", "instrument_id", "interval_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        phase = str(self.phase).strip().upper()
        if phase not in SESSION_PHASES:
            raise ValueError("turnover phase is not registered")
        object.__setattr__(self, "phase", phase)
        denominator = str(self.denominator_type).strip().upper()
        if denominator not in DENOMINATOR_TYPES:
            raise ValueError("unsupported turnover denominator type")
        object.__setattr__(self, "denominator_type", denominator)
        unit = str(self.output_unit).strip().upper()
        if unit not in OUTPUT_UNITS:
            raise ValueError("turnover output unit must be FRACTION or PERCENT")
        object.__setattr__(self, "output_unit", unit)
        if isinstance(self.slot_index, bool) or self.slot_index < 0:
            raise ValueError("slot_index must be nonnegative")
        if isinstance(self.decimal_places, bool) or not 0 <= self.decimal_places <= 12:
            raise ValueError("decimal_places must be between 0 and 12")
        if self.operator_registered is not True:
            raise ValueError("turnover policy must be Operator-registered")
        if self.factor_activation_allowed or self.scoring_allowed:
            raise ValueError("turnover policy exceeds research-only scope")


@dataclass(frozen=True)
class RegisteredTurnoverObservation:
    observation_id: str
    session_evidence_hash: str
    instrument_id: str
    phase: str
    interval_id: str
    slot_index: int
    observed_at_utc: str
    volume_available_at_utc: str
    share_base_effective_at_utc: str
    share_base_available_at_utc: str
    traded_volume: Decimal
    share_base: Decimal
    denominator_type: str
    volume_source_artifact_hash: str
    share_base_source_artifact_hash: str
    registered_local_only: bool = True

    def __post_init__(self) -> None:
        for name in ("observation_id", "instrument_id", "interval_id"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        object.__setattr__(self, "session_evidence_hash", _sha256(self.session_evidence_hash, "session_evidence_hash"))
        phase = str(self.phase).strip().upper()
        if phase not in SESSION_PHASES:
            raise ValueError("turnover observation phase is not registered")
        object.__setattr__(self, "phase", phase)
        denominator = str(self.denominator_type).strip().upper()
        if denominator not in DENOMINATOR_TYPES:
            raise ValueError("unsupported turnover denominator type")
        object.__setattr__(self, "denominator_type", denominator)
        if isinstance(self.slot_index, bool) or self.slot_index < 0:
            raise ValueError("slot_index must be nonnegative")
        for name in ("observed_at_utc", "volume_available_at_utc", "share_base_effective_at_utc", "share_base_available_at_utc"):
            object.__setattr__(self, name, utc(getattr(self, name), name))
        if instant(self.volume_available_at_utc) < instant(self.observed_at_utc):
            raise ValueError("volume availability precedes observation")
        if instant(self.share_base_available_at_utc) < instant(self.share_base_effective_at_utc):
            raise ValueError("share-base availability precedes effective time")
        if instant(self.share_base_effective_at_utc) > instant(self.observed_at_utc):
            raise ValueError("future-effective share base is prohibited")
        traded = decimal_value(self.traded_volume, "traded_volume")
        base = decimal_value(self.share_base, "share_base")
        if traded < 0 or traded > MAX_QUANTITY:
            raise ValueError("traded volume is outside bounded scope")
        if base < 0 or base > MAX_QUANTITY:
            raise ValueError("share base is outside bounded scope")
        object.__setattr__(self, "traded_volume", traded)
        object.__setattr__(self, "share_base", base)
        for name in ("volume_source_artifact_hash", "share_base_source_artifact_hash"):
            object.__setattr__(self, name, _sha256(getattr(self, name), name))
        if self.registered_local_only is not True:
            raise ValueError("turnover observation must remain registered and local")
