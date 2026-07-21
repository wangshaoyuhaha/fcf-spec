# FCF Current State FCP 0036 Guojin QMT Registered Local Daily Batch Coverage Reconciliation App 1 Delivered

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

Delivered scope:

- exact registration and verification for expected trading-date artifacts
- immutable contiguous QMT batch sequence and source lineage
- deterministic per-batch FCP-0035 normalization
- byte-identical overlap deduplication
- conflicting overlap quarantine without silent row selection
- explicit missing, unexpected, and declared-row-cap findings
- deterministic merged FCP-0019-compatible ASCII bytes and manifest hashes

Tests use synthetic ASCII fixtures only. No real source file is copied into the
repository. No natural-day inference, SDK, network, credential, provider
selection, raw repository retention, realtime, trading, account, balance,
position, order, execution, product, tag, release, or deployment authority is
added.

Validation before merge:

- FCP-0036 isolated suite: 15 passed
- affected QMT bridge and governance suite: 83 passed
- FCP governance stage suite: 712 passed
- full pytest: 6049 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained
