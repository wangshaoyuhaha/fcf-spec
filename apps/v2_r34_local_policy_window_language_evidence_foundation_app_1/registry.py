from dataclasses import dataclass, replace

from .contracts import PolicyLanguageChangeRecord, RegisteredPolicyDocumentObservation


@dataclass(frozen=True)
class LocalPolicyLanguageEvidenceRegistry:
    documents: tuple[RegisteredPolicyDocumentObservation, ...] = ()
    records: tuple[PolicyLanguageChangeRecord, ...] = ()
    capacity: int = 10000

    def __post_init__(self) -> None:
        documents, records = tuple(self.documents), tuple(self.records)
        if isinstance(self.capacity, bool) or not 1 <= self.capacity <= 100000 or len(documents) + len(records) > self.capacity:
            raise ValueError("policy language registry capacity is invalid")
        if len({item.document_id for item in documents}) != len(documents) or len({item.document_hash for item in documents}) != len(documents):
            raise ValueError("duplicate policy document is prohibited")
        if len({item.record_id for item in records}) != len(records):
            raise ValueError("duplicate policy language record is prohibited")
        hashes = {item.document_hash for item in documents}
        if any(item.prior_document.document_hash not in hashes or item.current_document.document_hash not in hashes for item in records):
            raise ValueError("policy comparison documents must be registered")
        object.__setattr__(self, "documents", documents)
        object.__setattr__(self, "records", records)

    def append_document(self, item: RegisteredPolicyDocumentObservation) -> "LocalPolicyLanguageEvidenceRegistry":
        if not isinstance(item, RegisteredPolicyDocumentObservation):
            raise ValueError("registry accepts policy documents only")
        return replace(self, documents=(*self.documents, item))

    def append_record(self, item: PolicyLanguageChangeRecord) -> "LocalPolicyLanguageEvidenceRegistry":
        if not isinstance(item, PolicyLanguageChangeRecord):
            raise ValueError("registry accepts policy language records only")
        return replace(self, records=(*self.records, item))
