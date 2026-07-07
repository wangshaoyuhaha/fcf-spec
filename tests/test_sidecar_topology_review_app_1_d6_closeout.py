from pathlib import Path

def test_final_closeout():
    assert Path("docs/sidecar_topology_review_app_1/D6_FINAL_CLOSEOUT.md").exists()
    assert Path("FCF_CURRENT_STATE_SIDECAR_TOPOLOGY_REVIEW_APP_1_FINAL.md").exists()