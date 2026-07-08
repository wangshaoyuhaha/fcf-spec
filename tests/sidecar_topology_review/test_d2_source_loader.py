import importlib.util
from pathlib import Path


def load_module():
    path = Path("app/sidecar_topology_review/source_loader.py")
    spec = importlib.util.spec_from_file_location("source_loader", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_d2_source_loader_inventory_and_zones():
    module = load_module()
    rows = module.load_completed_sidecar_inventory()
    ids = {row["sidecar_id"] for row in rows}
    assert len(rows) >= 18
    assert "CORRELATION-ID-TRACEABILITY-APP-1" in ids
    assert "CONTROL-CENTER-MAINTENANCE-APP-1" in ids
    assert set(module.load_zone_names()) == {
        "data_ingestion_and_quarantine",
        "context_and_interpretation",
        "governance_and_review_gate",
        "presentation_and_immutable_archive",
    }
    for row in rows:
        assert row["paper_only"] is True
        assert row["local_only"] is True
        assert row["read_only"] is True
        assert row["sidecar_only"] is True
        assert row["operator_review_required"] is True
        assert row["core_mutation_allowed"] is False
        assert row["p48_core_expansion_allowed"] is False
        assert row["trade_action_allowed"] is False
        assert row["real_execution_allowed"] is False
