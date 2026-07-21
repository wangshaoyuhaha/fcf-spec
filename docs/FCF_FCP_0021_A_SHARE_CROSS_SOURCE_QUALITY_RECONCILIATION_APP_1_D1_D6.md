# FCF FCP 0021 A-Share Cross-Source Quality Reconciliation App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Registered Dataset Contract

Each input is an immutable registered-local canonical A-share daily dataset.
Dataset identity, source identity, schema, units, rights, retention, as-of time,
observation content, factor lineage, and source-artifact lineage are hashed.

## D2 Compatibility Gates

Only the registered A-share daily schema with CNY price and amount values and
share-denominated volume is accepted. Operator registration and local-only
scope are mandatory. Provider selection and future knowledge fail closed.

## D3 Deterministic Coverage Comparison

The reconciler requires at least two distinct dataset and source identities.
It calculates deterministic union and overlap key sets and emits coverage gaps
without filling, inferring, or selecting records.

## D4 Pairwise Field Findings

All source pairs are compared for raw OHLC, volume, amount, adjustment factor,
factor version, trading status, availability, tradability, revision, and factor
availability clocks. Exact bounded tolerances are policy-controlled.

## D5 Quarantine Review

Any blocking finding produces `QUARANTINE_REVIEW_REQUIRED`. Findings and their
details are immutable registered evidence. The result requires Operator review
and cannot automatically trust or select a source.

## D6 Validation and Closeout

Validation order is the isolated FCP-0021 suite, FCP governance targeted suite,
full pytest, `scripts/run_all_checks.py`, generated-output restoration, exact
changed-file verification, and `git diff --check` before merge and closeout.

Validated result:

- FCP-0021 isolated suite: 31 passed
- FCP governance targeted suite: 500 passed
- full pytest: 5816 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: no tracked output changed; no restoration required
