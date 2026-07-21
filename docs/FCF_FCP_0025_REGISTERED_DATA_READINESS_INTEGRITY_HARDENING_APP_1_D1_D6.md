# FCF FCP 0025 Registered Data Readiness Integrity Hardening App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Digest Lineage

BTC reconciliation results and readiness rows now require exact lowercase
SHA-256 result, policy, and dataset lineage.

## D2 Typed Evidence

BTC result findings and cross-market packet rows must use their registered typed
contracts. Untyped values fail closed with controlled validation errors.

## D3 Count Integrity

Readiness counts must be non-boolean nonnegative integers and dataset hashes
must be distinct.

## D4 Venue Semantics

Different BTC `venue_semantics_id` values create explicit blocking quarantine
evidence even when event payloads otherwise match.

## D5 Decimal Errors

Invalid policy decimals are normalized to controlled `ValueError` failures.

## D6 Validation and Closeout

Validation order is the isolated FCP-0025 suite, affected regression suite,
FCP governance targeted suite, full pytest, `scripts/run_all_checks.py`, output
restoration, exact changed-file verification, and `git diff --check`.

Validated result:

- FCP-0025 isolated suite: 15 passed
- affected FCP-0023 and FCP-0024 regression suite: 31 passed
- FCP governance targeted suite: 565 passed
- full pytest: 5881 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: four tracked check outputs restored exactly
