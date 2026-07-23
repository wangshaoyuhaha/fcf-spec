# FCF FCP 0097 Registered Target Label Registry Runtime App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Registered Artifact Boundary

Accept exact Operator-registered ASCII JSON bytes only after byte-length and
SHA-256 verification. Reject unknown fields and unregistered schema versions.

## D2 Existing Foundation Reuse

Delegate forecast-target validation to the frozen V2-R1 target contract and
registry foundation without modifying P1-P47.

## D3 Label Definition Contract

Register immutable label definitions with explicit target reference, maturity,
availability clocks, evidence rule, missing behavior, censoring, and revision
policy. Do not materialize outcome values.

## D4 Bidirectional Lineage

Build deterministic target-to-label and label-to-target indexes. Require every
label to reference a target in the same artifact and every target to have at
least one label definition.

## D5 Fail-Closed Integrity

Reject duplicate target or label references, missing targets, unlabelled
targets, hash mismatches, non-ASCII payloads, schema drift, and authority
escalation.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full pytest, and all-checks suites; restore
generated outputs; audit exact files and `git diff --check`; then commit, push,
merge, revalidate, and synchronize final authority state.

Delivery validation:

- isolated tests: 8 passed
- affected-chain tests: 58 passed
- all-FCP tests: 1856 passed
- full pytest: 7193 passed
- `run_all_checks.py`: passed
