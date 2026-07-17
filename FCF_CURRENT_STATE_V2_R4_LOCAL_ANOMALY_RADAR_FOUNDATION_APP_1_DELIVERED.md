# FCF Current State V2 R4 Local Anomaly Radar Foundation App 1 Delivered

Status: VALIDATED_PENDING_MAIN_MERGE

V2-R4 D1-D6 implements a deterministic local registered-artifact anomaly
research Sidecar. It consumes ready V2-R2 historical baselines and immutable
V2-R3 local event envelopes. Transparent gates cover Decimal Z-score, absolute
velocity, consecutive persistence, age, direction, negative evidence,
duplicate, expiry, and cooldown behavior.

Research output is limited to immutable NORMAL, WATCH, CONFIRMED, or DEGRADED
evidence, metadata-only read models, and mandatory Operator acceptance. It is
not a live market feed, universe scanner, licensed provider adapter, model,
official score, prediction, recommendation, alert service, order, or execution
route.

Validation evidence:

- V2-R4 application test file: 9 passed
- V2-R4 application and guard suite: 12 passed
- V2-R4 plus project memory suite: 23 passed
- Browser and Control Center targeted suite: 834 passed, 3 skipped
- full pytest: 4704 passed, 5 skipped
- scripts/run_all_checks.py: ALL CHECKS PASSED
- generated output: 39 files and 11 subdirectories removed
- approval commit: af7f4656fae290a6c2c2186e4e82a2cf5d09adbf

V2-R5 remains planned, not approved, and not started. P1-P47 remain frozen;
no P48. No tag, release, or deployment was run.
