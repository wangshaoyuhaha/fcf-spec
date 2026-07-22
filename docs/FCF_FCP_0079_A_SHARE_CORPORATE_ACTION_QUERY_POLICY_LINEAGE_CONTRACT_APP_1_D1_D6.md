# FCF FCP 0079 A-Share Corporate Action Query Policy Lineage Contract App 1 D1-D6

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

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
