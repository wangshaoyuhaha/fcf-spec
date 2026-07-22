# FCF FCP 0074 BTC Perpetual Paper Signal Evidence Separation Contract App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Closed Domain Vocabulary

Register the exact ordered domains for reusable market signal, contract,
leverage-margin, cost-funding, liquidation-risk, and outcome-accounting evidence.

## D2 Immutable Registered References

Bind safe artifact identity, SHA-256 digest, explicit domain, observation UTC,
and deterministic reference hash without raw-provider or network access.

## D3 Complete Separation Manifest

Require every closed domain in order, unique artifact identity and digest, and
an exact reusable versus derivative-specific hash partition.

## D4 Fail-Closed Validation

Reject untyped, missing, duplicate, reordered, unknown-domain, time-regressed,
unregistered, or authority-escalated evidence.

## D5 Non-Authorizing Contract

Emit immutable local Paper separation evidence without signal calculation,
factor promotion, strategy selection, profitability claim, or account action.

## D6 Validation And Closeout

Run isolated, all-FCP, full-pytest, all-checks, generated-output, exact-file,
ASCII, and diff validation before merge and final synchronization.

Validation evidence:

- isolated FCP-0074 suite: 32 passed
- all FCP suites: 1430 passed before and after merge
- full pytest: 6767 passed before and after merge
- `scripts/run_all_checks.py`: ALL CHECKS PASSED before and after merge
- generated runtime outputs: no tracked generated delta
- exact changed files and ASCII scope verified
- `git diff --check`: passed

Evidence commits:

- governance approval: `6206a9bdf6be065794b165542ec1f4484516880f`
- sidecar delivery: `3026a53b682082641166e162f15d274a9e23b78c`
- main delivery merge: `ae8b03b9b6156f06ddc1a26f6d08f8cc6cf4cf5a`
