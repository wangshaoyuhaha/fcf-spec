from pathlib import Path

def test_control_center_maintenance_d3_merge_template_exists():
    path = Path('docs/control_center_maintenance_app_1/D3_MERGE_RECORD_TEMPLATE.md')
    assert path.exists()
    text = path.read_text(encoding='utf-8')
    assert 'D3 Merge Record Template' in text
    assert 'docs/FCF_PROJECT_CONTROL_CENTER.md' in text
    assert 'merge_commit' in text
    assert 'pytest_count' in text
    assert 'no deploy confirmation' in text
    assert 'safety confirmation' in text
    assert 'paper-only' in text
    assert 'no real execution' in text
