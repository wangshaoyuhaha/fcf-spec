# FCF Current State FCP 0035 Guojin QMT Registered Local Daily Export Profile App 1 Delivered

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

Registered external evidence observed on 2026-07-21:

- raw local export SHA-256: `4c61b151c7dda4d321d1bbf6143d9cde2dec7db593f90d14a47fa79ac15e8da6`
- front reference SHA-256: `ca509e505f9df82812ee822de72726149a9df878b0ca6e47504a5818d4686c6c`
- exact source columns: `timetag,open,high,low,close,volumn,amount`
- observed row count: 500
- observed date range: 2024-06-28 through 2026-07-21
- requested date range: 2021-01-01 through 2026-07-21
- price-different rows: 476
- volume-different rows: 0
- amount-different rows: 0
- observed additive-offset boundaries: 2024-07-16, 2024-09-13,
  2025-06-18, 2025-09-12, and 2026-06-17

Delivered scope:

- immutable exact-byte registration and validation
- explicit A-share instrument identity
- deterministic date and 100-share lot normalization
- exact FCP-0019 bridge-compatible ASCII bytes
- requested-range mismatch findings
- additive front-adjustment reference without factor authority
- fail-closed factor, status, and point-in-time findings

The real export bytes remain outside the repository. Tests use synthetic ASCII
fixtures only. No SDK, network, credential, provider selection, raw repository
retention, realtime, trading, order, execution, product, tag, release, or
deployment authority is added.

Validation before merge:

- FCP-0035 isolated suite: 18 passed
- affected A-share bridge and governance suite: 81 passed
- FCP governance stage suite: 697 passed
- full pytest: 6034 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained
