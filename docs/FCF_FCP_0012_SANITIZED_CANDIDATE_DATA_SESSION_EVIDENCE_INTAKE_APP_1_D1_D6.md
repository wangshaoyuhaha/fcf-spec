# FCF FCP 0012 Sanitized Candidate Data Session Evidence Intake App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Closed Registered Artifact Boundary

The sidecar accepts one exact registered local sanitized artifact. Credentials,
account identifiers, raw market values, provider selection, entitlement approval,
realtime activation, and trading or execution authority are forbidden.

## D2 Exact Bounded JSON Loader

The ASCII JSON loader verifies the exact byte length and SHA-256, rejects duplicate
or unregistered fields, rejects secret-bearing key names, enforces bounded integer
and UTC/date values, and preserves the source digest without copying or rewriting
the artifact.

## D3 Sanitized Session Evidence

The closed evidence fields are candidate identity, capture time, license class,
remaining days, quota limit and use, and one bounded read-only probe summary. The
artifact contains no price, volume, account, credential, or executable request.

## D4 FCP-0011 Gap Composition

The session review composes the existing candidate profile and keeps every
documentary and canonical TICK, MINUTE_BAR, and ORDER_BOOK gap explicit. A
successful local observation does not prove rights, retention, lineage, realtime
availability, or product readiness. External activation is always BLOCKED.

## D5 Read-Only Browser Review

`/data-source-session-evidence` supports GET and HEAD only. Simplified Chinese is
the default and English remains explicit. No form, button, script, upload, secret
input, write, approval, trading, or execution control is present.

## D6 Validation And Closeout Boundary

Validation order is the FCP-0012 isolated suite, related FCP-0001/FCP-0009 through
FCP-0011 and browser targeted suite, full pytest, `scripts/run_all_checks.py`,
generated-output restoration, exact changed-file verification, and
`git diff --check`.

The delivery cannot call a provider, accept credentials, approve entitlement,
select RQData, close a referenced gap, claim realtime readiness, start a product
phase, create P48, or enable execution.
