# System Integrity and Product Hardening Stage 13 D1-D6

Status: DELIVERY_VALIDATED_PENDING_MERGE

## D1 Evidence and Backtest Integrity

- reject unknown, duplicate, late, or availability-misaligned evidence
- reject non-finite numeric payloads and non-UTC audit times
- provide immutable data-source, calendar, corporate-action, config,
  benchmark, outcome-label, result, and attribution registries
- bind every P0-P3 capability identity to a callable implementation
- separate bias and walk-forward validators from the backtest engine
- build registered outcome and attribution records from backtest results

## D2 P4 Governance Integrity

- require complete registered-artifact containment for case retrieval
- require training-result evidence to belong to the approved plan
- declare every Challenger change variable
- require registered schedule dependencies
- report signed error, absolute error, and direction accuracy
- bind every P4 capability identity to a callable implementation

## D3 Web Console Security and Semantics

- require registered Operator identity for control receipts
- require same-origin HTTP POST requests
- add anti-framing, restrictive CSP nonces, and permissions controls
- require approved URL hosts for local read-only intake
- identify Console actions as validation and attestation receipts only

## D4 Active Surface and Documentation

- replace stale top-level product identity and progress claims
- identify canonical and legacy compatibility package surfaces
- pin the active development dependency
- add project metadata and security reporting guidance
- replace the P14 regime stub with a validated deterministic classifier
- delete one proven duplicate document

## D5 Generated Output and Clean Clone Reliability

- isolate pytest temporary files outside the repository
- restore four tracked runtime outputs byte-for-byte after all checks
- classify generated Dify artifact sources as optional and reproducible
- retain tracked Dify runtime and current-state sources as mandatory
- remove ignored artifacts and Python or pytest caches after validation
- exercise the symlink rejection branch without Windows symlink privilege

## D6 Validation

- independent remediation suite: 13 passed
- targeted suite: 493 passed, 2 skipped
- full pytest: 4621 passed, 5 skipped
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated tracked outputs: restored with no diff
- ignored generated outputs and caches: removed
- `git diff --check`: passed before delivery commit

## Deferred Work

- Dify and model-provider configuration
- live model and Prompt execution
- specialist training execution
- live or remote market-data retrieval
- persistent backend execution of Console actions
- full legacy package migration
- repository owner LICENSE selection
- public deployment and real financial execution

Deferred work is explicit product backlog, not delivered capability. Permanent
paper-only, local-only, loopback-only, sidecar-only, registered-artifact-only,
read-only presentation, deterministic-authority, evidence-authority, advisory
AI, and mandatory Operator review boundaries remain unchanged. P1-P47 remain
frozen; no P48. No tag, release, or deploy was run.
