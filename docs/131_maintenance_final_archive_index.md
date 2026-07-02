# FCF Final Archive Index

Date: 2026-07-02 11:53:15 +0800

Project: FCF / fcf-spec
Repository: https://github.com/wangshaoyuhaha/fcf-spec.git
Branch: main
Mode: final archived, maintenance-only, paper-only

## Purpose

This document is a quick index for the final archive and post-archive maintenance records.

It does not open a new Phase.

## Final Archive Bridge And Archive Records

- docs/120_p12_to_final_archive_bridge_plan.md
- docs/121_archive_d1_final_archive_plan.md
- docs/122_archive_d2_immutable_delivery_snapshot_checklist.md
- docs/123_archive_d3_final_release_note.md
- docs/124_archive_d4_final_archive_manifest.md
- docs/125_archive_d5_final_operator_archive_handoff.md
- docs/126_archive_d6_final_archive_acceptance_smoke.md
- docs/127_archive_d7_final_archive_closeout.md

## Post-Archive Maintenance Records

- docs/128_maintenance_final_archive_health_check.md
- docs/129_maintenance_final_archive_export_summary.md
- docs/130_maintenance_operator_quickstart.md
- docs/131_maintenance_final_archive_index.md

## Latest Verified State

- Phase 1 through Phase 12 completed
- Final Archive D1 through D7 completed
- Final Archive D7 closeout completed
- Final archive acceptance smoke completed
- Latest verified full test result: 773 passed
- paper-only safe_boundary preserved
- operator_review_required = true
- bypass_operator_review = false
- bypass_policy_risk_safe_boundary = false

## Required Validation Commands

After any future maintenance change, run:

- python main.py
- python scripts/run_p12_final_delivery_package_summary.py
- python scripts/run_final_archive_acceptance_smoke.py
- python -m pytest -q

## Maintenance Rule

Future work should stay limited to:

- bug fixes
- documentation improvements
- archive checks
- maintenance summaries
- safe-boundary-preserving validation

Do not open a new Phase unless explicitly required.

Do not rewrite history.

Use a new commit for every maintenance change.

## Safe Boundary

This project remains paper-only.

Do not connect real exchange APIs, store real API keys, read wallet private keys, place real orders, read real balances, read real positions, claim real execution success, claim real financial impact, configure CI secrets, deploy to production, auto-trade live capital, bypass operator review, bypass policy checks, bypass risk checks, or bypass safe_boundary checks.
