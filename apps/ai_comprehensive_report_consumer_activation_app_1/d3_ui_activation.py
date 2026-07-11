"""D3 deterministic UI consumer activation.

The adapter exposes registered comprehensive-report binding data to a
read-only UI surface. It never invokes models, executes prompts, routes
automatically, approves decisions, or writes archive artifacts.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass

from .d1_activation_contract import PHASE_ID, SOURCE_BINDING_PACKAGE

UI_CONSUMER_ID = "ai_comprehensive_report_ui_consumer"
UI_DISPLAY_STATE = "READ_ONLY_REVIEW_REQUIRED"
UI_RENDER_MODE = "READ_ONLY"

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

_FORBIDDEN_TRUE_FIELDS = (
    "automatic_approval_allowed",
    "automatic_archive_allowed",
    "archive_write_allowed",
    "runtime_model_invocation_allowed",
    "prompt_execution_allowed",
    "automatic_routing_allowed",
    "real_execution_allowed",
)


@dataclass(frozen=True)
class UiActivationPacket:
    """Immutable packet exposed to the production UI entry point."""

    phase_id: str
    consumer_id: str
    surface: str
    source_binding_package: str
    source_artifact_id: str
    source_artifact_type: str
    source_artifact_digest: str
    correlation_id: str
    evidence_ids: tuple[str, ...]
    risk_flags: tuple[str, ...]
    source_payload_keys: tuple[str, ...]
    display_state: str = UI_DISPLAY_STATE
    render_mode: str = UI_RENDER_MODE
    registered_artifact: bool = True
    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    deterministic_only: bool = True
    operator_review_required: bool = True
    manual_archive_authorization_required: bool = True
    action_controls_enabled: bool = False
    archive_controls_enabled: bool = False
    automatic_refresh_enabled: bool = False
    automatic_approval_allowed: bool = False
    automatic_archive_allowed: bool = False
    archive_write_allowed: bool = False
    runtime_model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    automatic_routing_allowed: bool = False
    real_execution_allowed: bool = False
    source_payload_mutated: bool = False

    def validate(self) -> tuple[str, ...]:
        """Return deterministic packet validation errors."""

        errors: list[str] = []

        expected_values = {
            "phase_id": (self.phase_id, PHASE_ID),
            "consumer_id": (self.consumer_id, UI_CONSUMER_ID),
            "surface": (self.surface, "ui"),
            "source_binding_package": (
                self.source_binding_package,
                SOURCE_BINDING_PACKAGE,
            ),
            "display_state": (
                self.display_state,
                UI_DISPLAY_STATE,
            ),
            "render_mode": (
                self.render_mode,
                UI_RENDER_MODE,
            ),
        }

        for name, values in expected_values.items():
            actual, expected = values

            if actual != expected:
                errors.append(f"{name}_mismatch")

        required_text = {
            "source_artifact_id": self.source_artifact_id,
            "source_artifact_type": self.source_artifact_type,
            "correlation_id": self.correlation_id,
        }

        for name, value in required_text.items():
            if not value:
                errors.append(f"{name}_required")

        if not _SHA256_PATTERN.fullmatch(
            self.source_artifact_digest
        ):
            errors.append("source_artifact_digest_invalid")

        required_true = {
            "registered_artifact": self.registered_artifact,
            "paper_only": self.paper_only,
            "local_only": self.local_only,
            "read_only": self.read_only,
            "sidecar_only": self.sidecar_only,
            "deterministic_only": self.deterministic_only,
            "operator_review_required":
                self.operator_review_required,
            "manual_archive_authorization_required":
                self.manual_archive_authorization_required,
        }

        for name, value in required_true.items():
            if value is not True:
                errors.append(f"{name}_must_be_true")

        required_false = {
            "action_controls_enabled":
                self.action_controls_enabled,
            "archive_controls_enabled":
                self.archive_controls_enabled,
            "automatic_refresh_enabled":
                self.automatic_refresh_enabled,
            "automatic_approval_allowed":
                self.automatic_approval_allowed,
            "automatic_archive_allowed":
                self.automatic_archive_allowed,
            "archive_write_allowed":
                self.archive_write_allowed,
            "runtime_model_invocation_allowed":
                self.runtime_model_invocation_allowed,
            "prompt_execution_allowed":
                self.prompt_execution_allowed,
            "automatic_routing_allowed":
                self.automatic_routing_allowed,
            "real_execution_allowed":
                self.real_execution_allowed,
            "source_payload_mutated":
                self.source_payload_mutated,
        }

        for name, value in required_false.items():
            if value is not False:
                errors.append(f"{name}_must_be_false")

        return tuple(sorted(set(errors)))

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic serializable representation."""

        result = asdict(self)
        result["validation_errors"] = list(self.validate())
        result["valid"] = not self.validate()
        return result


def _require_text(
    payload: Mapping[str, object],
    field_name: str,
) -> str:
    value = payload.get(field_name)

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")

    return value.strip()


def _require_true(
    payload: Mapping[str, object],
    field_name: str,
) -> None:
    if payload.get(field_name) is not True:
        raise ValueError(f"{field_name} must be true")


def _normalize_text_sequence(
    value: object,
    field_name: str,
) -> tuple[str, ...]:
    if value is None:
        return ()

    if isinstance(value, str) or not isinstance(value, Sequence):
        raise ValueError(
            f"{field_name} must be a sequence of strings"
        )

    normalized: list[str] = []

    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                f"{field_name} must contain non-empty strings"
            )

        normalized.append(item.strip())

    return tuple(sorted(set(normalized)))


def build_ui_activation_packet(
    binding_payload: Mapping[str, object],
) -> UiActivationPacket:
    """Build a read-only UI packet without mutating its source."""

    if not isinstance(binding_payload, Mapping):
        raise TypeError("binding_payload must be a mapping")

    source_binding_package = _require_text(
        binding_payload,
        "source_binding_package",
    )

    if source_binding_package != SOURCE_BINDING_PACKAGE:
        raise ValueError("source_binding_package mismatch")

    _require_true(binding_payload, "registered_artifact")
    _require_true(binding_payload, "operator_review_required")
    _require_true(
        binding_payload,
        "manual_archive_authorization_required",
    )

    for field_name in _FORBIDDEN_TRUE_FIELDS:
        if binding_payload.get(field_name, False) is not False:
            raise ValueError(f"{field_name} must be false")

    artifact_digest = _require_text(
        binding_payload,
        "artifact_digest",
    ).lower()

    if not _SHA256_PATTERN.fullmatch(artifact_digest):
        raise ValueError(
            "artifact_digest must be a lowercase SHA-256 value"
        )

    packet = UiActivationPacket(
        phase_id=PHASE_ID,
        consumer_id=UI_CONSUMER_ID,
        surface="ui",
        source_binding_package=source_binding_package,
        source_artifact_id=_require_text(
            binding_payload,
            "artifact_id",
        ),
        source_artifact_type=_require_text(
            binding_payload,
            "artifact_type",
        ),
        source_artifact_digest=artifact_digest,
        correlation_id=_require_text(
            binding_payload,
            "correlation_id",
        ),
        evidence_ids=_normalize_text_sequence(
            binding_payload.get("evidence_ids"),
            "evidence_ids",
        ),
        risk_flags=_normalize_text_sequence(
            binding_payload.get("risk_flags"),
            "risk_flags",
        ),
        source_payload_keys=tuple(
            sorted(str(key) for key in binding_payload)
        ),
    )

    errors = packet.validate()

    if errors:
        raise ValueError(
            "Invalid UI activation packet: "
            + ", ".join(errors)
        )

    return packet


def validate_ui_activation_packet(
    packet: UiActivationPacket,
) -> tuple[str, ...]:
    """Validate a UI packet without mutation or side effects."""

    if not isinstance(packet, UiActivationPacket):
        return ("ui_activation_packet_required",)

    return packet.validate()
