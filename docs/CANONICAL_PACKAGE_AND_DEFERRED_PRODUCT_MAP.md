# Canonical Package and Deferred Product Map

## Canonical Active Surfaces

- `apps/` contains current bounded product and runtime applications
- `src/fcf/` contains established FCF sidecar libraries
- `scripts/` contains local validation and Operator utilities
- `tests/` contains contract, integration, runtime, and control guards
- `docs/FCF_PROJECT_CONTROL_CENTER.md` is the project authority

## Legacy Compatibility Surfaces

The root `app/`, older root `*_app` packages, and `src/btc_finance_platform/`
remain compatibility surfaces. They must receive no new product capability
unless a migration phase explicitly authorizes it. Existing imports are frozen
until incremental migration tests prove removal is safe.

## Explicitly Deferred Product Work

- Dify and model-provider configuration
- live model and Prompt execution
- specialist training execution
- live or remote market-data retrieval
- persistent backend execution of Console actions
- full package consolidation
- public deployment and real financial execution

## Generated Output Policy

- `artifacts/` contains reproducible local smoke outputs and is not canonical
- Dify handoff entries under `artifacts/` are optional generated sources
- tracked runtime and current-state Dify sources remain mandatory
- generated outputs may be deleted after validation
- four tracked runtime outputs are restored byte-for-byte by `run_all_checks.py`

## Legal Decision

No LICENSE file is present. The repository owner must choose the legal license.
Engineering work must not infer legal permission on the owner's behalf.
