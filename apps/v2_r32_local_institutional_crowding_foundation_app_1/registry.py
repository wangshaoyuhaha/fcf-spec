from dataclasses import dataclass, replace

from .contracts import (
    InstitutionalCrowdingRecord,
    RegisteredInstitutionalHoldingDisclosure,
)


@dataclass(frozen=True)
class LocalInstitutionalCrowdingRegistry:
    disclosures: tuple[RegisteredInstitutionalHoldingDisclosure, ...] = ()
    records: tuple[InstitutionalCrowdingRecord, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        disclosures, records = tuple(self.disclosures), tuple(self.records)
        if (
            isinstance(self.capacity, bool)
            or not 1 <= self.capacity <= 100000
            or len(disclosures) + len(records) > self.capacity
        ):
            raise ValueError("institutional crowding registry capacity is invalid")
        if len({item.disclosure_id for item in disclosures}) != len(disclosures):
            raise ValueError("duplicate disclosure id is prohibited")
        if len({item.disclosure_hash for item in disclosures}) != len(disclosures):
            raise ValueError("duplicate disclosure evidence is prohibited")
        if len({item.record_id for item in records}) != len(records):
            raise ValueError("duplicate crowding record id is prohibited")
        hashes = {item.disclosure_hash for item in disclosures}
        if any(
            any(item.disclosure_hash not in hashes for item in record.disclosures)
            for record in records
        ):
            raise ValueError("crowding record disclosures must be registered")
        object.__setattr__(self, "disclosures", disclosures)
        object.__setattr__(self, "records", records)

    def append_disclosure(
        self, item: RegisteredInstitutionalHoldingDisclosure
    ) -> "LocalInstitutionalCrowdingRegistry":
        if not isinstance(item, RegisteredInstitutionalHoldingDisclosure):
            raise ValueError("registry accepts holding disclosures only")
        return replace(self, disclosures=(*self.disclosures, item))

    def append_record(
        self, item: InstitutionalCrowdingRecord
    ) -> "LocalInstitutionalCrowdingRegistry":
        if not isinstance(item, InstitutionalCrowdingRecord):
            raise ValueError("registry accepts crowding records only")
        return replace(self, records=(*self.records, item))
