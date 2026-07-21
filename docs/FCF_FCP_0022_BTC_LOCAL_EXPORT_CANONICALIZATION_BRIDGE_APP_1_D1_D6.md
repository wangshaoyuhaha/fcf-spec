# FCF FCP 0022 BTC Local Export Canonicalization Bridge App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Registered Local Export Contract

The bridge accepts exact Operator-registered local NDJSON bytes with immutable
source identity, SHA-256, byte length, rights, retention, and local-only scope.

## D2 Provider-Neutral Field Profile

A closed immutable mapping isolates provider field names from canonical venue,
instrument, event kind, source sequence, UTC clock, and payload semantics.

## D3 Typed Observation Construction

Trade, book snapshot, book delta, reference-price, and funding rows become the
exact FCP-0018 typed contracts. Missing or invalid evidence fails closed.

## D4 Sequence and Clock Integrity

Positive canonical sequences, previous-sequence ordering, ordered event,
receive, and ingest clocks, book shape, perpetual semantics, and as-of isolation
are inherited from FCP-0018 and are not weakened by the bridge.

## D5 Canonical Replay Artifact

The bridge emits deterministic ASCII NDJSON, a registered canonical artifact,
immutable observation hashes, and a lineage manifest accepted directly by the
FCP-0018 local replay engine.

## D6 Validation and Closeout

Validation order is the isolated FCP-0022 suite, FCP governance targeted suite,
full pytest, `scripts/run_all_checks.py`, generated-output restoration, exact
changed-file verification, and `git diff --check` before merge and closeout.

Validated result:

- FCP-0022 isolated suite: 19 passed
- FCP governance targeted suite: 519 passed
- full pytest: 5835 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: four tracked check outputs restored exactly
