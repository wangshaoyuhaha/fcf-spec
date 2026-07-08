# SIDECAR-DAG-DEPENDENCY-GUARD-APP-1 D3 Policy Matrix Repair

## Purpose

D3 repairs the default sidecar dependency graph introduced in D2.

The D2 default graph incorrectly treated REPORT-ARCHIVE-APP-1 as data_foundation.

REPORT-ARCHIVE-APP-1 is an archive_audit sidecar because it receives completed review and report artifacts.

## Repair

Before:

REPORT-ARCHIVE-APP-1 = data_foundation

After:

REPORT-ARCHIVE-APP-1 = archive_audit

## Reason

OPERATOR-REVIEW-APP-1 may hand off completed paper review artifacts to REPORT-ARCHIVE-APP-1.

That is a forward dependency:

governance_review -> archive_audit

It is not a reverse dependency.

## Safety Boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no source mutation
- no source deletion
- no source overwrite
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
- no real trading
- no real execution
- no broker API
- no exchange API
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy
