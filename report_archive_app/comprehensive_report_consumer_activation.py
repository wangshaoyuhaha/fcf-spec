"""Production Report Archive entry point for report consumption."""

from __future__ import annotations

from collections.abc import Mapping

from apps import ai_comprehensive_report_consumer_binding_app_1
from apps.ai_comprehensive_report_consumer_activation_app_1 import (
    SOURCE_BINDING_PACKAGE,
    ReportArchiveActivationPacket,
    build_report_archive_activation_packet,
    validate_report_archive_activation_packet,
)

ENTRY_POINT_ID = (
    "report_archive.comprehensive_report_consumer_activation"
)
BOUND_BINDING_PACKAGE = (
    ai_comprehensive_report_consumer_binding_app_1.__name__
)


def activate_comprehensive_report_for_report_archive(
    binding_payload: Mapping[str, object],
) -> ReportArchiveActivationPacket:
    """Prepare a registered report for manual archive review only."""

    if BOUND_BINDING_PACKAGE != SOURCE_BINDING_PACKAGE:
        raise RuntimeError(
            "Consumer binding package identity mismatch"
        )

    packet = build_report_archive_activation_packet(
        binding_payload
    )
    errors = validate_report_archive_activation_packet(packet)

    if errors:
        raise ValueError(
            "Report Archive activation rejected: "
            + ", ".join(errors)
        )

    return packet
