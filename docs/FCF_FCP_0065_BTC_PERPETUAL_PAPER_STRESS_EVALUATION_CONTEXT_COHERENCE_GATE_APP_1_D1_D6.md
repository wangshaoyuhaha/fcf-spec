# FCF FCP 0065 BTC Perpetual Paper Stress Evaluation Context Coherence Gate App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Exact Typed Inputs

Consume exact typed FCP-0056, FCP-0062, and FCP-0064 evidence.

## D2 Definition Context

Bind all eight ordered scenario and version identities, definition hashes, and
typed parameter hashes to the FCP-0062 extended-readiness lineage.

## D3 Operand Context

Bind all twelve FCP-0064 operand-observation hashes and exact FCP-0063 schema
ancestry to the same venue, contract, coverage, parameter-domain, and rule
bundle.

## D4 Point-In-Time Coherence

Require scenario registry, extended readiness, operand evidence, and context
as-of times to be monotonic UTC values.

## D5 Immutable Context Evidence

Emit deterministic context-only evidence with no direction, formula,
evaluation, calculation, account-state, or execution authority.

## D6 Validation And Closeout

Run isolated, affected, all-FCP, full-pytest, all-checks, generated-output,
exact-file, ASCII, and diff validation before merge and final synchronization.

Validation evidence before merge:

- isolated FCP-0065 suite: 18 passed
- affected BTC perpetual rule, stress, and governance suite: 376 passed
- all FCP suites: 1182 passed
- full pytest: 6519 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated output restoration: no tracked generated delta

Post-merge validation evidence:

- affected BTC perpetual rule, stress, and governance suite: 376 passed
- full pytest: 6519 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored; no tracked generated changes remained

Evidence commits:

- governance approval: `e6a80484b6c126374cc5deb877bbaf3e6cd6b7f9`
- sidecar delivery: `6683c7a29c05cfdc4a4eb30ae7cd3d8c0299eb56`
- main delivery merge: `a11639efddc6bcb086004bd0925a31be615d3a9c`
