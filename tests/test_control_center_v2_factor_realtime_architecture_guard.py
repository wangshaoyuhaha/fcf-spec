import json
from pathlib import Path

from scripts.control_center_v2_factor_realtime_architecture_guard import (
    ADR_IDS,
    GAP_IDS,
    ROADMAP_PHASES,
    build_architecture_guard_report,
    main,
)


ROOT = Path(__file__).resolve().parents[1]


def test_v2_factor_realtime_architecture_guard_passes_repository():
    report = build_architecture_guard_report(ROOT)

    assert report["ok"] is True
    assert all(report["checks"].values())


def test_v2_factor_realtime_architecture_guard_main_passes():
    assert main() == 0


def test_v2_factor_realtime_architecture_registers_exact_adr_set():
    text = (
        ROOT / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md"
    ).read_text(encoding="ascii")

    assert len(ADR_IDS) == 20
    assert all(text.count(adr_id) == 1 for adr_id in ADR_IDS)


def test_v2_factor_realtime_architecture_registers_exact_gap_set():
    text = (
        ROOT / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
    ).read_text(encoding="ascii")

    assert len(GAP_IDS) == 70
    assert all(text.count(gap_id) == 1 for gap_id in GAP_IDS)


def test_v2_factor_realtime_roadmap_preserves_explicit_phase_authority():
    architecture = (
        ROOT / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
    ).read_text(encoding="ascii")

    for phase in ROADMAP_PHASES:
        assert f"{phase}:" in architecture
    assert (
        "- V2-R6: Paper Simulation Research; APPROVED / NOT_STARTED /"
        in architecture
        or "- V2-R6: Paper Simulation Research; COMPLETED /" in architecture
    )
    assert "No phase starts\nautomatically." in architecture
    assert "V2-R1: Factor Contract Foundation; COMPLETED" in architecture
    assert "V2-R2: Historical Factor Baseline; COMPLETED" in architecture
    assert "V2-R3: Realtime Ingestion Foundation; COMPLETED" in architecture
    assert (
        "V2-R7: Local Market Session Registry Foundation; "
        "APPROVED / NOT_STARTED" in architecture
        or "V2-R7: Local Market Session Registry Foundation; COMPLETED /"
        in architecture
    )
    assert (
        "V2-R8: Local Same-Time Baseline Foundation; "
        "APPROVED / NOT_STARTED" in architecture
        or "V2-R8: Local Same-Time Baseline Foundation; COMPLETED /"
        in architecture
    )
    manifest = json.loads(
        (ROOT / "FCF_CURRENT_STATE_MANIFEST.json").read_text(encoding="ascii")
    )
    statuses = {
        item["phase_id"]: item["status"] for item in manifest["roadmap"]
    }
    gap_lines = (
        ROOT / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
    ).read_text(encoding="ascii").splitlines()
    assert all(
        ("COMPLETED" in next(
            line
            for line in gap_lines
            if line.startswith(f"| {phase} |")
        ))
        == (statuses[phase] == "COMPLETED")
        for phase in ROADMAP_PHASES
    )
    assert "No V2-R implementation phase starts automatically" in "\n".join(
        path.read_text(encoding="ascii")
        for path in (
            ROOT / "docs/FCF_PROJECT_CONTROL_CENTER.md",
            ROOT / "docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md",
            ROOT / "docs/HANDOFF_PROMPT.md",
            ROOT / "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
            ROOT / "FCF_NEW_WINDOW_CHAT_PROMPT.md",
        )
    )


def test_v2_factor_realtime_architecture_preserves_no_execution_boundary():
    architecture = (
        ROOT / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
    ).read_text(encoding="ascii")

    assert "Real Execution Mode: OUTSIDE FCF AND PROHIBITED" in architecture
    assert "P1-P47 remain frozen" in architecture
    assert "No P48 is created" in architecture
    assert "AI remains advisory" in architecture


def test_v2_market_session_extension_is_architecture_only():
    architecture = (
        ROOT / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
    ).read_text(encoding="ascii")
    gap = (
        ROOT / "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md"
    ).read_text(encoding="ascii")

    assert "Market Session Registry and Exchange Calendar" in architecture
    assert "A-Share Call-Auction Research Contract" in architecture
    assert "Late-Session and Closing Research Contract" in architecture
    assert "Read-Only Operator Research Control Plane" in architecture
    assert (
        "| V2-FR-GAP-065 | automatic learning, promotion, and "
        "self-modification runtime | OUTSIDE_CURRENT_AUTHORIZATION |"
    ) in gap
