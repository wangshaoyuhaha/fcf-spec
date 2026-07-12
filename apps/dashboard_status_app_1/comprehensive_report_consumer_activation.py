"""Production UI entry point for comprehensive-report consumption."""

from __future__ import annotations

from collections.abc import Mapping

from apps import ai_comprehensive_report_consumer_binding_app_1
from apps.ai_comprehensive_report_consumer_activation_app_1 import (
    SOURCE_BINDING_PACKAGE,
    UiActivationPacket,
    build_ui_activation_packet,
    validate_ui_activation_packet,
)

ENTRY_POINT_ID = "ui.comprehensive_report_consumer_activation"
BOUND_BINDING_PACKAGE = (
    ai_comprehensive_report_consumer_binding_app_1.__name__
)


def activate_comprehensive_report_for_ui(
    binding_payload: Mapping[str, object],
) -> UiActivationPacket:
    """Expose a registered report to the read-only UI surface."""

    if BOUND_BINDING_PACKAGE != SOURCE_BINDING_PACKAGE:
        raise RuntimeError(
            "Consumer binding package identity mismatch"
        )

    packet = build_ui_activation_packet(binding_payload)
    errors = validate_ui_activation_packet(packet)

    if errors:
        raise ValueError(
            "UI activation rejected: " + ", ".join(errors)
        )

    return packet
