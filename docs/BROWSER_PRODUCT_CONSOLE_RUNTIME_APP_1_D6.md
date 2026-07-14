# BROWSER-PRODUCT-CONSOLE-RUNTIME-APP-1 D6

## Status

IMPLEMENTED_VALIDATED_READY_FOR_MAIN_MERGE

## Scope

D6 completes final runtime integration, explicit Operator launch, acceptance,
and sidecar closeout.

Delivered integration:

- explicit local launcher
- fixed host 127.0.0.1
- no server autostart
- registered artifact index loading
- SHA-256 artifact verification
- deterministic read-model construction
- loopback HTTP server creation
- browser health endpoint
- stock candidate workspace
- score breakdown, reason code, and risk flag presentation
- Paper Validation and Shadow Observation presentation
- Operator review and report presentation
- governed Operator review commands
- deterministic receipt, audit, and manifest bundles
- exact idempotent reuse
- tamper, collision, and incomplete-bundle rejection
- machine-readable final acceptance state

Explicit launch command:

```text
python scripts/run_browser_product_console_runtime.py --allowed-root <LOCAL_ROOT> --index <INDEX_JSON> --port 8765
```

The launcher is Operator-triggered and blocking. Importing or building the
runtime does not start a server.

## Validation baseline

- targeted suite: 36 passed
- full pytest: 3800 passed
- scripts/run_all_checks.py: PASSED
- generated runtime outputs restored
- sidecar branch clean and synchronized

## Permanent restrictions

- P1-P47 frozen
- no P48
- paper-only
- local-only
- loopback-only
- sidecar-only
- registered-artifact-only
- Operator review required
- Deterministic Engine authority preserved
- AI advisory only
- no public network exposure
- no broker or exchange connection
- no credentials
- no account, balance, position, or wallet access
- no order path
- no real execution
- no automatic approval
- no automatic promotion
- no automatic baseline replacement
- no automatic learning activation
- no automatic archive
- no tag
- no release
- no deployment

## Next step

Merge the completed sidecar into main, validate main, push, and synchronize
the final authority state.
