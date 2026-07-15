from pathlib import Path

from apps.browser_product_console_runtime_app_1 import (
    FINAL_CLOSEOUT_STAGE_ID,
    build_operator_launch_final_closeout,
)
from scripts.run_browser_product_console_runtime import main


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_d6_closeout_is_ready_for_main_merge() -> None:
    closeout = build_operator_launch_final_closeout()

    assert FINAL_CLOSEOUT_STAGE_ID == "D6"
    assert closeout.status == "READY_FOR_MAIN_MERGE"
    assert closeout.completed_stages == (
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
    )
    assert closeout.product_acceptance_status == "READY_FOR_OPERATOR_USE"
    assert closeout.main_merge_authorized is True


def test_d6_closeout_preserves_operator_and_successor_state() -> None:
    closeout = build_operator_launch_final_closeout()

    assert closeout.operator_review_required is True
    assert closeout.successor_phase == "NOT_SELECTED"


def test_d6_default_product_preflight_passes(capsys) -> None:
    assert main(["--check"]) == 0
    output = capsys.readouterr()

    assert "FCF-LAUNCH-READY" in output.out
    assert "DEMONSTRATION_ONLY" in output.out
    assert "Registered artifacts: 14" in output.out
    assert output.err == ""


def test_d6_operator_handoff_files_exist() -> None:
    required = (
        PROJECT_ROOT / "START_FCF_BROWSER_CONSOLE.cmd",
        PROJECT_ROOT / "docs" / "BROWSER_PRODUCT_CONSOLE_OPERATOR_GUIDE.md",
        PROJECT_ROOT
        / "docs"
        / "BROWSER_PRODUCT_CONSOLE_OPERATOR_LAUNCH_APP_1_D6.md",
        PROJECT_ROOT
        / "docs"
        / "browser_product_console_operator_launch_app_1"
        / "FINAL_CURRENT_STATE.md",
    )

    assert all(path.is_file() for path in required)
