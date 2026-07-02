# FCF Final Archive Operator Quickstart

Date: 2026-07-02 11:33:53 +0800

Project: FCF / fcf-spec  
Repository: https://github.com/wangshaoyuhaha/fcf-spec.git  
Branch: main  
Mode: final archived, maintenance-only, paper-only

## Purpose

This document gives a short operator quickstart for future maintenance after Final Archive D7.

The main project line is already closed.

This file does not open a new Phase.

## Current State

- Phase 1 through Phase 12 completed
- Final Archive D1 through D7 completed
- Archive-D7 final archive closeout completed
- Final archive acceptance smoke completed
- Final archive export summary completed
- Latest verified full test result: 773 passed

## Normal Maintenance Check

Use these commands after any future maintenance edit:

```bash
python main.py
python scripts/run_p12_final_delivery_package_summary.py
python scripts/run_final_archive_acceptance_smoke.py
python -m pytest -q
```

Expected result:

- runtime check completes
- P12 final delivery package summary completes
- final archive acceptance smoke completes
- full test suite passes

## Required Commit Rule

After any future successful maintenance change:

```bash
git status --short
git add <changed-files>
git commit -m "<short maintenance message>"
git push origin main
```

Do not rewrite history.

Do not amend old archive commits.

Use a new commit for every maintenance change.

## Safe Boundary Reminder

The project remains paper-only.

The operator must not:

- connect real exchange APIs
- store real API keys
- read wallet private keys
- place real orders
- read real account balances
- read real positions
- claim real execution success
- claim real financial impact
- configure CI secrets
- deploy to production
- enable live auto-trading
- bypass operator review
- bypass policy checks
- bypass risk checks
- bypass safe_boundary checks
- interpret paper-only passed as a real trading signal
- interpret paper-only passed as a real fill or execution

## If A Future Check Fails

Do not expand the project.

Do not open a new Phase.

Only perform the minimum fix needed to restore:

- paper-only behavior
- operator review requirement
- safe_boundary preservation
- archive consistency
- passing validation

Then rerun the required validation commands and commit the fix.
