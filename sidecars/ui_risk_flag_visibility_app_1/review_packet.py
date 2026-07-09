"""Operator review visibility packet builder for UI risk flag visibility sidecar."""

from __future__ import annotations

from typing import Any

from .visibility_validator import validate_visibility_preservation


PACKET_FIELDS = (
    'candidate_id',
    'risk_flags',
    'reason_codes',
    'review_status',
    'blocked_reasons',
    'conflict_signals',
    'missing_required_fields',
    'unsafe_permissions',
    'operator_review_required',
    'circuit_break',
    'correlation_id',
    'source_artifact',
    'evidence_chain_status',
)


def build_operator_review_visibility_packet(source_packet: dict[str, Any]) -> dict[str, Any]:
    rendered_packet: dict[str, Any] = {}
    for field in PACKET_FIELDS:
        if field in source_packet:
            rendered_packet[field] = source_packet[field]

    errors = validate_visibility_preservation(source_packet, rendered_packet)
    rendered_packet['visibility_errors'] = errors
    rendered_packet['display_blocked'] = bool(errors) or rendered_packet.get('operator_review_required') is True
    return rendered_packet

