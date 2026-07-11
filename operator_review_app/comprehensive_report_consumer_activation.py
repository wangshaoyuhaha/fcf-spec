"""Production Operator Review entry point for report consumption."""

from __future__ import annotations

from collections.abc import Mapping

from apps import ai_comprehensive_report_consumer_binding_app_1
from apps.ai_comprehensive_report_consumer_activation_app_1 import (
    SOURCE_BINDING_PACKAGE,
    OperatorReviewActivationPacket,
    build_operator_review_activation_packet,
    validate_operator_review_activation_packet,
)

ENTRY_POINT_ID = (
    "operator_review.comprehensive_report_consumer_activation"
)
BOUND_BINDING_PACKAGE = (
    ai_comprehensive_report_consumer_binding_app_1.__name__
)


def activate_comprehensive_report_for_operator_review(
    binding_payload: Mapping[str, object],
) -> OperatorReviewActivationPacket:
    """Activate a registered report for human review only."""

    if BOUND_BINDING_PACKAGE != SOURCE_BINDING_PACKAGE:
        raise RuntimeError(
            "Consumer binding package identity mismatch"
        )

    packet = build_operator_review_activation_packet(
        binding_payload
    )
    errors = validate_operator_review_activation_packet(packet)

    if errors:
        raise ValueError(
            "Operator Review activation rejected: "
            + ", ".join(errors)
        )

    return packet
