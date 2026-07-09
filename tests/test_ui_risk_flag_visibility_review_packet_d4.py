from sidecars.ui_risk_flag_visibility_app_1 import build_operator_review_visibility_packet


def _source_packet():
    return {
        'candidate_id': 'D4_SAMPLE_PACKET',
        'risk_flags': ['REVIEW_REQUIRED', 'CIRCUIT_BREAK', 'CONFLICT_SIGNAL'],
        'reason_codes': ['MISSING_REQUIRED_FIELD', 'UNSAFE_PERMISSION'],
        'review_status': 'REVIEW_REQUIRED',
        'blocked_reasons': ['missing_required_fields', 'unsafe_permissions'],
        'conflict_signals': ['model_signal_conflict'],
        'missing_required_fields': ['evidence_chain_status'],
        'unsafe_permissions': ['attempted_execution_permission'],
        'operator_review_required': True,
        'circuit_break': True,
        'correlation_id': 'D4-CORRELATION-SAMPLE',
        'source_artifact': 'd4-source-artifact',
        'evidence_chain_status': 'incomplete',
    }


def test_d4_review_packet_preserves_required_risk_metadata():
    source = _source_packet()
    packet = build_operator_review_visibility_packet(source)
    for field in [
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
    ]:
        assert packet[field] == source[field]


def test_d4_review_packet_keeps_blocking_status_visible():
    packet = build_operator_review_visibility_packet(_source_packet())
    assert packet['review_status'] == 'REVIEW_REQUIRED'
    assert packet['operator_review_required'] is True
    assert packet['circuit_break'] is True
    assert packet['display_blocked'] is True


def test_d4_review_packet_has_no_visibility_errors_when_all_fields_preserved():
    packet = build_operator_review_visibility_packet(_source_packet())
    assert packet['visibility_errors'] == []


def test_d4_review_packet_does_not_replace_reason_codes_or_risk_flags_with_summary_only():
    packet = build_operator_review_visibility_packet(_source_packet())
    assert 'MISSING_REQUIRED_FIELD' in packet['reason_codes']
    assert 'UNSAFE_PERMISSION' in packet['reason_codes']
    assert 'REVIEW_REQUIRED' in packet['risk_flags']
    assert 'CIRCUIT_BREAK' in packet['risk_flags']
    assert 'CONFLICT_SIGNAL' in packet['risk_flags']

