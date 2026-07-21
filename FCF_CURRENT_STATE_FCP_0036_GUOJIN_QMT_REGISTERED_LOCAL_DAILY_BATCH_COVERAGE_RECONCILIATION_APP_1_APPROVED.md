# FCF Current State FCP 0036 Guojin QMT Registered Local Daily Batch Coverage Reconciliation App 1 Approved

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

Approved branch:

- `sidecar-fcp-0036-guojin-qmt-registered-local-daily-batch-coverage-reconciliation-app-1`

Approved scope:

- accept multiple exact Operator-registered QMT daily export batches
- require stable ordered batch registrations and explicit instrument identity
- require a registered expected trading-date set for completeness claims
- deduplicate byte-equivalent overlaps and quarantine conflicting overlaps
- expose missing, unexpected, truncated, and row-cap coverage findings
- emit deterministic merged ASCII bytes and immutable reconciliation lineage
- remain compatible with FCP-0019 and FCP-0035 authority contracts

No natural-day trading-calendar inference, SDK, network retrieval, credential,
provider selection, raw repository retention, realtime activation, product
phase, P48, trading API, account, balance, position, order, execution, tag,
release, or deployment is authorized.
