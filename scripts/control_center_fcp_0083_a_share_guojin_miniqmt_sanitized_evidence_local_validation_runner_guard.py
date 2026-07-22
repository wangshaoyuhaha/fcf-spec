from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

try:
    from scripts.fcp_governance_sequence import is_historical_delivery_state_safe
except ModuleNotFoundError:
    from fcp_governance_sequence import is_historical_delivery_state_safe


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.fcp_0082_a_share_guojin_miniqmt_python_market_data_entitlement_evidence_contract_app_1 import (  # noqa: E402
    build_reference_packet,
)
from apps.fcp_0083_a_share_guojin_miniqmt_sanitized_evidence_local_validation_runner_app_1 import (  # noqa: E402
    render_packet_json,
)


AUTHORITY_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
    "docs/HANDOFF_PROMPT.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
)
DELIVERY_ID = "FCF-FCP-0083-A-SHARE-GUOJIN-MINIQMT-SANITIZED-EVIDENCE-LOCAL-VALIDATION-RUNNER-APP-1"
MARKER = "FCP 0083 A SHARE GUOJIN MINIQMT SANITIZED EVIDENCE LOCAL VALIDATION RUNNER APP 1"
RUNNER_PATH = "apps/fcp_0083_a_share_guojin_miniqmt_sanitized_evidence_local_validation_runner_app_1/runner.py"
RUNNER_SHA = "ba9cf5e9db81eee2980c0d2bf0b882ce1e51d74ce7ee109d602b19bf0013c54b"
REFERENCE_OUTPUT_SHA = "f9a8e59c4278002c64342b91ec6d25245770663a4c38f14626f04f8380c873d5"


def _block(text: str, kind: str) -> str:
    start = f"<!-- {MARKER} {kind} START -->"
    end = f"<!-- {MARKER} {kind} END -->"
    if text.count(start) != 1 or text.count(end) != 1:
        return ""
    begin = text.index(start)
    finish = text.index(end, begin) + len(end)
    return text[begin:finish]


def _read_ascii(path: Path) -> str:
    return path.read_text(encoding="ascii")


def build_fcp_0083_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        texts = tuple(_read_ascii(root / path) for path in AUTHORITY_PATHS)
        manifest = json.loads(_read_ascii(root / "FCF_CURRENT_STATE_MANIFEST.json"))
        intake = json.loads(_read_ascii(root / "FCF_FUTURE_CAPABILITY_INTAKE_REGISTER.json"))
        architecture = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md")
        adr = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md")
        gaps = _read_ascii(root / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md")
        protocol = _read_ascii(root / "docs/FCF_FUTURE_CAPABILITY_CHANGE_PROTOCOL.md")
        memory = _read_ascii(root / "docs/FCF_PROJECT_MEMORY_AND_CONTINUITY_PROTOCOL.md")
        run_all = _read_ascii(root / "scripts/run_all_checks.py")
        runner_bytes = (root / RUNNER_PATH).read_bytes()
        runner_text = runner_bytes.decode("ascii")
        reference_packet = build_reference_packet()
        reference_output = render_packet_json(reference_packet).encode("ascii")
        readable = True
    except (OSError, UnicodeError, ValueError, TypeError, json.JSONDecodeError):
        texts, manifest, intake = (), {}, {}
        architecture = adr = gaps = protocol = memory = run_all = runner_text = ""
        runner_bytes = reference_output = b""
        reference_packet = None
        readable = False
    truth = manifest.get("current_truth", {})
    status = truth.get("current_governance_phase_status")
    active = truth.get("current_governance_phase_id") == DELIVERY_ID and status in {
        "APPROVED_GOVERNANCE_ONLY_NOT_STARTED",
        "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
        "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
    }
    closed = truth.get("current_governance_phase_id") == "NONE" and truth.get("latest_completed_governance_delivery") == DELIVERY_ID
    approvals = tuple(_block(text, "APPROVAL") for text in texts)
    locks = tuple(_block(text, "LOCK") for text in texts)
    finals = tuple(_block(text, "FINAL") for text in texts)
    proposal = next((item for item in intake.get("proposals", []) if item.get("proposal_id") == "FCF-FCP-0083"), {})
    expected = {
        "FCF_CURRENT_STATE_FCP_0083_A_SHARE_GUOJIN_MINIQMT_SANITIZED_EVIDENCE_LOCAL_VALIDATION_RUNNER_APP_1_APPROVED.md",
        "FCF_CURRENT_STATE_FCP_0083_A_SHARE_GUOJIN_MINIQMT_SANITIZED_EVIDENCE_LOCAL_VALIDATION_RUNNER_APP_1_DELIVERED.md",
        "FCF_CURRENT_STATE_FCP_0083_A_SHARE_GUOJIN_MINIQMT_SANITIZED_EVIDENCE_LOCAL_VALIDATION_RUNNER_APP_1_FINAL.md",
        "docs/FCF_FCP_0083_A_SHARE_GUOJIN_MINIQMT_SANITIZED_EVIDENCE_LOCAL_VALIDATION_RUNNER_APP_1_D1_D6.md",
    }
    gap_row = next((line for line in gaps.splitlines() if "| V2-FR-GAP-104 |" in line), "")
    prohibited = ("import xtquant", "from xtquant", "import requests", "import socket", "import urllib", ".write_bytes(", ".write_text(")
    checks = {
        "files_ascii_and_json": readable,
        "approval_exact": len(texts) == 5 and all(approvals) and len(set(approvals)) == 1,
        "lock_exact_when_implemented": status not in {
            "GOVERNANCE_DELIVERY_IMPLEMENTED_PENDING_VALIDATION",
            "GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE",
        } or (all(locks) and len(set(locks)) == 1),
        "final_exact_when_closed": not closed or (all(finals) and len(set(finals)) == 1),
        "final_evidence_when_closed": not closed or (
            (root / next(path for path in expected if "FINAL" in path)).is_file()
            and all(finals)
            and "ALL CHECKS PASSED" in finals[0]
        ),
        "manifest_state_safe": active or closed or is_historical_delivery_state_safe(truth, DELIVERY_ID),
        "proposal_safe": proposal.get("status") == proposal.get("operator_decision") == "ACCEPTED_ARCHITECTURE"
        and proposal.get("phase_id") == "NONE"
        and expected.issubset(set(proposal.get("evidence_refs", []))),
        "architecture_registered": all(
            term in architecture
            for term in (
                "## 116. MiniQMT Sanitized Evidence Local Validation Runner",
                "existing regular non-symlink path",
                "performs no source mutation",
            )
        ),
        "adr_registered": all(
            term in adr
            for term in (
                "FCF-V2-ADR-083",
                "Provide A Read-Only Local MiniQMT Evidence Validator",
                "reads bounded bytes once",
            )
        ),
        "gap_preserved": "| RESEARCH_REQUIRED |" in gap_row,
        "gap_observation_registered": "FCP-0083 is approved" in gaps and "GAP-104" in gaps,
        "protocol_registered": "Proposal `FCF-FCP-0083`" in protocol,
        "memory_registered": "MiniQMT sanitized evidence runner" in memory,
        "run_all_wired": "control_center_fcp_0083_a_share_guojin_miniqmt_sanitized_evidence_local_validation_runner_guard.py" in run_all,
        "runner_hash_exact": hashlib.sha256(runner_bytes).hexdigest() == RUNNER_SHA,
        "reference_output_hash_exact": hashlib.sha256(reference_output).hexdigest() == REFERENCE_OUTPUT_SHA,
        "reference_output_non_authorizing": reference_packet is not None
        and reference_packet.entitlement_authorized is False
        and reference_packet.realtime_activation_authorized is False
        and reference_packet.provider_selected is False,
        "runner_read_only_and_provider_free": not any(term in runner_text for term in prohibited),
        "delivery_files_exist": all((root / path).is_file() for path in expected if "FINAL" not in path)
        and ((root / next(path for path in expected if "FINAL" in path)).is_file() if closed else True),
        "no_product_phase": truth.get("current_product_implementation_phase") == "NONE",
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_fcp_0083_guard_report()
    print(json.dumps(report, ensure_ascii=True, sort_keys=True))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
