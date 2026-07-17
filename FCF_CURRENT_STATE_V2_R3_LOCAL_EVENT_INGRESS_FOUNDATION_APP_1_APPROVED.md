# FCF Current State V2 R3 Local Event Ingress Foundation App 1 Approved

Status: APPROVED_NOT_STARTED

Approved branch:

- `sidecar-v2-r3-local-event-ingress-foundation-app-1`

Business objective and horizon:

- establish deterministic event-ingress contracts before any external source
- support bounded event-level local replay only
- preserve future realtime source selection as separate Operator research

Approved D1-D6 scope:

- D1 local registered-event boundary and exact event envelope
- D2 immutable UTC event, receive, and processing time validation
- D3 bounded idempotent ingress with sequence and capacity failure closure
- D4 deterministic replay checkpoint, restart, expiry, and receipt identity
- D5 immutable read-only presentation and mandatory Operator acceptance
- D6 exact guard, tests, validation, merge, final sync, and cleanup

Readiness Gate:

- source: Operator-supplied registered local artifacts only
- rights: existing Operator-confirmed local research rights; no redistribution
- cost: no data purchase, network, provider, credential, or external compute
- fields: event and stream IDs, source and artifact IDs, event type, sequence,
  event, receive, and processing time, payload, payload hash, clock quality,
  correction kind, and schema version
- interfaces: immutable event envelope, bounded ingress, receipt, checkpoint,
  replay, read-only presentation, and Operator acceptance
- failure behavior: reject duplicate IDs, duplicate or missing sequence,
  timestamp inversion, unsafe payloads, capacity overflow, expiry, checksum
  mismatch, checkpoint mismatch, and authority violations
- tests: immutability, UTC order, idempotency, sequence, bounded capacity,
  expiry, deterministic replay, restart, presentation, acceptance, and guard
- rollback: new V2-R3 Sidecar and exact governed files only
- acceptance: deterministic local replay with no silent loss or mutation
- stop conditions: any external source, provider, market selection, credential,
  unbounded process, daemon, network, AI invocation, scoring, order, execution,
  unexpected changed path, safety failure, or test failure

This phase does not implement an approved realtime source, market connection,
production ingestion process, external queue, market scanner, anomaly radar,
order book, factor activation, official score, ranking, model, Prompt, training,
automatic learning, Paper order, virtual account, or execution route. Gaps
V2-FR-GAP-022 through V2-FR-GAP-025, V2-FR-GAP-028, and V2-FR-GAP-030 remain
open outside this local foundation.

P1-P47 remain frozen. No P48 is created. Paper-only, local-only,
loopback-only, sidecar-only, registered-artifact-only, read-only presentation,
Deterministic Engine calculation authority, Registered Evidence authority,
advisory AI, and mandatory Operator review remain binding.

No broker, exchange, credential, account, balance, position, wallet, order,
real execution, tag, release, or deployment path is authorized.
