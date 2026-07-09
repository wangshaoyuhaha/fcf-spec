"""Sidecar-only validator for protected risk metadata visibility.

This module does not mutate core.
This module does not create execution logic.
"""

from __future__ import annotations

from typing import Any


PROTECTED_FIELDS = (
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

ABNORMAL_EVIDENCE_CHAIN_STATUS = {
    'stale',
    'incomplete',
    'missing',
    'unresolved',
}


def _has_value(packet: dict[str, Any], field: str) -> bool:
    if field not in packet:
        return False
    value = packet[field]
    if value is None:
        return False
    if value == '':
        return False
    if isinstance(value, (list, tuple, set, dict)) and len(value) == 0:
        return False
    return True


def _requires_operator_review(packet: dict[str, Any]) -> bool:
    flags = set(packet.get('risk_flags') or [])
    status = packet.get('review_status')
    evidence_status = packet.get('evidence_chain_status')

    if status == 'REVIEW_REQUIRED':
        return True
    if 'REVIEW_REQUIRED' in flags:
        return True
    if packet.get('circuit_break') is True or 'CIRCUIT_BREAK' in flags:
        return True
    if _has_value(packet, 'conflict_signals'):
        return True
    if _has_value(packet, 'missing_required_fields'):
        return True
    if _has_value(packet, 'unsafe_permissions'):
        return True
    if evidence_status in ABNORMAL_EVIDENCE_CHAIN_STATUS:
        return True
    return False


def validate_visibility_preservation(
    source_packet: dict[str, Any], rendered_packet: dict[str, Any]
) -> list[str]:
    errors: list[str] = []

    for field in PROTECTED_FIELDS:
        if _has_value(source_packet, field) and not _has_value(rendered_packet, field):
            errors.append(f'missing protected field: {field}')

    if source_packet.get('review_status') == 'REVIEW_REQUIRED' and rendered_packet.get('review_status') != 'REVIEW_REQUIRED':
        errors.append('REVIEW_REQUIRED downgraded')

    if source_packet.get('circuit_break') is True and rendered_packet.get('circuit_break') is not True:
        errors.append('CIRCUIT_BREAK downgraded')

    if _requires_operator_review(source_packet) and rendered_packet.get('operator_review_required') is not True:
        errors.append('operator review requirement missing')

    source_reason_codes = set(source_packet.get('reason_codes') or [])
    rendered_reason_codes = set(rendered_packet.get('reason_codes') or [])
    missing_reason_codes = sorted(source_reason_codes - rendered_reason_codes)
    if missing_reason_codes:
        errors.append('reason_codes removed: ' + ','.join(missing_reason_codes))

    source_risk_flags = set(source_packet.get('risk_flags') or [])
    rendered_risk_flags = set(rendered_packet.get('risk_flags') or [])
    missing_risk_flags = sorted(source_risk_flags - rendered_risk_flags)
    if missing_risk_flags:
        errors.append('risk_flags removed: ' + ','.join(missing_risk_flags))

    return errors

