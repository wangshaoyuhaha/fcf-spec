from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_d6_closeout_documents_all_stages_and_next_runtime():
    files = tuple(
        ROOT
        / "docs"
        / f"CONTROL_CENTER_AUTHORITY_EXECUTION_CONTINUITY_APP_1_D{stage}.md"
        for stage in range(1, 7)
    )

    assert all(path.is_file() for path in files)
    closeout = files[-1].read_text(encoding="utf-8")
    assert "Status: READY_FOR_CLOSEOUT" in closeout
    assert "READ-ONLY-DATA-GATEWAY-APP-1" in closeout
    assert "No tag, release, deployment" in closeout
    assert (
        ROOT
        / "FCF_CURRENT_STATE_CONTROL_CENTER_"
        "AUTHORITY_EXECUTION_CONTINUITY_APP_1_FINAL.md"
    ).is_file()
