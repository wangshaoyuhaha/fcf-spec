from sidecars.ui_risk_flag_visibility_app_1 import build_visibility_guard_report


def _source_packet(candidate_id='D5_SAMPLE_PACKET'):
    return {
        'candidate_id': candidate_id,
        'risk_flags': ['REVIEW_REQUIRED', 'CIRCUIT_BREAK', 'CONFLICT_SIGNAL'],
        'reason_codes': ['MISSING_REQUIRED_FIELD', 'UNSAFE_PERMISSION'],
        'review_status': 'REVIEW_REQUIRED',
        'blocked_reasons': ['missing_required_fields', 'unsafe_permissions'],
        'conflict_signals': ['model_signal_conflict'],
        'missing_required_fields': ['evidence_chain_status'],
        'unsafe_permissions': ['attempted_execution_permission'],
        'operator_review_required': True,
        'circuit_break': True,
        'correlation_id': 'D5-CORRELATION-SAMPLE',
        'source_artifact': 'd5-source-artifact',
        'evidence_chain_status': 'incomplete',
    }


def test_d5_report_accepts_clean_preservation_packet():
    source = _source_packet()
    report = build_visibility_guard_report([(source, dict(source))])
    assert report['total_packets'] == 1
    assert report['passed_packets'] == 1
    assert report['failed_packets'] == 0
    assert report['operator_review_required_packets'] == 1
    assert report['display_blocked_packets'] == 1
    assert report['visibility_errors'] == []


def test_d5_report_detects_removed_reason_codes_and_risk_flags():
    source = _source_packet()
    rendered = dict(source)
    rendered['reason_codes'] = ['MISSING_REQUIRED_FIELD']
    rendered['risk_flags'] = ['REVIEW_REQUIRED']
    report = build_visibility_guard_report([(source, rendered)])
    assert report['passed_packets'] == 0
    assert report['failed_packets'] == 1
    errors = [item['error'] for item in report['visibility_errors']]
    assert 'reason_codes removed: UNSAFE_PERMISSION' in errors
    assert 'risk_flags removed: CIRCUIT_BREAK,CONFLICT_SIGNAL' in errors


def test_d5_report_detects_review_required_and_circuit_break_downgrade():
    source = _source_packet()
    rendered = dict(source)
    rendered['review_status'] = 'APPROVED'
    rendered['circuit_break'] = False
    report = build_visibility_guard_report([(source, rendered)])
    errors = [item['error'] for item in report['visibility_errors']]
    assert 'REVIEW_REQUIRED downgraded' in errors
    assert 'CIRCUIT_BREAK downgraded' in errors


def test_d5_report_detects_missing_operator_review_requirement():
    source = _source_packet()
    rendered = dict(source)
    rendered['operator_review_required'] = False
    report = build_visibility_guard_report([(source, rendered)])
    errors = [item['error'] for item in report['visibility_errors']]
    assert 'operator review requirement missing' in errors


def test_d5_report_summarizes_mixed_packet_results():
    clean_source = _source_packet('D5_CLEAN')
    bad_source = _source_packet('D5_BAD')
    bad_rendered = dict(bad_source)
    bad_rendered.pop('unsafe_permissions')
    report = build_visibility_guard_report([(clean_source, dict(clean_source)), (bad_source, bad_rendered)])
    assert report['total_packets'] == 2
    assert report['passed_packets'] == 1
    assert report['failed_packets'] == 1
    assert report['operator_review_required_packets'] == 2
    assert report['display_blocked_packets'] == 2
    assert any(item['candidate_id'] == 'D5_BAD' for item in report['visibility_errors'])

