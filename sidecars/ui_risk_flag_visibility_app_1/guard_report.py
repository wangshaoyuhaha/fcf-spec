"""Visibility guard report builder for UI risk flag visibility sidecar."""

from __future__ import annotations

from typing import Any

from .review_packet import build_operator_review_visibility_packet
from .visibility_validator import validate_visibility_preservation


def build_visibility_guard_report(
    packet_pairs: list[tuple[dict[str, Any], dict[str, Any]]]
) -> dict[str, Any]:
    packet_results: list[dict[str, Any]] = []

    for index, pair in enumerate(packet_pairs):
        source_packet, rendered_packet = pair
        visibility_errors = validate_visibility_preservation(source_packet, rendered_packet)
        review_packet = build_operator_review_visibility_packet(source_packet)
        display_blocked = bool(visibility_errors) or review_packet.get('display_blocked') is True

        packet_results.append(
            {
                'packet_index': index,
                'candidate_id': source_packet.get('candidate_id'),
                'passed': not visibility_errors,
                'operator_review_required': review_packet.get('operator_review_required') is True,
                'display_blocked': display_blocked,
                'visibility_errors': visibility_errors,
            }
        )

    all_errors: list[dict[str, Any]] = []
    for result in packet_results:
        for error in result['visibility_errors']:
            all_errors.append(
                {
                    'packet_index': result['packet_index'],
                    'candidate_id': result['candidate_id'],
                    'error': error,
                }
            )

    return {
        'total_packets': len(packet_results),
        'passed_packets': sum(1 for result in packet_results if result['passed']),
        'failed_packets': sum(1 for result in packet_results if not result['passed']),
        'operator_review_required_packets': sum(
            1 for result in packet_results if result['operator_review_required']
        ),
        'display_blocked_packets': sum(
            1 for result in packet_results if result['display_blocked']
        ),
        'visibility_errors': all_errors,
        'packet_results': packet_results,
    }

