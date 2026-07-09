from pathlib import Path

from sidecars.ui_risk_flag_visibility_app_1 import (
    build_operator_review_visibility_packet,
    build_visibility_guard_report,
    validate_visibility_preservation,
)


FINAL_DOC = Path('docs/sidecars/ui-risk-flag-visibility-app-1/UI_RISK_FLAG_VISIBILITY_FINAL_CLOSEOUT_D6.md')

REQUIRED_DOCS = [
    Path('docs/sidecars/ui-risk-flag-visibility-app-1/UI_RISK_FLAG_VISIBILITY_CONTRACT_D1.md'),
    Path('docs/sidecars/ui-risk-flag-visibility-app-1/UI_RISK_FLAG_VISIBILITY_SCHEMA_D2.md'),
    Path('docs/sidecars/ui-risk-flag-visibility-app-1/UI_RISK_FLAG_VISIBILITY_VALIDATOR_D3.md'),
    Path('docs/sidecars/ui-risk-flag-visibility-app-1/UI_RISK_FLAG_VISIBILITY_REVIEW_PACKET_D4.md'),
    Path('docs/sidecars/ui-risk-flag-visibility-app-1/UI_RISK_FLAG_VISIBILITY_GUARD_REPORT_D5.md'),
    FINAL_DOC,
]


def test_d6_all_stage_documents_exist():
    for path in REQUIRED_DOCS:
        assert path.exists(), f'missing required sidecar document: {path}'


def test_d6_final_closeout_declares_core_and_safety_boundaries():
    text = FINAL_DOC.read_text(encoding='utf-8')
    assert 'P1-P47 frozen' in text
    assert 'no P48' in text
    assert 'no core mutation' in text
    assert 'paper-only' in text
    assert 'local-only' in text
    assert 'read-only' in text
    assert 'operator review required' in text


def test_d6_final_closeout_preserves_required_risk_controls():
    text = FINAL_DOC.read_text(encoding='utf-8')
    for marker in [
        'risk_flags',
        'reason_codes',
        'REVIEW_REQUIRED must not auto-pass',
        'CIRCUIT_BREAK must not downgrade',
        'conflict_signals',
        'missing_required_fields',
        'unsafe_permissions',
        'correlation_id',
        'source_artifact',
        'evidence_chain_status',
    ]:
        assert marker in text


def test_d6_public_exports_are_available():
    assert callable(validate_visibility_preservation)
    assert callable(build_operator_review_visibility_packet)
    assert callable(build_visibility_guard_report)


def test_d6_guard_report_accepts_complete_packet():
    source = {
        'candidate_id': 'D6_SAMPLE',
        'risk_flags': ['REVIEW_REQUIRED', 'CIRCUIT_BREAK'],
        'reason_codes': ['MISSING_REQUIRED_FIELD'],
        'review_status': 'REVIEW_REQUIRED',
        'blocked_reasons': ['missing_required_fields'],
        'conflict_signals': ['model_signal_conflict'],
        'missing_required_fields': ['evidence_chain_status'],
        'unsafe_permissions': ['attempted_execution_permission'],
        'operator_review_required': True,
        'circuit_break': True,
        'correlation_id': 'D6-CORRELATION-SAMPLE',
        'source_artifact': 'd6-source-artifact',
        'evidence_chain_status': 'incomplete',
    }
    report = build_visibility_guard_report([(source, dict(source))])
    assert report['total_packets'] == 1
    assert report['passed_packets'] == 1
    assert report['failed_packets'] == 0
    assert report['display_blocked_packets'] == 1

