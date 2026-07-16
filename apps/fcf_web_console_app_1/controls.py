from __future__ import annotations

from types import MappingProxyType
from typing import Any, Mapping

from .contracts import (
    ConsoleAction,
    ConsoleActionReceipt,
    canonical_sha256,
    require_text,
)


class GovernedConsoleActionService:
    def __init__(self, registered_operator_ids: tuple[str, ...] = ()) -> None:
        self._registered_operator_ids = frozenset(
            require_text(value, "registered_operator_id")
            for value in registered_operator_ids
        )

    def validate(
        self,
        payload: Mapping[str, Any],
        peer_host: str,
    ) -> ConsoleActionReceipt:
        if peer_host != "127.0.0.1":
            raise ValueError("console action peer must be exactly 127.0.0.1")
        if not isinstance(payload, Mapping):
            raise ValueError("console action payload must be an object")
        if payload.get("confirmed") is not True:
            raise ValueError("explicit Operator confirmation is required")
        try:
            action = ConsoleAction(
                require_text(payload.get("action", ""), "action").upper()
            )
        except ValueError as exc:
            raise ValueError("unsupported console action") from exc
        request_id = require_text(payload.get("request_id", ""), "request_id")
        correlation_id = require_text(
            payload.get("correlation_id", ""),
            "correlation_id",
        )
        operator_id = require_text(payload.get("operator_id", ""), "operator_id")
        if operator_id not in self._registered_operator_ids:
            raise ValueError("registered Operator attestation is required")
        target_artifact_id = require_text(
            payload.get("target_artifact_id", ""),
            "target_artifact_id",
        )
        reason = require_text(payload.get("reason", ""), "reason")
        canonical = MappingProxyType(
            {
                "action": action.value,
                "confirmed": True,
                "correlation_id": correlation_id,
                "operator_id": operator_id,
                "reason": reason,
                "request_id": request_id,
                "target_artifact_id": target_artifact_id,
            }
        )
        return ConsoleActionReceipt(
            request_id=request_id,
            correlation_id=correlation_id,
            operator_id=operator_id,
            action=action,
            target_artifact_id=target_artifact_id,
            reason=reason,
            request_sha256=canonical_sha256(canonical),
        )
