from __future__ import annotations

from dataclasses import dataclass, replace

from .contracts import FactorValidationPacket, ValidationCheckEvidence


@dataclass(frozen=True)
class LocalFactorValidationEvidenceRegistry:
    checks: tuple[ValidationCheckEvidence, ...] = ()
    packets: tuple[FactorValidationPacket, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        checks, packets = tuple(self.checks), tuple(self.packets)
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000 or len(checks) + len(packets) > self.capacity:
            raise ValueError("factor validation registry capacity is invalid")
        if len({item.check_id for item in checks}) != len(checks) or len({item.check_hash for item in checks}) != len(checks):
            raise ValueError("duplicate validation check is prohibited")
        keys = {(item.candidate_id, item.check_type) for item in checks}
        if len(keys) != len(checks):
            raise ValueError("validation check type cannot be overwritten for a candidate")
        if len({item.packet_id for item in packets}) != len(packets):
            raise ValueError("duplicate validation packet is prohibited")
        hashes = {item.check_hash for item in checks}
        if any(any(check.check_hash not in hashes for check in packet.checks) for packet in packets):
            raise ValueError("validation packet checks must be registered")
        object.__setattr__(self, "checks", checks)
        object.__setattr__(self, "packets", packets)

    def append_check(self, item: ValidationCheckEvidence) -> "LocalFactorValidationEvidenceRegistry":
        if not isinstance(item, ValidationCheckEvidence):
            raise ValueError("registry accepts ValidationCheckEvidence only")
        return replace(self, checks=(*self.checks, item))

    def append_packet(self, item: FactorValidationPacket) -> "LocalFactorValidationEvidenceRegistry":
        if not isinstance(item, FactorValidationPacket):
            raise ValueError("registry accepts FactorValidationPacket only")
        return replace(self, packets=(*self.packets, item))
