import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = Path("apps/v2_r21_local_robust_normalization_foundation_app_1/contracts.py")
NORMALIZATION = Path("apps/v2_r21_local_robust_normalization_foundation_app_1/normalization.py")
DOCS = tuple(Path(f"docs/V2_R22_LOCAL_ROBUST_NORMALIZATION_INTEGRITY_HARDENING_APP_1_D{i}.md") for i in range(1, 7))


def build_v2_r22_guard_report(root: Path = ROOT) -> dict[str, object]:
    try:
        contracts = (root / CONTRACTS).read_text(encoding="ascii")
        normalization = (root / NORMALIZATION).read_text(encoding="ascii")
        docs = tuple((root / path).read_text(encoding="ascii") for path in DOCS)
        ascii_only = True
    except (FileNotFoundError, UnicodeDecodeError): contracts, normalization, docs, ascii_only = "", "", (), False
    checks = {
        "hardening_and_docs_ascii": ascii_only,
        "docs_complete": len(docs) == 6 and all("P1-P47 frozen" in document and "no P48" in document for document in docs),
        "instrument_identity_closed": "factor series instrument mismatch" in contracts,
        "evidence_state_closed": all(token in normalization for token in ("invalid normalization evidence state", "missing-state evidence is inconsistent", "non-ready normalization evidence cannot carry metrics")),
        "operator_and_hash_closed": "requires Operator review" in normalization and "lowercase SHA-256" in normalization,
        "formula_unchanged": "raw_median = _median(available)" in normalization and "raw_mad = _median" in normalization,
        "no_runtime_expansion": all(token not in (contracts + normalization).lower() for token in ("import requests", "import socket", "place_order", "websocket")),
    }
    return {"checks": checks, "ok": all(checks.values())}


def main() -> int:
    report = build_v2_r22_guard_report()
    if report["ok"] is not True: raise SystemExit("V2-R22 normalization integrity guard failed")
    print(json.dumps(report, sort_keys=True)); return 0


if __name__ == "__main__": raise SystemExit(main())
