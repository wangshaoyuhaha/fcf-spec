from pathlib import Path


def test_d1_visibility_contract_exists():
    path = Path('app/ui_risk_flag_visibility/D1_VISIBILITY_CONTRACT.md')
    assert path.exists()
    text = path.read_text(encoding='utf-8')
    assert 'risk_flags must be rendered explicitly' in text
    assert 'reason_codes must be rendered explicitly' in text
    assert 'blocked_response_state must be rendered explicitly' in text
    assert 'operator_review_required must be rendered explicitly' in text
    assert 'risk flag downgrade is forbidden' in text
    assert 'risk flag deletion is forbidden' in text
    assert 'reason code deletion is forbidden' in text
    assert 'operator review bypass is forbidden' in text
    assert 'no buy button' in text
    assert 'no sell button' in text
    assert 'no order button' in text
    assert 'no tag' in text
    assert 'no release' in text
    assert 'no deploy' in text
