from sidecars.ui_risk_flag_visibility_app_1 import validate_visibility_preservation


def _source_packet():
    return {
        'risk_flags': ['REVIEW_REQUIRED', 'CIRCUIT_BREAK', 'CONFLICT_SIGNAL'],
        'reason_codes': ['MISSING_REQUIRED_FIELD', 'UNSAFE_PERMISSION'],
        'review_status': 'REVIEW_REQUIRED',
        'blocked_reasons': ['missing_required_fields'],
        'conflict_signals': ['model_signal_conflict'],
        'missing_required_fields': ['evidence_chain_status'],
        'unsafe_permissions': ['attempted_execution_permission'],
        'operator_review_required': True,
        'circuit_break': True,
        'correlation_id': 'D3-CORRELATION-SAMPLE',
        'source_artifact': 'd3-source-artifact',
        'evidence_chain_status': 'incomplete',
    }


def test_d3_accepts_full_visibility_preservation():
    source = _source_packet()
    rendered = dict(source)
    assert validate_visibility_preservation(source, rendered) == []


def test_d3_detects_missing_protected_fields():
    source = _source_packet()
    rendered = dict(source)
    rendered.pop('reason_codes')
    errors = validate_visibility_preservation(source, rendered)
    assert 'missing protected field: reason_codes' in errors


def test_d3_detects_review_required_downgrade():
    source = _source_packet()
    rendered = dict(source)
    rendered['review_status'] = 'APPROVED'
    errors = validate_visibility_preservation(source, rendered)
    assert 'REVIEW_REQUIRED downgraded' in errors


def test_d3_detects_circuit_break_downgrade():
    source = _source_packet()
    rendered = dict(source)
    rendered['circuit_break'] = False
    errors = validate_visibility_preservation(source, rendered)
    assert 'CIRCUIT_BREAK downgraded' in errors


def test_d3_detects_operator_review_requirement_removed():
    source = _source_packet()
    rendered = dict(source)
    rendered['operator_review_required'] = False
    errors = validate_visibility_preservation(source, rendered)
    assert 'operator review requirement missing' in errors


def test_d3_detects_removed_reason_codes_and_risk_flags():
    source = _source_packet()
    rendered = dict(source)
    rendered['reason_codes'] = ['MISSING_REQUIRED_FIELD']
    rendered['risk_flags'] = ['REVIEW_REQUIRED']
    errors = validate_visibility_preservation(source, rendered)
    assert 'reason_codes removed: UNSAFE_PERMISSION' in errors
    assert 'risk_flags removed: CIRCUIT_BREAK,CONFLICT_SIGNAL' in errors

