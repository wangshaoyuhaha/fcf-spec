import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _text(path: str) -> str:
    return (ROOT / path).read_text(encoding="ascii")


def test_d1_contract_and_collateral_registry_is_preserved():
    architecture = _text(
        "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
    )
    assert "venue-versioned contract registry" in architecture
    assert "linear or inverse settlement" in architecture
    assert "delisting or migration evidence" in architecture


def test_d2_margin_position_mode_and_pnl_are_separate():
    architecture = _text(
        "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
    )
    assert "isolated or cross margin" in architecture
    assert "one-way or hedge position-mode" in architecture
    assert "realized and unrealized PnL accounting" in architecture


def test_d3_funding_cost_latency_and_outage_are_registered():
    architecture = _text(
        "docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_EXPANSION_ARCHITECTURE.md"
    )
    assert "funding interval, cap, floor, direction" in architecture
    assert "partial-fill, latency, outage" in architecture


def test_d4_liquidation_adl_and_insurance_are_not_collapsed():
    adr = _text("docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_ADR_REGISTER.md")
    assert "index, mark, bankruptcy, or liquidation price" in adr
    assert "ADL, insurance-fund" in adr


def test_d5_all_new_gaps_remain_unfinished():
    gaps = _text("docs/FCF_V2_FACTOR_REALTIME_COGNITIVE_GAP_BACKLOG.md")
    for index in range(96, 104):
        row = next(
            line for line in gaps.splitlines() if f"V2-FR-GAP-{index:03d}" in line
        )
        assert row.endswith(("| NOT_IMPLEMENTED |", "| RESEARCH_REQUIRED |"))


def test_d6_manifest_preserves_phase_and_execution_boundaries():
    manifest = json.loads(_text("FCF_CURRENT_STATE_MANIFEST.json"))
    truth = manifest["current_truth"]
    safety = manifest["safety_boundaries"]
    assert truth["current_product_implementation_phase"] == "NONE"
    assert truth["next_product_implementation_phase"] == "NOT_SELECTED"
    assert truth["next_product_phase_approval"] == "NOT_APPROVED"
    assert safety["broker_path_allowed"] is False
    assert safety["exchange_path_allowed"] is False
    assert safety["credential_path_allowed"] is False
    assert safety["order_or_execution_path_allowed"] is False
