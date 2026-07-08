from pathlib import Path


def test_d1_topology_contract_exists():
    path = Path('app/sidecar_topology_review/D1_TOPOLOGY_CONTRACT.md')
    assert path.exists()
    text = path.read_text(encoding='utf-8')
    assert 'DAG-only dependency rule' in text
    assert 'no circular dependency' in text
    assert 'data_ingestion_and_quarantine' in text
    assert 'context_and_interpretation' in text
    assert 'governance_and_review_gate' in text
    assert 'presentation_and_immutable_archive' in text
    assert 'no P48 core expansion' in text
    assert 'no real trading' in text
    assert 'no tag' in text
    assert 'no release' in text
    assert 'no deploy' in text
