# FCF Current State V2 R7 Local Market Session Registry Foundation App 1 Approved

Status: APPROVED_NOT_STARTED

Business objective:

- register immutable local calendar and market-session definitions
- resolve registered observation times without a network or live clock source

Approved D1-D6 scope:

- D1 closed registered-local calendar and session boundary
- D2 immutable venue, calendar, rule, phase, and analysis-window contracts
- D3 deterministic point-in-time session and window resolution
- D4 overlap, missing, unavailable, expiry, and outside-session blocking
- D5 append-only registry and metadata-only read model
- D6 Operator acceptance, guards, tests, merge, and closeout

Readiness Gate:

- inputs: Operator-registered local calendar definitions and explicit as-of time
- formula: half-open UTC interval resolution with version and effective-time gates
- rights and cost: registered local artifacts only; no external cost
- acceptance: deterministic resolution and canonical SHA-256
- rollback: V2-R7 Sidecar and exact governed files only
- stop: network, live source, system-clock authority, hardcoded venue schedule,
  model, Prompt, learning, execution, unexpected path, or test failure

This is not an exchange calendar service, realtime clock, market-data source,
signal, recommendation, account, order, or execution engine. V2-FR-GAP-048
remains open beyond this bounded foundation.

P1-P47 remain frozen. No P48. No tag, release, or deployment is authorized.
