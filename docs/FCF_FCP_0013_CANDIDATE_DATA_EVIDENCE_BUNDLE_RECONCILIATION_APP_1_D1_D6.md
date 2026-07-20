# FCF FCP 0013 Candidate Data Evidence Bundle Reconciliation App 1 D1-D6

Status: VALIDATED_PENDING_MERGE

## D1 Closed Evidence Bundle Boundary

The sidecar is paper-only, local-only, loopback-only, registered-artifact-only,
read-only, and Operator-reviewed. Network access, credentials, raw provider
bytes, provider selection, entitlement approval, gap closure, product phase
authorization, and trading or execution authority are forbidden.

## D2 Exact Registered Evidence Loading

The loader accepts one exact ASCII JSON bundle registry, rejects duplicate or
unknown keys, and verifies the canonical JSON SHA-256 of both referenced
registries. It binds exactly the registered FCP-0007 daily Demo schema evidence
and FCP-0012 sanitized trial-session evidence. It does not require or copy the
raw provider Demo CSV.

## D3 Deterministic Reconciliation

The reconciliation verifies candidate identity, evidence identity, source
lineage, evidence kinds, observed capabilities, observation windows, and
conflict codes. Non-overlapping observation windows are context, not hidden
conflict or false continuity.

## D4 Readiness Delta And Preserved Gaps

The result is always `EVIDENCE_EXPANDED_NOT_READY`. Canonical TICK, MINUTE_BAR,
and ORDER_BOOK gaps remain explicit, together with commercial entitlement,
retention rights, provider selection, and realtime coverage evidence.
External activation is always BLOCKED and provider selection remains UNSELECTED.

## D5 Read-Only Browser Review

`/data-source-evidence-bundle` supports GET and HEAD only. Simplified Chinese is
the default and English remains explicit. No form, button, script, upload,
secret input, write, approval, provider activation, trading, or execution
control is present.

## D6 Validation And Closeout Boundary

Validation order is the isolated FCP-0013 suite, related FCP-0007 and FCP-0011
through FCP-0013 plus browser targeted suite, full pytest,
`scripts/run_all_checks.py`, generated-output restoration, exact changed-file
verification, and `git diff --check`.

The delivery cannot call a provider, accept credentials, approve entitlement,
select RQData, close a referenced gap, claim realtime readiness, start a product
phase, create P48, or enable execution.

Validated result:

- FCP-0013 isolated suite: 28 passed
- related evidence, localization, and browser suite: 551 passed
- full pytest: 5678 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: no tracked output changed; no restoration required
