# FCF Current State V2 R2 Historical Factor Baseline App 1 Approved

Status: APPROVED_NOT_STARTED

Approved branch:

- `sidecar-v2-r2-historical-factor-baseline-app-1`

Business objective and horizon:

- build deterministic historical baseline foundations for daily or explicitly
  declared observation frequencies
- accept only Operator-supplied registered local artifacts
- preserve point-in-time availability and block forward information

Exact input and rights contract:

- instrument, event time, available time, field, value, quality, source, and
  registered artifact identity
- explicit timezone, calendar, adjustment, missing, duplicate, suspension,
  retention, permitted-use, and license declarations
- source type is local registered artifact only; network and purchase cost are
  zero for this phase

Exact deterministic formulas:

- arithmetic mean: sum(x) / n
- population variance: sum((x - mean)^2) / n
- population standard deviation: sqrt(variance)
- z-score: (x - mean) / standard deviation, with ZERO_VARIANCE abstention
- deterministic nearest-rank quantiles over an ordered historical window
- no prediction target or outcome label is produced by this baseline phase

Delivery order:

- D1 immutable historical observation, rights, and boundary contracts
- D2 point-in-time dataset validation and chronological registry
- D3 deterministic rolling baseline statistics and abstention
- D4 walk-forward split, leakage guard, and replay identity
- D5 immutable read-only presentation and Operator acceptance
- D6 guards, tests, validation, merge, and authority synchronization

Failure, test, rollback, and stop rules:

- reject unregistered artifacts, unsafe identities, rights denial, time travel,
  duplicates, invalid decimals, insufficient history, and unsafe policies
- property, determinism, PIT, leakage, replay, immutability, and authority tests
- rollback is limited to the V2-R2 Sidecar and exact governed files
- stop on any network, credential, model, Prompt, factor activation, scoring,
  candidate ranking, order, execution, or unexpected changed path

Acceptance requires deterministic repeated results, no future observation in a
baseline, explicit abstention, immutable read-only output, full validation, and
mandatory Operator review. Standard-library Decimal work has no external
compute or data cost.

This approval does not select an MVP market, data vendor, Champion factor, or
forecast target. It does not close production data, complete indicator-library,
normalization-research, or model-validation gaps.

P1-P47 remain frozen. No P48 is created. Paper-only, local-only,
loopback-only, sidecar-only, registered-artifact-only, read-only presentation,
Deterministic Engine calculation authority, Registered Evidence authority,
advisory AI, and mandatory Operator review remain binding.

No broker, exchange, credential, account, balance, position, wallet, order,
real execution, tag, release, or deployment path is authorized.
