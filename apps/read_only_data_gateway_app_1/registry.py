from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from types import MappingProxyType
from typing import Mapping

from .contracts import RegisteredArtifactSource


class RegisteredArtifactRegistry:
    def __init__(self, sources: Iterable[RegisteredArtifactSource]) -> None:
        supplied = tuple(sources)
        if not all(isinstance(item, RegisteredArtifactSource) for item in supplied):
            raise TypeError("registry entries must be RegisteredArtifactSource values")
        records = tuple(sorted(supplied, key=lambda item: item.source_id))
        if not records:
            raise ValueError("registered artifact registry must not be empty")

        source_ids = [item.source_id for item in records]
        evidence_ids = [item.evidence_id for item in records]
        relative_paths = [item.relative_path for item in records]
        for field_name, values in (
            ("source_id", source_ids),
            ("evidence_id", evidence_ids),
            ("relative_path", relative_paths),
        ):
            if len(values) != len(set(values)):
                raise ValueError(f"duplicate registered artifact {field_name}")

        self._sources = records
        self._by_source_id: Mapping[str, RegisteredArtifactSource] = MappingProxyType(
            {item.source_id: item for item in records}
        )

    @property
    def sources(self) -> tuple[RegisteredArtifactSource, ...]:
        return self._sources

    @property
    def source_ids(self) -> tuple[str, ...]:
        return tuple(self._by_source_id)

    @property
    def registry_sha256(self) -> str:
        payload = [dict(item.as_payload()) for item in self._sources]
        canonical = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        return hashlib.sha256(canonical).hexdigest()

    def require(self, source_id: str) -> RegisteredArtifactSource:
        try:
            return self._by_source_id[source_id]
        except KeyError as exc:
            raise KeyError(f"unregistered source_id: {source_id}") from exc

    def as_payload(self) -> Mapping[str, object]:
        return MappingProxyType(
            {
                "registered_source_count": len(self._sources),
                "registry_sha256": self.registry_sha256,
                "source_ids": self.source_ids,
                "sources": tuple(item.as_payload() for item in self._sources),
            }
        )
