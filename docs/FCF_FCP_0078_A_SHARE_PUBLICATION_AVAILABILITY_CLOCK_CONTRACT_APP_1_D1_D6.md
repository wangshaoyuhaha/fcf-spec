# FCF FCP 0078 A-Share Publication Availability Clock Contract App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Closed Clock Vocabulary

Define exact clock kinds, timestamp precision, evidence state, and revision
state vocabularies for A-share registered artifacts.

## D2 Immutable Publication Clock Record

Bind registered artifact identity, subject identity, publication, legal
availability, retrieval, ingest, first-tradable, revision, and source digest.

## D3 Fail-Closed Time Semantics

Reject impossible ordering, future leakage, implicit timezone conversion,
unknown exact publication time, and date-only timestamps used as exact time.

## D4 Revision And Point-In-Time Selection

Require exact predecessor lineage and select only records whose availability
and revision were observable at the evaluation time.

## D5 Coverage Matrix Evidence Bridge

Register exact tracked implementation SHA-256 as PUBLICATION_CLOCK foundation
evidence for GAP-088 while preserving the Gap and every authority requirement.

## D6 Validation And Closeout

Run isolated, affected-governance, all-FCP, full-pytest, all-checks,
generated-output, exact-file, ASCII, and diff validation before merge and final
synchronization.

Current augmented coverage matrix hash:
`c888687a23536ade9059e16e126d9dba4fa70e14253de772cc04d3ff3613cc9a`

Validation evidence:

- isolated FCP-0078 suite: 31 passed
- affected suite: 119 passed
- all FCP suites: 1535 passed after merge
- full pytest: 6872 passed before and after merge
- `scripts/run_all_checks.py`: ALL CHECKS PASSED before and after merge
- generated runtime outputs: no tracked generated delta
- Windows checkout retained LF and exact matrix hash
- exact changed files and ASCII scope verified
- `git diff --check`: passed

Evidence commits:

- governance approval: `5ad70d1fef720b820b19c5608ec11729e5d568d2`
- sidecar delivery: `3e85e30ed39cc3ee65c392c70b545057546c8c03`
- main delivery merge: `21367595d22859f4b6e2dbe2566235c8ca3cbd4a`
- Windows hash stabilization: `fd2ec78f3d96ee7a9fbf15d478e217b8c0f13354`
