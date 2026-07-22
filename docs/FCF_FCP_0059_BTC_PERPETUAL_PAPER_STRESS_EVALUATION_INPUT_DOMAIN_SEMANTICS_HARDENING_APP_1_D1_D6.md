# FCF FCP 0059 BTC Perpetual Paper Stress Evaluation Input Domain Semantics Hardening App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Exact FCP-0058 Registry

Consume one exact immutable FCP-0058 BTC perpetual Paper stress-evaluation
input registry and preserve its coverage, contract, venue, and observation
lineage.

## D2 Signed Funding Domain

Permit finite negative, zero, or positive funding-reference rates without
binary-float coercion or sign inference.

## D3 Metric-Specific Domains

Require positive market price, depth-notional, and collateral-index references;
bounded liquidation-distance ratios; and nonnegative integral counts and
seconds.

## D4 Fail-Closed Validation

Reject invalid signs, zero positive references, out-of-range distance ratios,
fractional count or seconds, non-finite values, binary floats, untyped
registries, and authority escalation.

## D5 Immutable Domain Snapshot

Preserve deterministic registry, coverage, observation, domain-schema, and
snapshot hashes with mandatory Operator review and validation-only authority.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0059 suite: 25 passed
- affected BTC stress-domain and governance suite: 566 passed
- all FCP suites: 1057 passed
- full pytest: 6394 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated output restoration: no tracked generated delta

Synthetic fixtures do not close GAP-098, GAP-099, GAP-100, or GAP-101 and grant
no acquisition, SDK, network, credential, realtime, exchange, wallet, account,
balance, position, order, execution, product, P48, tag, release, or deployment
authority.
