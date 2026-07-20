# FCF FCP 0017 A-Share Trusted Daily Data Substrate Local Calibration App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

Validated result:

- FCP-0017 isolated suite: 13 passed
- FCP governance targeted suite: 398 passed
- full pytest: 5727 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: no tracked output changed; no restoration required

## D1 Immutable Daily Observation Contract

The substrate accepts exact-value provider-neutral A-share observations. Vendor
SDK objects and binary floating-point values cannot cross the canonical edge.

## D2 Point-in-Time and Trading Status

Event, availability, first-tradable, ingest, and revision clocks are explicit
and monotonic. Future availability or revisions fail closed. Trading,
suspension, and unknown states remain explicit rather than inferred silently.

## D3 Raw and Adjusted Price Views

Raw prices are immutable. Forward-adjusted research prices are derived from an
exact positive factor with a registered version. A missing factor blocks the
research view instead of mutating or guessing historical prices.

## D4 Layered Deterministic Manifests

RAW, NORMALIZED, and RESEARCH manifests retain parent and content SHA-256,
record count, schema, transform, rights, and retention lineage. Identical input
and as-of clocks produce identical results.

## D5 Registered Local Calibration

The loader verifies exact byte length and SHA-256 before parsing an ASCII
canonical CSV. Rights, retention, factor, status, duplicate, order, and
point-in-time failures remain visible and fail closed.

## D6 Validation and Closeout

Validation order is the isolated FCP-0017 suite, FCP governance targeted suite,
full pytest, `scripts/run_all_checks.py`, generated-output restoration, exact
changed-file verification, and `git diff --check`.

BTC data-source implementation remains the explicit successor after this
A-share delivery is completed, merged, and validated.
