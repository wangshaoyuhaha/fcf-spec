from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / 'FCF_CURRENT_STATE_CORRELATION_ID_TRACEABILITY_APP_1_FINAL.md'


def test_correlation_id_traceability_final_state_archive_exists():
    assert DOC.exists()
    text = DOC.read_text(encoding='utf-8')
    required = [
        'FCF_CURRENT_STATE_CORRELATION_ID_TRACEABILITY_APP_1_FINAL',
        'e9bcfe update control center after CORRELATION-ID-TRACEABILITY-APP-1 merge',
        'b2ef1ce merge CORRELATION-ID-TRACEABILITY-APP-1 into main',
        '2da428d add CORRELATION-ID-TRACEABILITY-D6 final handoff closeout',
        '1582 passed',
        'D1 sidecar boundary and traceability contract',
        'D2 read-only source map',
        'D3 trace record schema',
        'D4 chain integrity rules',
        'D5 trace review packet',
        'D6 final handoff closeout',
        'Data',
        'Validation',
        'Operator Review',
        'UI Report',
        'Archive',
        'Dify handoff',
        'paper-only',
        'local-only',
        'read-only',
        'sidecar-only',
        'operator review required',
        'no P48 core expansion',
        'no P1-P47 core mutation',
        'no Dify deploy',
        'no Dify API write',
        'no tag',
        'no release',
        'no deploy',
    ]
    for item in required:
        assert item in text
