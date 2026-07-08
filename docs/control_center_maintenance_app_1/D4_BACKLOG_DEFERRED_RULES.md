# CONTROL-CENTER-MAINTENANCE-APP-1 D4 Backlog Deferred Rules

Status: D4 completed.

Purpose: define how deferred backlog items and candidate sidecars must be maintained in docs/FCF_PROJECT_CONTROL_CENTER.md.

Backlog item required fields:
- item name
- item type
- current status
- deferred reason
- start condition
- required operator approval
- dependency
- safety gate
- latest update source

Deferred status values:
- required later
- optional deferred
- blocked
- accepted candidate
- rejected
- completed

Current deferred items:
- DIFY-LOCAL-CONFIG-HARDENING-APP-1: optional deferred until operator starts local Dify or Ollama configuration.
- Future sidecar development: blocked until explicit operator approval.

Maintenance rules:
- chat memory must not replace repo backlog records
- every accepted idea must be written to the control center
- every rejected idea must keep rejection reason
- every deferred item must keep start condition
- no candidate sidecar may start automatically
- no deferred item may be silently dropped

Safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator-review-only
- no P48
- no core mutation
- no real trading
- no real execution
- no deploy
- no release
- no tag

D4 result: backlog and deferred item maintenance rules established.
