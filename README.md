# Financial Cognitive Framework

Status: active local paper-only development.
Repository: `wangshaoyuhaha/fcf-spec`.
Canonical control: `docs/FCF_PROJECT_CONTROL_CENTER.md`.

FCF is a local financial research, deterministic analysis, Paper validation,
Shadow observation, governed learning, and read-only Operator Console platform.
BTC was the first implementation line; the architecture now includes equities,
funds, futures, FX, and additional registered market adapters.

## Current Delivered Structure

- exact-loopback Browser Product Console and one-click local operations
- registered-artifact data and evidence gateways
- deterministic multi-market Paper and Shadow validation
- point-in-time evidence, backtesting, outcome, and attribution controls
- governed AI historical evaluation without model invocation
- Champion/Challenger candidates and Operator-gated evolution
- bounded P4 case memory, proposals, scheduling, Shadow, and training governance

## Current Non-Delivered Product Work

- local AI runtime and Dify/model-provider configuration
- live model invocation and Prompt execution
- training execution
- remote or live-market data retrieval
- backend execution of Console action requests
- production deployment and real financial execution

These items are not implied by completed structural contracts.

## Validation

Run `python scripts/run_all_checks.py` and `python -m pytest -q` locally. The
latest authoritative counts are recorded in the current final-state file and
the Project Control Center, not hard-coded in this README.

## Permanent Safety Boundary

- paper-only, local-only, loopback-only, sidecar-only
- registered artifacts and Registered Evidence only
- Deterministic Engine remains calculation authority
- AI remains advisory and explicit Operator review is mandatory
- no credentials, accounts, wallets, balances, positions, orders, or execution
- no tag, release, or deploy without a separate authorized phase

## Local Consoles

Use `START_FCF_BROWSER_CONSOLE.cmd` in the repository root for the current
read-only Browser Product Console on `127.0.0.1:8765`. Keep its terminal open
while using the product pages. See `docs/BROWSER_PRODUCT_CONSOLE_OPERATOR_GUIDE.md`
for preflight, no-browser, and custom registered-artifact options.

Use `operations/windows/FCF Start.cmd`, `FCF Status.cmd`, and `FCF Stop.cmd`
for the separately delivered Stage 9 background lifecycle console on
`127.0.0.1:8775`. That operations surface manages an owned local process; it
does not replace the Browser Product Console product presentation.

Actions on either console remain paper-only and non-executing. Console action
requests create validated receipts unless a later authorized backend-control
phase explicitly implements execution.
