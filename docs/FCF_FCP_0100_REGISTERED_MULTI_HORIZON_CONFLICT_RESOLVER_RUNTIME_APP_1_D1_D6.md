# FCF FCP 0100 Registered Multi Horizon Conflict Resolver Runtime App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

Phase: FCF-FCP-0100-REGISTERED-MULTI-HORIZON-CONFLICT-RESOLVER-RUNTIME-APP-1

## D1 Exact Registered Artifact

Accept exact Operator-registered bytes only. Byte length, SHA-256, rights,
registration time, ASCII decoding, and a closed JSON schema fail closed.

## D2 Horizon Isolation

Preserve the registered medium-equity, short-equity, A-share intraday, and
BTC short-horizon identities. A conflict set cannot contain duplicate
horizons and cannot create one mixed total score.

## D3 Deterministic Conflict Resolution

Group every horizon result as `SUPPORTING`, `OPPOSING`, `NEUTRAL`, `MISSING`,
`STALE`, or `BLOCKED` by exact state, expiry, direction, and hard-risk
metadata. No AI selection or discretionary resolution is allowed.

## D4 Read-Only Presentation

Expose immutable rows containing horizon, deterministic group, and result
identity. Conflicting results remain visible and no consensus collapse is
allowed.

## D5 Lifecycle And Evidence Integrity

Require evidence for observed results, forbid evidence on missing results,
bind state, correlation, invalidation, availability, and expiry, and reject
future or malformed inputs.

## D6 Operator And Authority Boundary

Require Operator review. The runtime is read-only and creates no calculation,
recommendation, account, order, execution, P48, tag, release, or deployment
authority.
