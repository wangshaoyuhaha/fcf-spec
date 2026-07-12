"""D5 registered cross-surface activation validation.

The validation artifact proves that Operator Review, UI, and Report
Archive consume the same registered comprehensive-report binding.

The module is deterministic and read-only. It does not write archives,
approve artifacts, invoke models, execute prompts, route automatically,
or perform real execution.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import asdict, dataclass

from .d1_activation_contract import PHASE_ID, SOURCE_BINDING_PACKAGE
from .d2_operator_review_activation import (
    OPERATOR_REVIEW_CONSUMER_ID,
    OPERATOR_REVIEW_STATUS,
    OperatorReviewActivationPacket,
)
from .d3_ui_activation import (
    UI_CONSUMER_ID,
    UI_DISPLAY_STATE,
    UiActivationPacket,
)
from .d4_report_archive_activation import (
    REPORT_ARCHIVE_CONSUMER_ID,
    REPORT_ARCHIVE_STATUS,
    ReportArchiveActivationPacket,
)

CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE = (
    "ai_comprehensive_report_cross_surface_activation_validation"
)
CROSS_SURFACE_VALIDATION_STATUS = (
    "VALIDATED_OPERATOR_REVIEW_REQUIRED"
)

CROSS_SURFACE_ORDER = (
    "operator_review",
    "ui",
    "report_archive",
)

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")

_REQUIRED_TRUE_FIELDS = (
    "registered_artifact",
    "paper_only",
    "local_only",
    "read_only",
    "sidecar_only",
    "deterministic_only",
    "operator_review_required",
    "manual_archive_authorization_required",
)

_REQUIRED_FALSE_FIELDS = (
    "automatic_approval_allowed",
    "automatic_archive_allowed",
    "archive_write_allowed",
    "runtime_model_invocation_allowed",
    "prompt_execution_allowed",
    "automatic_routing_allowed",
    "real_execution_allowed",
    "source_payload_mutated",
)


def _canonical_digest(payload: dict[str, object]) -> str:
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")

    return hashlib.sha256(serialized).hexdigest()


def _digest_payload(
    *,
    source_artifact_id: str,
    source_artifact_type: str,
    source_artifact_digest: str,
    correlation_id: str,
    evidence_ids: tuple[str, ...],
    risk_flags: tuple[str, ...],
    surface_consumer_ids: tuple[str, ...],
    surface_states: tuple[str, ...],
) -> dict[str, object]:
    return {
        "phase_id": PHASE_ID,
        "artifact_type":
            CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE,
        "source_binding_package": SOURCE_BINDING_PACKAGE,
        "source_artifact_id": source_artifact_id,
        "source_artifact_type": source_artifact_type,
        "source_artifact_digest": source_artifact_digest,
        "correlation_id": correlation_id,
        "evidence_ids": list(evidence_ids),
        "risk_flags": list(risk_flags),
        "surfaces": list(CROSS_SURFACE_ORDER),
        "surface_consumer_ids": list(surface_consumer_ids),
        "surface_states": list(surface_states),
    }


@dataclass(frozen=True)
class RegisteredCrossSurfaceActivationArtifact:
    """Immutable registered cross-surface validation artifact."""

    phase_id: str
    artifact_type: str
    artifact_id: str
    validation_digest: str
    status: str
    source_binding_package: str
    source_artifact_id: str
    source_artifact_type: str
    source_artifact_digest: str
    correlation_id: str
    evidence_ids: tuple[str, ...]
    risk_flags: tuple[str, ...]
    surfaces: tuple[str, ...]
    surface_consumer_ids: tuple[str, ...]
    surface_states: tuple[str, ...]
    registered_artifact: bool = True
    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    deterministic_only: bool = True
    operator_review_required: bool = True
    manual_archive_authorization_required: bool = True
    archive_payload_written: bool = False
    automatic_approval_allowed: bool = False
    automatic_archive_allowed: bool = False
    archive_write_allowed: bool = False
    runtime_model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    automatic_routing_allowed: bool = False
    real_execution_allowed: bool = False
    source_payload_mutated: bool = False

    def expected_validation_digest(self) -> str:
        """Return the deterministic expected validation digest."""

        return _canonical_digest(
            _digest_payload(
                source_artifact_id=self.source_artifact_id,
                source_artifact_type=self.source_artifact_type,
                source_artifact_digest=(
                    self.source_artifact_digest
                ),
                correlation_id=self.correlation_id,
                evidence_ids=self.evidence_ids,
                risk_flags=self.risk_flags,
                surface_consumer_ids=(
                    self.surface_consumer_ids
                ),
                surface_states=self.surface_states,
            )
        )

    def validate(self) -> tuple[str, ...]:
        """Return deterministic artifact validation errors."""

        errors: list[str] = []

        expected_values = {
            "phase_id": (self.phase_id, PHASE_ID),
            "artifact_type": (
                self.artifact_type,
                CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE,
            ),
            "status": (
                self.status,
                CROSS_SURFACE_VALIDATION_STATUS,
            ),
            "source_binding_package": (
                self.source_binding_package,
                SOURCE_BINDING_PACKAGE,
            ),
            "surfaces": (
                self.surfaces,
                CROSS_SURFACE_ORDER,
            ),
            "surface_consumer_ids": (
                self.surface_consumer_ids,
                (
                    OPERATOR_REVIEW_CONSUMER_ID,
                    UI_CONSUMER_ID,
                    REPORT_ARCHIVE_CONSUMER_ID,
                ),
            ),
            "surface_states": (
                self.surface_states,
                (
                    OPERATOR_REVIEW_STATUS,
                    UI_DISPLAY_STATE,
                    REPORT_ARCHIVE_STATUS,
                ),
            ),
        }

        for field_name, values in expected_values.items():
            actual, expected = values

            if actual != expected:
                errors.append(f"{field_name}_mismatch")

        required_text = {
            "artifact_id": self.artifact_id,
            "source_artifact_id": self.source_artifact_id,
            "source_artifact_type":
                self.source_artifact_type,
            "correlation_id": self.correlation_id,
        }

        for field_name, value in required_text.items():
            if not value:
                errors.append(f"{field_name}_required")

        if not _SHA256_PATTERN.fullmatch(
            self.source_artifact_digest
        ):
            errors.append("source_artifact_digest_invalid")

        if not _SHA256_PATTERN.fullmatch(
            self.validation_digest
        ):
            errors.append("validation_digest_invalid")

        expected_digest = self.expected_validation_digest()

        if self.validation_digest != expected_digest:
            errors.append("validation_digest_mismatch")

        expected_artifact_id = (
            f"{CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE}:"
            f"{self.source_artifact_id}:"
            f"{expected_digest[:16]}"
        )

        if self.artifact_id != expected_artifact_id:
            errors.append("artifact_id_mismatch")

        for field_name in _REQUIRED_TRUE_FIELDS:
            if getattr(self, field_name) is not True:
                errors.append(f"{field_name}_must_be_true")

        for field_name in _REQUIRED_FALSE_FIELDS:
            if getattr(self, field_name) is not False:
                errors.append(f"{field_name}_must_be_false")

        if self.archive_payload_written is not False:
            errors.append("archive_payload_written_must_be_false")

        return tuple(sorted(set(errors)))

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic serializable representation."""

        result = asdict(self)
        errors = self.validate()
        result["validation_errors"] = list(errors)
        result["valid"] = not errors
        return result


def _validate_source_packet(
    packet: object,
    expected_type: type[object],
    surface_name: str,
) -> None:
    if not isinstance(packet, expected_type):
        raise TypeError(
            f"{surface_name} packet has invalid type"
        )

    errors = packet.validate()

    if errors:
        raise ValueError(
            f"{surface_name} packet invalid: "
            + ", ".join(errors)
        )

    for field_name in _REQUIRED_TRUE_FIELDS:
        if getattr(packet, field_name) is not True:
            raise ValueError(
                f"{surface_name} {field_name} must be true"
            )

    for field_name in _REQUIRED_FALSE_FIELDS:
        if getattr(packet, field_name) is not False:
            raise ValueError(
                f"{surface_name} {field_name} must be false"
            )


def _require_equal(
    field_name: str,
    operator_value: object,
    ui_value: object,
    archive_value: object,
) -> object:
    if not (
        operator_value == ui_value == archive_value
    ):
        raise ValueError(
            f"cross_surface_{field_name}_mismatch"
        )

    return operator_value


def build_registered_cross_surface_activation_artifact(
    operator_packet: OperatorReviewActivationPacket,
    ui_packet: UiActivationPacket,
    archive_packet: ReportArchiveActivationPacket,
) -> RegisteredCrossSurfaceActivationArtifact:
    """Validate three surfaces and build a registered artifact."""

    _validate_source_packet(
        operator_packet,
        OperatorReviewActivationPacket,
        "operator_review",
    )
    _validate_source_packet(
        ui_packet,
        UiActivationPacket,
        "ui",
    )
    _validate_source_packet(
        archive_packet,
        ReportArchiveActivationPacket,
        "report_archive",
    )

    source_binding_package = _require_equal(
        "source_binding_package",
        operator_packet.source_binding_package,
        ui_packet.source_binding_package,
        archive_packet.source_binding_package,
    )

    if source_binding_package != SOURCE_BINDING_PACKAGE:
        raise ValueError(
            "cross_surface_source_binding_package_mismatch"
        )

    source_artifact_id = _require_equal(
        "source_artifact_id",
        operator_packet.source_artifact_id,
        ui_packet.source_artifact_id,
        archive_packet.source_artifact_id,
    )
    source_artifact_type = _require_equal(
        "source_artifact_type",
        operator_packet.source_artifact_type,
        ui_packet.source_artifact_type,
        archive_packet.source_artifact_type,
    )
    source_artifact_digest = _require_equal(
        "source_artifact_digest",
        operator_packet.source_artifact_digest,
        ui_packet.source_artifact_digest,
        archive_packet.source_artifact_digest,
    )
    correlation_id = _require_equal(
        "correlation_id",
        operator_packet.correlation_id,
        ui_packet.correlation_id,
        archive_packet.correlation_id,
    )
    evidence_ids = _require_equal(
        "evidence_ids",
        operator_packet.evidence_ids,
        ui_packet.evidence_ids,
        archive_packet.evidence_ids,
    )
    _require_equal(
        "source_payload_keys",
        operator_packet.source_payload_keys,
        ui_packet.source_payload_keys,
        archive_packet.source_payload_keys,
    )

    if ui_packet.risk_flags != archive_packet.risk_flags:
        raise ValueError("cross_surface_risk_flags_mismatch")

    surface_consumer_ids = (
        operator_packet.consumer_id,
        ui_packet.consumer_id,
        archive_packet.consumer_id,
    )
    surface_states = (
        operator_packet.review_status,
        ui_packet.display_state,
        archive_packet.archive_status,
    )

    digest_payload = _digest_payload(
        source_artifact_id=str(source_artifact_id),
        source_artifact_type=str(source_artifact_type),
        source_artifact_digest=str(
            source_artifact_digest
        ),
        correlation_id=str(correlation_id),
        evidence_ids=tuple(evidence_ids),
        risk_flags=ui_packet.risk_flags,
        surface_consumer_ids=surface_consumer_ids,
        surface_states=surface_states,
    )
    validation_digest = _canonical_digest(digest_payload)

    artifact = RegisteredCrossSurfaceActivationArtifact(
        phase_id=PHASE_ID,
        artifact_type=(
            CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE
        ),
        artifact_id=(
            f"{CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE}:"
            f"{source_artifact_id}:"
            f"{validation_digest[:16]}"
        ),
        validation_digest=validation_digest,
        status=CROSS_SURFACE_VALIDATION_STATUS,
        source_binding_package=str(
            source_binding_package
        ),
        source_artifact_id=str(source_artifact_id),
        source_artifact_type=str(source_artifact_type),
        source_artifact_digest=str(
            source_artifact_digest
        ),
        correlation_id=str(correlation_id),
        evidence_ids=tuple(evidence_ids),
        risk_flags=ui_packet.risk_flags,
        surfaces=CROSS_SURFACE_ORDER,
        surface_consumer_ids=surface_consumer_ids,
        surface_states=surface_states,
    )

    errors = artifact.validate()

    if errors:
        raise ValueError(
            "Invalid registered cross-surface artifact: "
            + ", ".join(errors)
        )

    return artifact


def validate_registered_cross_surface_activation_artifact(
    artifact: RegisteredCrossSurfaceActivationArtifact,
) -> tuple[str, ...]:
    """Validate a registered artifact without side effects."""

    if not isinstance(
        artifact,
        RegisteredCrossSurfaceActivationArtifact,
    ):
        return (
            "registered_cross_surface_activation_artifact_required",
        )

    return artifact.validate()
