# FCF FCP 0026 Registered Data Authority Exactness Hardening App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Digest Exactness

A-share, BTC, and readiness contracts reject uppercase, padded, byte, or other
nonexact SHA-256 inputs instead of silently normalizing them.

## D2 Count Exactness

A-share and BTC reconciliation union and overlap counts require non-boolean
nonnegative integers with overlap bounded by union.

## D3 Boolean Exactness

Registration, provider-selection, source-selection, and review boundaries use
exact boolean identities so false-like integers cannot bypass policy.

## D4 Authority Identity

BTC results and cross-market packets require Deterministic Engine calculation,
Registered Evidence authority, and advisory-only AI identity.

## D5 Compatibility

Exact registered inputs preserve existing deterministic hashes, market
isolation, quality states, and mandatory Operator review behavior.

## D6 Validation and Closeout

Validation order is the FCP-0026 isolated suite, affected A-share/BTC/readiness
regression suite, FCP governance target suite, full pytest,
`scripts/run_all_checks.py`, generated-output restoration, exact changed-file
verification, and `git diff --check`.

Validated result:

- FCP-0026 isolated suite: 22 passed
- affected A-share, BTC, and readiness regression suite: 90 passed
- FCP governance stage suite: 566 passed
- project governance suite: 21 passed
- full pytest: 5903 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: four tracked check outputs restored exactly
