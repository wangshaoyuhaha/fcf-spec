# FCF FCP 0096 Registered Factor Registry Runtime App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Registered Artifact Boundary

Accept exact Operator-registered ASCII JSON bytes only after byte-length and
SHA-256 verification. Reject unknown fields and unregistered schema versions.

## D2 Existing Foundation Reuse

Delegate factor-definition validation and registry coherence to the frozen
V2-R11 local factor registry foundation without modifying P1-P47.

## D3 Read-Only Runtime Snapshot

Build immutable record-hash, dependency, reverse-dependency, and deterministic
topological-order views. No calculation, scoring, or promotion is activated.

## D4 Lifecycle And Retirement

Require explicit retirement time, registered replacement references, and
deterministic transitive invalidation from retired dependencies.

## D5 Fail-Closed Integrity

Reject duplicate keys, missing dependencies, cycles, missing replacements,
hash mismatches, schema drift, and authority escalation.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full pytest, and all-checks suites; restore
generated outputs; audit exact files and `git diff --check`; then commit, push,
merge, revalidate, and synchronize final authority state.
