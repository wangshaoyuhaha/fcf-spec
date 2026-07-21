# FCF FCP 0027 Registered Data Primitive Type Integrity Hardening App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Exact BTC Digests

BTC substrate and bridge registrations reject uppercase, padded, byte, and
other nonexact SHA-256 values instead of silently normalizing them.

## D2 Exact Bounded Integers

A-share and BTC registered byte lengths, manifest counts, source sequences,
previous sequences, and schema versions require non-boolean integers.

## D3 Exact Closed Booleans

A-share and BTC local bridge storage and provider-selection flags require
exact false identities. False-like strings and integers cannot cross the
authority boundary.

## D4 Compatibility

Exact registered values retain their prior canonical hashes, bridge outputs,
provider-neutral behavior, market isolation, and mandatory Operator review.

## D5 Regression Guard

The dedicated guard verifies synchronized approval, delivery evidence,
primitive contract markers, tests, and all-check wiring.

## D6 Validation and Closeout

Validation order is the FCP-0027 isolated suite, affected A-share and BTC
substrate and bridge suites, FCP governance target suite, full pytest,
`scripts/run_all_checks.py`, generated-output restoration, exact changed-file
verification, and `git diff --check`.

Validated result:

- FCP-0027 isolated suite: 25 passed
- affected A-share and BTC substrate and bridge suite: 93 passed
- FCP governance stage suite: 591 passed
- project governance suite: 21 passed
- full pytest: 5928 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: final run left no tracked generated changes
