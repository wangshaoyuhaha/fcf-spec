from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping
from urllib.parse import urlsplit

from .contracts import (
    IntakeDescriptor,
    IntakeKind,
    IntakeValidationReceipt,
    canonical_sha256,
    require_text,
)


_EXTENSIONS = {
    IntakeKind.PDF: (".pdf",),
    IntakeKind.EXCEL: (".xlsx", ".xls"),
    IntakeKind.CSV: (".csv",),
    IntakeKind.JSON: (".json",),
    IntakeKind.LOCAL_FILE: (".pdf", ".xlsx", ".xls", ".csv", ".json", ".txt"),
}
_CREDENTIAL_MARKERS = (
    "api_key",
    "apikey",
    "password",
    "passwd",
    "private_key",
    "secret",
    "access_token",
    "refresh_token",
    "credential",
)


def _contains_credential_marker(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in _CREDENTIAL_MARKERS)


def _descriptor(raw: object) -> IntakeDescriptor:
    if not isinstance(raw, Mapping):
        raise ValueError("intake item must be an object")
    try:
        kind = IntakeKind(require_text(raw.get("kind", ""), "kind").upper())
    except ValueError as exc:
        raise ValueError("unsupported intake kind") from exc
    descriptor = IntakeDescriptor(
        item_id=raw.get("item_id", ""),
        kind=kind,
        display_name=raw.get("display_name", ""),
        media_type=raw.get("media_type", ""),
        size_bytes=raw.get("size_bytes", -1),
        content_sha256=raw.get("content_sha256", ""),
        source_reference=raw.get("source_reference", ""),
    )
    inspected = f"{descriptor.display_name} {descriptor.source_reference}"
    if _contains_credential_marker(inspected):
        raise ValueError("credential-like intake metadata is prohibited")
    expected_extensions = _EXTENSIONS.get(kind)
    if expected_extensions and not descriptor.display_name.lower().endswith(
        expected_extensions
    ):
        raise ValueError(f"{kind.value} intake extension is not allowed")
    if kind == IntakeKind.URL:
        parsed = urlsplit(descriptor.source_reference)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.fragment
        ):
            raise ValueError("approved URL must be credential-free HTTPS")
    if kind == IntakeKind.TEXT and descriptor.source_reference:
        raise ValueError("text intake cannot contain a source reference")
    return descriptor


class GovernedIntakeService:
    def validate(
        self,
        payload: Mapping[str, Any],
        peer_host: str,
    ) -> IntakeValidationReceipt:
        if peer_host != "127.0.0.1":
            raise ValueError("intake peer must be exactly 127.0.0.1")
        if not isinstance(payload, Mapping):
            raise ValueError("intake payload must be an object")
        if payload.get("confirmed") is not True:
            raise ValueError("explicit Operator confirmation is required")
        request_id = require_text(payload.get("request_id", ""), "request_id")
        correlation_id = require_text(
            payload.get("correlation_id", ""),
            "correlation_id",
        )
        operator_id = require_text(payload.get("operator_id", ""), "operator_id")
        raw_items = payload.get("items")
        if not isinstance(raw_items, list) or not 1 <= len(raw_items) <= 20:
            raise ValueError("intake items must contain between 1 and 20 items")
        descriptors = tuple(_descriptor(item) for item in raw_items)
        item_ids = tuple(item.item_id for item in descriptors)
        if len(set(item_ids)) != len(item_ids):
            raise ValueError("intake item ids must be unique")
        required_governance = (
            "source_classification",
            "trust_classification",
            "freshness_classification",
            "licensing_status",
        )
        for field_name in required_governance:
            require_text(payload.get(field_name, ""), field_name)
        canonical = MappingProxyType(
            {
                "confirmed": True,
                "correlation_id": correlation_id,
                "freshness_classification": payload["freshness_classification"],
                "items": [
                    {
                        "content_sha256": item.content_sha256,
                        "display_name": item.display_name,
                        "item_id": item.item_id,
                        "kind": item.kind.value,
                        "media_type": item.media_type,
                        "size_bytes": item.size_bytes,
                        "source_reference": item.source_reference,
                    }
                    for item in descriptors
                ],
                "licensing_status": payload["licensing_status"],
                "operator_id": operator_id,
                "request_id": request_id,
                "source_classification": payload["source_classification"],
                "trust_classification": payload["trust_classification"],
            }
        )
        return IntakeValidationReceipt(
            request_id=request_id,
            correlation_id=correlation_id,
            operator_id=operator_id,
            descriptors=descriptors,
            request_sha256=canonical_sha256(canonical),
        )
