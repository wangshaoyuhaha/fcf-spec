"""Controlled handoff cleanup utilities.

This module is paper-only, local-only, and sidecar-only.
It builds deterministic text updates for handoff documents.
"""

from __future__ import annotations


CURRENT_TRUTH_HEADER_TITLE = "FCF CURRENT HANDOFF TRUTH - STALE MARKER CLEANUP APPLIED"

CURRENT_TRUTH_HEADER = """# FCF CURRENT HANDOFF TRUTH - STALE MARKER CLEANUP APPLIED

This section is the active current-state authority for this handoff file.

Current completed phase:
CONTROL-CENTER-GLOBAL-SCAN-CLASSIFICATION-GUARD-APP-1 is completed.

Current main state:
- main merge commit: ad16c03
- final handoff sync commit: 8c18573
- validation: python scripts/run_all_checks.py = ALL CHECKS PASSED
- pytest: 1884 passed
- git status: clean
- origin/main: synced

Stale marker rule:
Any older "Approved but not started", "APPROVED NEXT PHASE", "Begin with D1",
"Create sidecar branch", old validation count, or old next-phase candidate below
this section is historical unless explicitly re-approved by the operator.

Current next action:
Architecture gap review or explicitly approved next phase only.

Safety:
paper-only / local-only / read-only / sidecar-only / operator review required.
No P48. No core mutation. No real trading. No broker/exchange API. No API key.
No wallet private key. No buy/sell/order. No tag/release/deploy.

---
"""


TARGET_HANDOFF_PATHS = (
    "docs/FCF_PROJECT_CONTROL_CENTER.md",
    "FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md",
    "FCF_NEW_WINDOW_CHAT_PROMPT.md",
    "docs/HANDOFF_PROMPT.md",
)


def has_current_truth_header(text: str) -> bool:
    return CURRENT_TRUTH_HEADER_TITLE in text


def apply_current_truth_header(text: str) -> str:
    if has_current_truth_header(text):
        return text
    return CURRENT_TRUTH_HEADER + "\n" + text


def cleanup_is_idempotent(text: str) -> bool:
    once = apply_current_truth_header(text)
    twice = apply_current_truth_header(once)
    return once == twice


def historical_content_preserved(original_text: str, updated_text: str) -> bool:
    return original_text in updated_text


def safety_boundary_present(text: str) -> bool:
    required = (
        "paper-only",
        "local-only",
        "sidecar-only",
        "operator review required",
        "No P48",
        "No core mutation",
        "No real trading",
        "No broker/exchange API",
        "No API key",
        "No buy/sell/order",
        "No tag/release/deploy",
    )
    return all(item in text for item in required)
