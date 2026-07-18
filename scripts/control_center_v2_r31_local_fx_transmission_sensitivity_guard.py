import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from apps.v2_r31_local_fx_transmission_sensitivity_foundation_app_1 import V2_R31_LOCAL_FX_TRANSMISSION_SENSITIVITY_BOUNDARY
APP_ROOT=Path("apps/v2_r31_local_fx_transmission_sensitivity_foundation_app_1");APP_FILES=("__init__.py","acceptance.py","boundary.py","contracts.py","presentation.py","registry.py","resolver.py");DOCS=tuple(Path(f"docs/V2_R31_LOCAL_FX_TRANSMISSION_SENSITIVITY_FOUNDATION_APP_1_D{i}.md") for i in range(1,7));PROHIBITED=("import requests","import socket","from urllib","import subprocess","websocket","place_order","score_candidate")
def build_v2_r31_guard_report(root:Path=ROOT)->dict[str,object]:
    try:text="\n".join((root/APP_ROOT/name).read_text(encoding="ascii") for name in APP_FILES);docs=tuple((root/path).read_text(encoding="ascii") for path in DOCS);ascii_only=True
    except (FileNotFoundError,UnicodeDecodeError):text,docs,ascii_only="",(),False
    b=V2_R31_LOCAL_FX_TRANSMISSION_SENSITIVITY_BOUNDARY;checks={"surface_exact":sorted(x.name for x in (root/APP_ROOT).glob("*.py"))==sorted(APP_FILES),"app_and_docs_ascii":ascii_only,"docs_complete":len(docs)==6 and all("P1-P47 frozen" in x and "No P48" in x for x in docs),"contract_present":all(x in text for x in ("RegisteredFXTransmissionSeries","FXTransmissionSensitivityRecord","usd_cny_beta_bps","usd_cny_correlation_bps","NO_CAUSAL_CONCLUSION")),"no_prohibited_runtime":all(x not in text.lower() for x in PROHIBITED),"boundary_closed":b.local_only and b.registered_artifact_only and not b.network_access_allowed and not b.live_source_allowed and not b.foreign_flow_inference_allowed and not b.causal_conclusion_allowed and not b.factor_activation_allowed and not b.order_or_execution_allowed};return {"checks":checks,"ok":all(checks.values())}
def main()->int:
    report=build_v2_r31_guard_report()
    if report["ok"] is not True:raise SystemExit("V2-R31 FX transmission guard failed")
    print(json.dumps(report,sort_keys=True));return 0
if __name__=="__main__":raise SystemExit(main())
