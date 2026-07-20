# FCF FCP 0018 BTC Trusted Market Data Substrate Local Replay App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Immutable BTC Market Contracts

Provider-neutral immutable records preserve exact Decimal values, venue and
instrument identity, instrument kind, observation kind, source sequence, event
time, receive time, ingest time, schema version, registered artifact lineage,
and deterministic hashes. Trade, L2 book, reference-price, and funding records
remain distinct typed contracts.

## D2 L2 Sequence and Resynchronization

A registered book snapshot starts or restores a synchronization generation.
Deltas must name the exact preceding sequence and advance by one. A gap,
delta-before-snapshot, empty book, or crossed book fails closed. The last valid
book is frozen and further deltas are ignored until a later registered snapshot
creates a new generation.

## D3 Perpetual Reference and Funding Semantics

Mark price, index price, and signed funding rate remain exact and separately
traceable. Reference-price and funding records are valid only for perpetual
instruments. Spot instruments do not inherit perpetual funding semantics.

## D4 Continuous-Market Quality Findings

BTC freshness is evaluated continuously against UTC event streams without an
A-share session calendar, suspension flag, or corporate-action adjustment
rule. Missing required streams, stale streams, and excessive mark/index
divergence create blocking findings with mandatory Operator review.

## D5 Registered Local Replay Evidence

Replay accepts exact bytes only after byte-length, ASCII, SHA-256, local-rights,
artifact identity, venue identity, and instrument identity checks. The replay
manifest hashes the registered artifact, accepted observations, final book
state, and replay time. No provider SDK or network path exists.

## D6 Validation and Closeout

Validation order is the isolated FCP-0018 suite, FCP governance targeted suite,
full pytest, `scripts/run_all_checks.py`, generated-output restoration, exact
changed-file verification, and `git diff --check`. Merge and final authority
synchronization occur only after every validation passes.

Validated result:

- FCP-0018 isolated suite: 16 passed
- FCP governance targeted suite: 427 passed
- full pytest: 5743 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: no tracked output changed; no restoration required
