# FCF FCP 0079 A-Share Corporate Action Query Policy Lineage Contract App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Closed Corporate Action Vocabulary

Define exact supported action, precision, query-view, factor-source, and
revision-state vocabularies for registered A-share price lineage.

## D2 Immutable Corporate Action Revision

Bind instrument, action identity, source artifact, publication and effective
dates, action payload digest, revision identity, and predecessor lineage.

## D3 Adjustment Factor Revision Lineage

Bind each exact adjustment factor to one registered action revision set,
factor version, availability clock, source digest, and predecessor revision.

## D4 Point-In-Time Query Policy

Resolve RAW or FORWARD_ADJUSTED views only under one explicit immutable query
policy and only from revisions observable at the query as-of time.

## D5 Coverage Matrix Evidence Bridge

Register exact tracked implementation SHA-256 values as
CORPORATE_ACTION_LINEAGE and QUERY_POLICY_LINEAGE foundation evidence while
preserving the Gap and every authority requirement.

## D6 Validation And Closeout

Run isolated, affected-governance, all-FCP, full-pytest, all-checks,
generated-output, exact-file, ASCII, and diff validation before merge and final
synchronization.

Current augmented coverage matrix hash:
`a522a720a7115b59a8146e675c5e9c26892a98f07b3f5f4557949d834b5b0e08`

Validation evidence before delivery commit:

- isolated FCP-0079 suite: 36 passed
- affected suite: 125 passed
- all FCP suites: 1571 passed
- full pytest: 6908 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: no tracked generated delta
- exact changed files and ASCII scope verified before commit
- `git diff --check`: required before commit

Evidence commits:

- governance approval: `218293bf7251b5371b8251d4c62f16a1bf5a22b3`
- sidecar delivery: `0e8dea760f4614c398a6d541f2a774cb20eacc92`
- main delivery merge: `ba443252713cbbeca827c63758699ecf7cb8eb91`
