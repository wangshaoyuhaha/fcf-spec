from pathlib import Path

def test_control_center_maintenance_d6_closeout_exists():
    path = Path('docs/control_center_maintenance_app_1/D6_FINAL_CLOSEOUT.md')
    assert path.exists()
    text = path.read_text(encoding='utf-8')
    assert 'D6 Final Closeout' in text
    assert 'D1 maintenance contract' in text
    assert 'D5 validation and clean-status checklist' in text
    assert 'repo control center remains source of truth' in text
    assert 'Ready for main merge review' in text
    assert 'no deploy' in text
    assert 'no release' in text
    assert 'no tag' in text

def test_control_center_maintenance_final_state_exists():
    path = Path('FCF_CURRENT_STATE_CONTROL_CENTER_MAINTENANCE_APP_1_FINAL.md')
    assert path.exists()
    text = path.read_text(encoding='utf-8')
    assert 'CONTROL-CENTER-MAINTENANCE-APP-1' in text
    assert 'Completed' in text
