# FCF FCP 0029 A Share Daily Calibration Result Lineage Coherence Hardening App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Typed Calibration Evidence

Calibration results accept only concrete A-share daily observations and daily
layer manifests.

## D2 Deterministic PIT Observations

Observation keys are unique and ordered, and availability, factor, and
revision clocks do not exceed the result point-in-time boundary.

## D3 Layer Counts and Lineage

RAW, NORMALIZED, and RESEARCH counts, artifact identities, source digests,
content digests, and parent digests agree with the typed observations.

## D4 Result Hash Commitment

The result hash commits to raw and research observation payloads as well as
the manifest evidence and quality state.

## D5 Regression Guard

The dedicated guard verifies synchronized authority evidence, contract
markers, isolated tests, and all-check wiring.

## D6 Validation and Closeout

Validation order is the FCP-0029 isolated suite, affected A-share substrate
and bridge suites, FCP governance stage suite, full pytest,
`scripts/run_all_checks.py`, generated-output restoration, exact changed-file
verification, and `git diff --check`.

Validated result:

- FCP-0029 isolated suite: 11 passed
- affected A-share substrate and bridge suite: 44 passed
- FCP governance stage suite: 617 passed
- project governance suite: 21 passed
- full pytest: 5954 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: final run left no tracked generated changes
