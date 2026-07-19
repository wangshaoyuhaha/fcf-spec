import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.controlled_learning_backtesting_p0_p3_stage_11 import (
    P0_P3_CAPABILITY_REGISTRY,
    P0_P3_IMPLEMENTATION_BINDINGS,
)
from apps.dify_ui_handoff_app_1.contract import UPSTREAM_READ_SOURCES
from apps.p4_controlled_enhancements_stage_12 import (
    P4_CAPABILITY_REGISTRY,
    P4_IMPLEMENTATION_BINDINGS,
)


GENERATED_OUTPUT_ALLOWLIST = (
    "runtime/learning_engine/shadow_ledger.json",
    "runtime/operator_console/status_snapshot.json",
    "runtime/operator_console/operator_review_packet.json",
    "runtime/operator_console/acceptance_summary.json",
    "runtime/operator_console/p13_branch_closeout_manifest.json",
    "runtime/operator_console/ai_learning_audit_report.json",
    "runtime/operator_console/ai_learning_memory_ledger.json",
    "runtime/operator_console/p13_final_closeout_summary.json",
)


def main() -> int:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements-dev.txt").read_text(encoding="ascii").strip()
    canonical_map = ROOT / "docs" / "CANONICAL_PACKAGE_AND_DEFERRED_PRODUCT_MAP.md"
    p0_p3 = {
        item for values in P0_P3_CAPABILITY_REGISTRY.values() for item in values
    }
    p4 = set(P4_CAPABILITY_REGISTRY["P4"])
    generated_dify_sources = [
        source
        for source in UPSTREAM_READ_SOURCES
        if source["relative_path"].startswith("artifacts/")
    ]
    tracked_dify_sources = [
        source
        for source in UPSTREAM_READ_SOURCES
        if not source["relative_path"].startswith("artifacts/")
    ]
    checks = {
        "canonical_map_present": canonical_map.is_file(),
        "generated_output_allowlist_exact": len(GENERATED_OUTPUT_ALLOWLIST) == 8,
        "generated_dify_sources_optional": bool(generated_dify_sources)
        and all(source["required"] is False for source in generated_dify_sources),
        "p0_p3_bindings_complete": set(P0_P3_IMPLEMENTATION_BINDINGS) == p0_p3,
        "p4_bindings_complete": set(P4_IMPLEMENTATION_BINDINGS) == p4,
        "pytest_dependency_pinned": requirements == "pytest==9.1.1",
        "readme_current_identity": "It is not FCF" not in readme
        and "Financial Cognitive Framework" in readme,
        "tracked_dify_sources_required": bool(tracked_dify_sources)
        and all(source["required"] is True for source in tracked_dify_sources),
        "known_duplicate_document_removed": not (
            ROOT / "docs" / "SIDECAR_DAG_DEPENDENCY_GUARD_APP_1_D4_IMPORT_BOUNDARY_SCAN.md"
        ).exists(),
    }
    if not all(checks.values()):
        raise SystemExit("active surface quality guard failed")
    print(json.dumps({"checks": checks, "ok": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
