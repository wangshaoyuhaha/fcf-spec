# DATA-AND-CREDENTIAL-GOVERNANCE D3 Freshness

## Status

IMPLEMENTED

## Delivered

- immutable per-source freshness policies
- deterministic registry checksum
- request-time as-of age evaluation
- FRESH, AGING, STALE, FUTURE_DATED, and UNKNOWN bands
- policy-controlled stale degradation or blocking
- evidence-linked Operator-reviewable decisions

Missing policies and future-dated data fail closed. No wall-clock lookup is used;
the explicit request timestamp remains calculation authority.
