from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0090_a_share_guojin_qmt_local_terminal_liveness_evidence_app_1.contracts import (  # noqa: E402
    DEFAULT_REGISTRATION,
    build_evidence,
    build_snapshot,
    render_evidence_json,
)


AUTHORITY_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    "docs/HANDOFF_PROMPT.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
)
DELIVERY_ID = (
    "FCF-FCP-0090-A-SHARE-GUOJIN-QMT-LOCAL-TERMINAL-LIVENESS-"
    "EVIDENCE-APP-1"
)
PREFIX = "FCP 0090 A SHARE GUOJIN QMT LOCAL TERMINAL LIVENESS EVIDENCE APP 1"


def _read_ascii(path: Path) -> str:
    return path.read_text(encoding="ascii")


def _block(text: str, kind: str) -> str | None:
    start = f"<!-- {PREFIX} {kind} START -->"
    end = f"<!-- {PREFIX} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return None
    first = text.index(start)
    last = text.index(end)
    return text[first : last + len(end)] if first < last else None


def build_fcp_0090_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple(_read_ascii(root / path) for path in AUTHORITY_PATHS)
        manifest = json.loads(_read_ascii(root / "FCF_CURRENT_STATE_MANIFEST.json"))
        intake = json.loads(
            _read_ascii(root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json")
        )
        architecture = _read_ascii(
            root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
        )
        adr = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md")
        gaps = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md")
        protocol = _read_ascii(root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md")
        memory = _read_ascii(root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md")
        run_all = _read_ascii(root / "scripts/run_all_checks.py")
        observer = _read_ascii(
            root
            / "apps/fcp_0090_a_share_guojin_qmt_local_terminal_liveness_evidence_app_1/observer.py"
        )
        delivered = _read_ascii(
            root
            / "FCF_CURRENT_STATE_FCP_0090_A_SHARE_GUOJIN_QMT_LOCAL_TERMINAL_LIVENESS_EVIDENCE_APP_1_DELIVERED.md"
        )
        reference = build_evidence(
            build_snapshot(
                ["XtMiniQmt.exe"],
                datetime(2026, 7, 23, 0, 50, tzinfo=timezone.utc),
            )
        )
        reference_output = render_evidence_json(reference).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        texts, manifest, intake = (), {}, {}
        architecture = adr = gaps = protocol = memory = run_all = ""
        observer = delivered = ""
        reference = None
        reference_output = b""
        readable = False

    truth = manifest.get("current_truth", {})
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID and status in {
        "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
    }
    closed = truth.get("current_governance_phase_id") == "NONE" and truth.get(
        "latest_completed_governance_delivery"
    ) == DELIVERY_ID
    approvals = tuple(_block(text, "APPROVAL") for text in texts)
    locks = tuple(_block(text, "LOCK") for text in texts)
    finals = tuple(_block(text, "FINAL") for text in texts)
    proposal = next(
        (
            item
            for item in intake.get("proposals", [])
            if item.get("proposal_id") == "FCF-FCP-0090"
        ),
        {},
    )
    required = {
        "FCF_CURRENT_STATE_FCP_0090_A_SHARE_GUOJIN_QMT_LOCAL_TERMINAL_LIVENESS_EVIDENCE_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0090_A_SHARE_GUOJIN_QMT_LOCAL_TERMINAL_LIVENESS_EVIDENCE_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0090_A_SHARE_GUOJIN_QMT_LOCAL_TERMINAL_LIVENESS_EVIDENCE_APP_1_FINAL.md",
        "docs/FCF_FCP_0090_A_SHARE_GUOJIN_QMT_LOCAL_TERMINAL_LIVENESS_EVIDENCE_APP_1_D1_D6.md",
    }
    final_path = next(path for path in required if "FINAL" in path)
    forbidden = (
        "subprocess",
        "psutil",
        "tasklist",
        "Get-Process",
        "CommandLine",
        "ExecutablePath",
        "OpenProcess",
    )
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5
        and all(approvals)
        and len(set(approvals)) == 1,
        "lock_exact_when_implemented": status
        not in {
            "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
            "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
        }
        or (all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed
        or (all(finals) and len(set(finals)) == 1),
        "final_evidence_when_closed": not closed
        or ((root / final_path).is_file() and "ALL CHECKS PASSED" in finals[0]),
        "manifest_state_safe": active
        or closed
        or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status")
        == proposal.get("operator_decision")
        == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and required.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": (
            "## 123. Guojin QMT Local Terminal Liveness Evidence" in architecture
        ),
        "adr_registered": "FCF-V2-ADR-090" in adr,
        "gap_preserved": "## FCP-0090 Evidence Boundary" in gaps
        and "| V2-FR-GAP-104 |" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0090`" in protocol,
        "memory_registered": "FCP-0090 preserves bounded path-free" in memory,
        "observer_is_narrow": "Process32FirstW" in observer
        and "szExeFile" in observer
        and all(term not in observer for term in forbidden),
        "run_all_wired": (
            "control_center_fcp_0090_a_share_guojin_qmt_local_terminal_liveness_evidence_guard.py"
            in run_all
        ),
        "reference_contract_exact": reference is not None
        and DEFAULT_REGISTRATION.contract_sha256
        == "c82466c987b415d5d78db0dba161fc1653b651d8caa642860ba5dda6772c097a",
        "reference_evidence_exact": reference is not None
        and reference.evidence_hash
        == "73683bffb99cbb428c275ea8e07c85e0edf8e41177c9dcf949e6fca1afd2af17",
        "reference_output_exact": hashlib.sha256(reference_output).hexdigest()
        == "366c02360c7192505a3d651e20c84d21b238e1188203a4a3443e9f2681c0ab6a",
        "delivered_boundary_exact": "TERMINAL_NOT_OBSERVED" in delivered
        and "GAP-104 remains RESEARCH_REQUIRED" in delivered,
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0090_guard_report()
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
