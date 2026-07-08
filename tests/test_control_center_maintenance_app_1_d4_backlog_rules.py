from pathlib import Path

def test_control_center_maintenance_d4_backlog_rules_exists():
    path = Path('docs/control_center_maintenance_app_1/D4_BACKLOG_DEFERRED_RULES.md')
    assert path.exists()
    text = path.read_text(encoding='utf-8')
    assert 'D4 Backlog Deferred Rules' in text
    assert 'DIFY-LOCAL-CONFIG-HARDENING-APP-1' in text
    assert 'explicit operator approval' in text
    assert 'no candidate sidecar may start automatically' in text
    assert 'no deferred item may be silently dropped' in text
    assert 'paper-only' in text
    assert 'no real execution' in text
    assert 'no deploy' in text
