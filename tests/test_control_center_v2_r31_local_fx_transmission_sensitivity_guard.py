from pathlib import Path
from scripts.control_center_v2_r31_local_fx_transmission_sensitivity_guard import APP_FILES,APP_ROOT,build_v2_r31_guard_report,main
ROOT=Path(__file__).resolve().parents[1]
def test_guard():assert build_v2_r31_guard_report(ROOT)["ok"] is True
def test_main():assert main()==0
def test_surface():assert sorted(x.name for x in (ROOT/APP_ROOT).glob("*.py"))==sorted(APP_FILES)
