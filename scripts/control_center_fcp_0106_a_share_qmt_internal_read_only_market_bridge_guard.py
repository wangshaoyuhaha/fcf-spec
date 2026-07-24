from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0106_a_share_qmt_internal_read_only_market_bridge_app_1 import (
    build_reference_event_bytes,
    build_reference_snapshot,
    inspect_bridge_file,
    render_reference_snapshot_json,
)


PHASE_ID = "FCF-FCP-0106-A-SHARE-QMT-INTERNAL-READ-ONLY-MARKET-BRIDGE-APP-1"
APPROVED = ROOT / (
    "FCF_CURRENT_STATE_FCP_0106_A_SHARE_QMT_INTERNAL_READ_ONLY_"
    "MARKET_BRIDGE_APP_1_APPROVED.md"
)
DELIVERED = ROOT / (
    "FCF_CURRENT_STATE_FCP_0106_A_SHARE_QMT_INTERNAL_READ_ONLY_"
    "MARKET_BRIDGE_APP_1_DELIVERED.md"
)
FINAL = ROOT / (
    "FCF_CURRENT_STATE_FCP_0106_A_SHARE_QMT_INTERNAL_READ_ONLY_"
    "MARKET_BRIDGE_APP_1_FINAL.md"
)
AUTHORITY = (
    ROOT / "docs/FCF_PROJECT_CONTROL_CENTER.md",
    ROOT / "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    ROOT / "docs/HANDOFF_PROMPT.md",
    ROOT / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    ROOT / "FCF_NEW_WINDOW_CHAT_PROMPT.md",
)
SOURCE_HASHES = {
    "__init__.py": "b556637b393a86b51d4a4310fb7c370d2a25d9f74c3acbb723ff1674d64ae6a6",
    "acceptance.py": "fdb09e149b7ef308aa12ba0f22812d6c95909d085d486246a6be4317caa9117a",
    "bridge_policy.py": "30931d19ccc46e08401bcf89f8da099fa0c7457cd21c869faa570c37d34ac4fb",
    "builder.py": "4f36e43210a75ca6b5fea3f4487756d58a74f4b019350d8be6c77e75143dffe1",
    "contracts.py": "531b2ad82c6d4ea50dd1a33c4099b2239ea5a58375230ede0d2b4ec93a132552",
    "qmt_bridge.py": "b2eac57691f9603e96a76345318c11d4deaf2a71c817f86c88c65e877614e6f9",
    "receiver.py": "3746dd07ddc5a1108b4448899af620d82edd324b96c3856df2eb9e3600c08fa8",
}
PROBE_SHA = "a888c7a3aa8541583a86214762df1e3b1d2092bb4ac4e769220b4d9a86c29c44"
RUNBOOK_SHA = "f1978562c4d3b371ff2a4879703452a025c1d6996e3840694c06be15879d3f7a"
CONFIG_SHA = "eb762b4b883cf1745047a7ff6666a1676c8ff746c4563a5d41807f82eeed38a6"
EVENT_SHA = "4e1d4eebfbbd8df624edcf67c1ce530e8ec94c899a6cee70ea4fa67973d46026"
SNAPSHOT_SHA = "be09c874260b69192f158390ccad2b0cb4dad27746312e851c4078558aae3a92"
OUTPUT_SHA = "ded1a6e758a108d4c91527096d3ddd4cafe261a9836fb5f9cb6b0f8dbd851f22"


def _block(text: str, kind: str) -> str:
    prefix = "FCP 0106 A SHARE QMT INTERNAL READ ONLY MARKET BRIDGE APP 1"
    start = f"<!-- {prefix} {kind} START -->"
    end = f"<!-- {prefix} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    return text.split(start, 1)[1].split(end, 1)[0].strip()


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_fcp_0106_guard_report(root: Path = ROOT) -> dict[str, object]:
    readable = True
    texts: dict[str, str] = {}
    paths = {
        "approved": APPROVED,
        "delivered": DELIVERED,
        "d1_d6": root
        / "docs/FCF_FCP_0106_A_SHARE_QMT_INTERNAL_READ_ONLY_MARKET_BRIDGE_APP_1_D1_D6.md",
        "adr": root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md",
        "gap": root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md",
        "protocol": root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md",
        "memory": root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md",
        "run_all": root / "scripts/run_all_checks.py",
    }
    try:
        for name, path in paths.items():
            texts[name] = path.read_text(encoding="ascii")
        authority_texts = tuple(path.read_text(encoding="ascii") for path in AUTHORITY)
        manifest = json.loads(
            (root / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
        )
        register = json.loads(
            (root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json").read_text(
                encoding="ascii"
            )
        )
    except (OSError, UnicodeError, json.JSONDecodeError):
        readable = False
        authority_texts = ()
        manifest = {}
        register = {}
    approvals = tuple(_block(text, "APPROVAL") for text in authority_texts)
    locks = tuple(_block(text, "LOCK") for text in authority_texts)
    finals = tuple(_block(text, "FINAL") for text in authority_texts)
    complete = FINAL.exists()
    proposal = next(
        (
            item
            for item in register.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0106"
        ),
        {},
    )
    truth = manifest.get("current_truth", {})
    source_dir = (
        root / "apps/fcp_0106_a_share_qmt_internal_read_only_market_bridge_app_1"
    )
    source_hashes = {name: _sha(source_dir / name) for name in SOURCE_HASHES}
    bridge_report = inspect_bridge_file(source_dir / "qmt_bridge.py")
    snapshot = build_reference_snapshot()
    output = render_reference_snapshot_json().encode("ascii")
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(approvals) == 5
        and all(approvals)
        and len(set(approvals)) == 1,
        "lock_exact": len(locks) == 5 and all(locks) and len(set(locks)) == 1,
        "final_exact_when_complete": (
            not complete
            or len(finals) == 5
            and all(finals)
            and len(set(finals)) == 1
        ),
        "adr_registered": "FCF-V2-ADR-106" in texts.get("adr", ""),
        "gap_registered": (
            "## FCP-0106 A-Share QMT Internal Read-Only Market Bridge Boundary"
            in texts.get("gap", "")
        ),
        "protocol_registered": "Proposal `FCF-FCP-0106`"
        in texts.get("protocol", ""),
        "memory_registered": "FCP-0106 adds one ordinary Guojin QMT internal"
        in texts.get("memory", ""),
        "proposal_state_exact": proposal.get("operator_decision")
        == ("ACCEPTED_ARCHITECTURE" if complete else "APPROVED")
        and proposal.get("phase_id") == ("NONE" if complete else PHASE_ID)
        and register.get("next_proposal_sequence") == 107,
        "manifest_state_exact": truth.get("latest_completed_governance_delivery")
        == (
            PHASE_ID
            if complete
            else "FCF-FCP-0105-REGISTERED-PRICE-SHAPE-INDICATOR-RUNTIME-APP-1"
        )
        and truth.get("current_governance_phase_id")
        == ("NONE" if complete else PHASE_ID),
        "source_hashes_exact": source_hashes == SOURCE_HASHES,
        "operator_probe_hash_exact": _sha(
            root / "scripts/run_fcp_0106_qmt_live_operator_review_probe.py"
        )
        == PROBE_SHA,
        "operator_runbook_hash_exact": _sha(
            root / "docs/FCF_FCP_0106_QMT_LIVE_OPERATOR_REVIEW_RUNBOOK.md"
        )
        == RUNBOOK_SHA,
        "config_hash_exact": _sha(
            root / "integrations/guojin_qmt/fcf_qmt_bridge_config.example.json"
        )
        == CONFIG_SHA,
        "reference_event_exact": hashlib.sha256(
            build_reference_event_bytes()
        ).hexdigest()
        == EVENT_SHA,
        "reference_snapshot_exact": snapshot.snapshot_hash == SNAPSHOT_SHA,
        "reference_output_exact": hashlib.sha256(output).hexdigest() == OUTPUT_SHA,
        "bridge_source_policy_exact": bridge_report.ok
        and bridge_report.context_calls == ("set_universe", "subscribe_quote")
        and not bridge_report.forbidden_calls
        and not bridge_report.forbidden_imports,
        "reference_non_authorizing": snapshot.operator_review_required
        and snapshot.read_only
        and not any(
            (
                snapshot.market_data_authority,
                snapshot.data_promotion_authority,
                snapshot.account_authority,
                snapshot.execution_authority,
            )
        ),
        "state_evidence_registered": (
            "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE"
            in texts.get("delivered", "")
            or "COMPLETED_MERGED_VALIDATED" in texts.get("delivered", "")
        )
        and (not complete or "COMPLETED_MERGED_VALIDATED" in FINAL.read_text("ascii")),
        "d1_d6_registered": all(
            f"## D{number} " in texts.get("d1_d6", "") for number in range(1, 7)
        ),
        "run_all_wired": (
            "control_center_fcp_0106_a_share_qmt_internal_read_only_market_bridge_guard.py"
            in texts.get("run_all", "")
        ),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0106_guard_report()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
