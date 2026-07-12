"""D6 deterministic full-chain consumer activation closeout.

The closeout verifies the production activation chain across Operator
Review, UI, and Report Archive. It remains paper-only, local-only,
read-only, deterministic, and operator-controlled.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass

from apps.dashboard_status_app_1.comprehensive_report_consumer_activation import (
    activate_comprehensive_report_for_ui,
)
from operator_review_app.comprehensive_report_consumer_activation import (
    activate_comprehensive_report_for_operator_review,
)
from report_archive_app.comprehensive_report_consumer_activation import (
    activate_comprehensive_report_for_report_archive,
)

from .d1_activation_contract import PHASE_ID, SOURCE_BINDING_PACKAGE
from .d5_cross_surface_activation_validation import (
    CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE,
    CROSS_SURFACE_VALIDATION_STATUS,
    RegisteredCrossSurfaceActivationArtifact,
    build_registered_cross_surface_activation_artifact,
)

FULL_CHAIN_CLOSEOUT_ARTIFACT_TYPE = (
    "ai_comprehensive_report_consumer_activation_closeout"
)
FULL_CHAIN_CLOSEOUT_STATUS = (
    "COMPLETE_OPERATOR_REVIEW_AND_MANUAL_ARCHIVE_REQUIRED"
)

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _canonical_digest(payload: dict[str, object]) -> str:
    serialized = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")

    return hashlib.sha256(serialized).hexdigest()


@dataclass(frozen=True)
class FullChainActivationCloseoutReceipt:
    """Immutable final closeout receipt for the activation phase."""

    phase_id: str
    artifact_type: str
    artifact_id: str
    closeout_digest: str
    status: str
    source_binding_package: str
    source_artifact_id: str
    source_artifact_type: str
    source_artifact_digest: str
    correlation_id: str
    cross_surface_artifact_id: str
    cross_surface_validation_digest: str
    cross_surface_status: str
    activated_surfaces: tuple[str, ...]
    production_entry_points: tuple[str, ...]
    gap_1_external_production_consumption_closed: bool
    gap_2_operator_review_activation_closed: bool
    gap_3_ui_activation_closed: bool
    gap_4_report_archive_activation_closed: bool
    gap_5_full_bundle_lifecycle_activation_closed: bool
    registered_artifact: bool = True
    paper_only: bool = True
    local_only: bool = True
    read_only: bool = True
    sidecar_only: bool = True
    deterministic_only: bool = True
    operator_review_required: bool = True
    manual_archive_authorization_required: bool = True
    automatic_approval_allowed: bool = False
    automatic_archive_allowed: bool = False
    archive_write_allowed: bool = False
    runtime_model_invocation_allowed: bool = False
    prompt_execution_allowed: bool = False
    automatic_routing_allowed: bool = False
    real_execution_allowed: bool = False
    archive_payload_written: bool = False
    source_payload_mutated: bool = False

    def digest_payload(self) -> dict[str, object]:
        """Return the canonical closeout digest payload."""

        return {
            "phase_id": self.phase_id,
            "artifact_type": self.artifact_type,
            "status": self.status,
            "source_binding_package":
                self.source_binding_package,
            "source_artifact_id": self.source_artifact_id,
            "source_artifact_type":
                self.source_artifact_type,
            "source_artifact_digest":
                self.source_artifact_digest,
            "correlation_id": self.correlation_id,
            "cross_surface_artifact_id":
                self.cross_surface_artifact_id,
            "cross_surface_validation_digest":
                self.cross_surface_validation_digest,
            "cross_surface_status": self.cross_surface_status,
            "activated_surfaces":
                list(self.activated_surfaces),
            "production_entry_points":
                list(self.production_entry_points),
            "gap_states": {
                "gap_1":
                    self.gap_1_external_production_consumption_closed,
                "gap_2":
                    self.gap_2_operator_review_activation_closed,
                "gap_3":
                    self.gap_3_ui_activation_closed,
                "gap_4":
                    self.gap_4_report_archive_activation_closed,
                "gap_5":
                    self.gap_5_full_bundle_lifecycle_activation_closed,
            },
        }

    def expected_closeout_digest(self) -> str:
        """Return the expected deterministic closeout digest."""

        return _canonical_digest(self.digest_payload())

    def validate(self) -> tuple[str, ...]:
        """Return deterministic closeout validation errors."""

        errors: list[str] = []

        expected_values = {
            "phase_id": (self.phase_id, PHASE_ID),
            "artifact_type": (
                self.artifact_type,
                FULL_CHAIN_CLOSEOUT_ARTIFACT_TYPE,
            ),
            "status": (
                self.status,
                FULL_CHAIN_CLOSEOUT_STATUS,
            ),
            "source_binding_package": (
                self.source_binding_package,
                SOURCE_BINDING_PACKAGE,
            ),
            "cross_surface_status": (
                self.cross_surface_status,
                CROSS_SURFACE_VALIDATION_STATUS,
            ),
            "activated_surfaces": (
                self.activated_surfaces,
                (
                    "operator_review",
                    "ui",
                    "report_archive",
                ),
            ),
            "production_entry_points": (
                self.production_entry_points,
                (
                    "operator_review_app."
                    "comprehensive_report_consumer_activation",
                    "apps.dashboard_status_app_1."
                    "comprehensive_report_consumer_activation",
                    "report_archive_app."
                    "comprehensive_report_consumer_activation",
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
            "cross_surface_artifact_id":
                self.cross_surface_artifact_id,
        }

        for field_name, value in required_text.items():
            if not value:
                errors.append(f"{field_name}_required")

        digest_fields = {
            "closeout_digest": self.closeout_digest,
            "source_artifact_digest":
                self.source_artifact_digest,
            "cross_surface_validation_digest":
                self.cross_surface_validation_digest,
        }

        for field_name, value in digest_fields.items():
            if not _SHA256_PATTERN.fullmatch(value):
                errors.append(f"{field_name}_invalid")

        expected_digest = self.expected_closeout_digest()

        if self.closeout_digest != expected_digest:
            errors.append("closeout_digest_mismatch")

        expected_artifact_id = (
            f"{FULL_CHAIN_CLOSEOUT_ARTIFACT_TYPE}:"
            f"{self.source_artifact_id}:"
            f"{expected_digest[:16]}"
        )

        if self.artifact_id != expected_artifact_id:
            errors.append("artifact_id_mismatch")

        required_true = {
            "gap_1_external_production_consumption_closed":
                self.gap_1_external_production_consumption_closed,
            "gap_2_operator_review_activation_closed":
                self.gap_2_operator_review_activation_closed,
            "gap_3_ui_activation_closed":
                self.gap_3_ui_activation_closed,
            "gap_4_report_archive_activation_closed":
                self.gap_4_report_archive_activation_closed,
            "gap_5_full_bundle_lifecycle_activation_closed":
                self.gap_5_full_bundle_lifecycle_activation_closed,
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

        for field_name, value in required_true.items():
            if value is not True:
                errors.append(f"{field_name}_must_be_true")

        required_false = {
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
            "archive_payload_written":
                self.archive_payload_written,
            "source_payload_mutated":
                self.source_payload_mutated,
        }

        for field_name, value in required_false.items():
            if value is not False:
                errors.append(f"{field_name}_must_be_false")

        return tuple(sorted(set(errors)))

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic serializable representation."""

        result = asdict(self)
        errors = self.validate()
        result["validation_errors"] = list(errors)
        result["valid"] = not errors
        return result


def _build_receipt_from_artifact(
    artifact: RegisteredCrossSurfaceActivationArtifact,
) -> FullChainActivationCloseoutReceipt:
    payload = {
        "phase_id": PHASE_ID,
        "artifact_type": FULL_CHAIN_CLOSEOUT_ARTIFACT_TYPE,
        "status": FULL_CHAIN_CLOSEOUT_STATUS,
        "source_binding_package":
            artifact.source_binding_package,
        "source_artifact_id": artifact.source_artifact_id,
        "source_artifact_type":
            artifact.source_artifact_type,
        "source_artifact_digest":
            artifact.source_artifact_digest,
        "correlation_id": artifact.correlation_id,
        "cross_surface_artifact_id": artifact.artifact_id,
        "cross_surface_validation_digest":
            artifact.validation_digest,
        "cross_surface_status": artifact.status,
        "activated_surfaces": list(artifact.surfaces),
        "production_entry_points": [
            "operator_review_app."
            "comprehensive_report_consumer_activation",
            "apps.dashboard_status_app_1."
            "comprehensive_report_consumer_activation",
            "report_archive_app."
            "comprehensive_report_consumer_activation",
        ],
        "gap_states": {
            "gap_1": True,
            "gap_2": True,
            "gap_3": True,
            "gap_4": True,
            "gap_5": True,
        },
    }
    closeout_digest = _canonical_digest(payload)

    return FullChainActivationCloseoutReceipt(
        phase_id=PHASE_ID,
        artifact_type=FULL_CHAIN_CLOSEOUT_ARTIFACT_TYPE,
        artifact_id=(
            f"{FULL_CHAIN_CLOSEOUT_ARTIFACT_TYPE}:"
            f"{artifact.source_artifact_id}:"
            f"{closeout_digest[:16]}"
        ),
        closeout_digest=closeout_digest,
        status=FULL_CHAIN_CLOSEOUT_STATUS,
        source_binding_package=
            artifact.source_binding_package,
        source_artifact_id=artifact.source_artifact_id,
        source_artifact_type=
            artifact.source_artifact_type,
        source_artifact_digest=
            artifact.source_artifact_digest,
        correlation_id=artifact.correlation_id,
        cross_surface_artifact_id=artifact.artifact_id,
        cross_surface_validation_digest=
            artifact.validation_digest,
        cross_surface_status=artifact.status,
        activated_surfaces=artifact.surfaces,
        production_entry_points=(
            "operator_review_app."
            "comprehensive_report_consumer_activation",
            "apps.dashboard_status_app_1."
            "comprehensive_report_consumer_activation",
            "report_archive_app."
            "comprehensive_report_consumer_activation",
        ),
        gap_1_external_production_consumption_closed=True,
        gap_2_operator_review_activation_closed=True,
        gap_3_ui_activation_closed=True,
        gap_4_report_archive_activation_closed=True,
        gap_5_full_bundle_lifecycle_activation_closed=True,
    )


def build_full_chain_activation_closeout_receipt(
    binding_payload: Mapping[str, object],
) -> FullChainActivationCloseoutReceipt:
    """Run the deterministic production activation chain."""

    operator_packet = (
        activate_comprehensive_report_for_operator_review(
            binding_payload
        )
    )
    ui_packet = activate_comprehensive_report_for_ui(
        binding_payload
    )
    archive_packet = (
        activate_comprehensive_report_for_report_archive(
            binding_payload
        )
    )
    validation_artifact = (
        build_registered_cross_surface_activation_artifact(
            operator_packet,
            ui_packet,
            archive_packet,
        )
    )

    if (
        validation_artifact.artifact_type
        != CROSS_SURFACE_VALIDATION_ARTIFACT_TYPE
    ):
        raise ValueError(
            "cross_surface_validation_artifact_type_mismatch"
        )

    receipt = _build_receipt_from_artifact(
        validation_artifact
    )
    errors = receipt.validate()

    if errors:
        raise ValueError(
            "Invalid full-chain closeout receipt: "
            + ", ".join(errors)
        )

    return receipt


def validate_full_chain_activation_closeout_receipt(
    receipt: FullChainActivationCloseoutReceipt,
) -> tuple[str, ...]:
    """Validate a closeout receipt without side effects."""

    if not isinstance(
        receipt,
        FullChainActivationCloseoutReceipt,
    ):
        return (
            "full_chain_activation_closeout_receipt_required",
        )

    return receipt.validate()
