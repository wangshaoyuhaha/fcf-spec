# FCF Current State FCP 0038 A Share Registered Same Calendar Cross Source Coverage Reconciliation App 1 Approved

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

Approved branch:

- `sidecar-fcp-0038-a-share-registered-same-calendar-cross-source-coverage-reconciliation-app-1`

Approved scope:

- require one registered QMT canonical dataset and one independent reference dataset
- require both datasets to target one explicit A-share instrument
- compare both source date sets against the same FCP-0037 registered calendar
- expose per-source missing and unexpected dates without source selection
- reuse FCP-0021 deterministic value and lineage reconciliation
- preserve calendar, dataset, policy, finding, and result hashes
- require Operator review and keep GAP-109 open without real evidence

No data acquisition, calendar scraping, SDK, network retrieval, credential,
provider selection, raw repository retention, realtime activation, product
phase, P48, trading API, account, balance, position, order, execution, tag,
release, or deployment is authorized.
