# FCF Current State V2 R4 Local Anomaly Radar Foundation App 1 Approved

Status: APPROVED_NOT_STARTED

Approved branch:

- `sidecar-v2-r4-local-anomaly-radar-foundation-app-1`

Business objective and horizon:

- establish transparent local anomaly research before any live market scan
- evaluate registered event windows against registered historical baselines
- produce event-level research states without prediction or recommendation

Approved D1-D6 scope:

- D1 closed boundary and versioned context-specific anomaly rule
- D2 numeric projection from immutable V2-R3 local registered events
- D3 deterministic Z-score, velocity, persistence, age, and direction gates
- D4 NORMAL, WATCH, CONFIRMED, and DEGRADED research-state evidence
- D5 immutable duplicate, expiry, cooldown, and negative-evidence ledger
- D6 read-only presentation, Operator acceptance, guard, tests, and closeout

Readiness Gate:

- inputs: V2-R2 ready historical baseline and V2-R3 local event envelopes
- rights and cost: inherited registered-local-artifact rights; no external cost
- formulas: Decimal Z-score from the registered baseline and absolute value
  change divided by positive event-time seconds
- thresholds: Operator-authored, versioned, context-bound research metadata;
  no permanent global threshold and no automatic tuning
- target label: NONE; states describe current local research evidence only
- failure behavior: abstain or degrade on insufficient or zero-variance
  baseline, field mismatch, unsafe numeric type, stale event, time inversion,
  noncontiguous stream, missing persistence, negative evidence, or cooldown
- acceptance: deterministic state and evidence hash with no silent mutation
- rollback: new V2-R4 Sidecar and exact governed files only
- stop conditions: live source, market scan, provider, credential, model,
  official score, ranking, prediction, automatic learning, order, execution,
  unexpected path, safety failure, or test failure

This phase does not implement a universe scanner, live anomaly radar, first
market adapter, realtime source, order book, alert service, official factor,
recommendation, prediction, model, Prompt, automatic learning, Paper order,
virtual account, or execution route. V2-FR-GAP-026 and the production parts of
V2-FR-GAP-027, V2-FR-GAP-058, and V2-FR-GAP-059 remain open.

P1-P47 remain frozen. No P48 is created. Paper-only, local-only,
loopback-only, sidecar-only, registered-artifact-only, read-only presentation,
Deterministic Engine calculation authority, Registered Evidence authority,
advisory AI, and mandatory Operator review remain binding.

No broker, exchange, credential, account, balance, position, wallet, order,
real execution, tag, release, or deployment path is authorized.
