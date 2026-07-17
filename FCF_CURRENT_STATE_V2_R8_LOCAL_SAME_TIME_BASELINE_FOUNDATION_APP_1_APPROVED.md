# FCF Current State V2 R8 Local Same-Time Baseline Foundation App 1 Approved

Status: APPROVED_NOT_STARTED

Business objective:

- compute deterministic same-session-slot and regime-relative local baselines
- prevent completed-day or future-available values from entering an earlier view

Approved D1-D6 scope:

- D1 closed registered-local point-in-time baseline boundary
- D2 immutable session-linked observation and baseline policy contracts
- D3 deterministic Decimal count, mean, median, minimum, and maximum statistics
- D4 session, slot, regime, availability, sample, and mismatch blocking
- D5 append-only baseline ledger and metadata-only read model
- D6 Operator acceptance, guards, tests, merge, and closeout

Readiness Gate:

- dependency: completed V2-R7 registered session resolution foundation
- inputs: registered local historical observations and explicit as-of time
- formula: exact Decimal statistics over one phase, slot, regime, and feature
- rights and cost: registered local artifacts only; no external cost
- acceptance: deterministic baseline and canonical SHA-256
- rollback: V2-R8 Sidecar and exact governed files only
- stop: network, live source, future evidence, completed-day leakage, scoring,
  model, Prompt, learning, execution, unexpected path, or test failure

This is not a realtime baseline service, factor activation, score, signal,
ranking, recommendation, account, order, or execution engine. V2-FR-GAP-049
remains open beyond this bounded foundation.

P1-P47 remain frozen. No P48. No tag, release, or deployment is authorized.
