# FCP-0106 A Share QMT Internal Read Only Market Bridge App 1 D1-D6

## D1 Closed Registration Contract

Register one bounded ordinary QMT internal quote bridge, exact schema, exact
source identity, safe A-share symbol syntax, freshness limits, file limits,
and one initial symbol. All configuration remains local and value-free.

## D2 QMT Internal Quote Producer

Use only QMT `ContextInfo.set_universe` and
`ContextInfo.subscribe_quote`. Write bounded atomic ASCII JSON events without
network modules, credentials, account APIs, trading APIs, or SDK RPC. Preserve
Python 3.6 syntax and use only a closed local config candidate set because the
ordinary QMT embedded runtime does not define `__file__`.

## D3 Registered Local Spool Receiver

Read only regular local files from one registered directory. Reject symlinks,
reparse points, network paths, unexpected names, oversized events, excessive
file counts, non-ASCII bytes, and non-canonical JSON.

## D4 Integrity And Realtime Gates

Validate exact event hashes, positive sequences, strict per-symbol ordering,
deduplication, independent event-clock and receive-clock maximum age, future
skew, price coherence, and registered symbols. A freshly received simulation
replay with an old market clock is not realtime evidence.

## D5 Candidate Observation Snapshot

Publish an immutable read-only `CANDIDATE_REALTIME_OBSERVED` snapshot. Preserve
native QMT volume as `QMT_NATIVE_UNCALIBRATED` until an observed callback is
calibrated against registered local daily export evidence.

## D6 Authority Boundary

Registered Evidence remains evidence authority and Operator review remains
mandatory. The bridge cannot promote data or grant market-data, credential,
account, balance, position, order, or execution authority. P1-P47 remain
frozen; P48, tag, release, and deployment remain forbidden.
