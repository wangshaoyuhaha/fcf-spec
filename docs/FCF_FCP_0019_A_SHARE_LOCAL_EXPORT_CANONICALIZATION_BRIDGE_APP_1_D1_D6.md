# FCF FCP 0019 A-Share Local Export Canonicalization Bridge App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Registered Local Export Contract

The bridge accepts exact Operator-registered local bytes with bounded length,
SHA-256, source identity, registration time, usage scope, rights state, and
retention state. Registration cannot select a provider or authorize raw
repository storage.

## D2 Closed Field Profile

An immutable provider-neutral profile maps an exact source header to the closed
daily price schema. It supports canonical A-share identifiers or explicit code
and exchange fields. The bridge accepts only UTF-8 comma-delimited local
exports and records a deterministic profile hash.

## D3 Point-in-Time Supplements

Every source row requires an exact instrument and trade-date supplement with
event, availability, first-tradable, ingest, and revision clocks. Adjustment
factor version and availability, plus observed trading status, are explicit.
The bridge never fabricates unavailable clocks, factor lineage, or status.

## D4 Canonicalization and Lineage

Source bytes are verified before parsing. Rows are validated with the FCP-0017
observation contract, deterministically sorted, and emitted as the exact
17-column ASCII CSV accepted by the trusted A-share daily calibrator. The
manifest binds source, profile, supplement set, canonical bytes, warnings, and
row count by hash.

## D5 Fail-Closed Quality State

Invalid bytes, headers, instruments, duplicates, supplements, clocks, or future
revisions are rejected. Unresolved rights or retention, missing adjustment
factors, and unknown trading status remain visible blocking findings. Operator
review is mandatory.

## D6 Validation and Closeout

Validation order is the isolated FCP-0019 suite, FCP governance targeted suite,
full pytest, `scripts/run_all_checks.py`, generated-output restoration, exact
changed-file verification, and `git diff --check`. Merge and final authority
synchronization occur only after every validation passes.

Validated result:

- FCP-0019 isolated suite: 20 passed
- FCP governance targeted suite: 447 passed
- full pytest: 5763 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: no tracked output changed; no restoration required
