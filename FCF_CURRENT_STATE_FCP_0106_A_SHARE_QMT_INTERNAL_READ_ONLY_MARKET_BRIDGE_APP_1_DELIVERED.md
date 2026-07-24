# FCF Current State FCP 0106 A Share QMT Internal Read Only Market Bridge App 1 Delivered

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

Phase: FCF-FCP-0106-A-SHARE-QMT-INTERNAL-READ-ONLY-MARKET-BRIDGE-APP-1

The ordinary QMT internal script subscribes only to registered quote symbols
and writes bounded atomic ASCII JSON events to a local spool. The FCF
registered receiver validates exact schema, hashes, symbols, freshness,
ordering, duplicates, filename-to-payload identity, path safety, file size,
and batch size.

The bridge is candidate realtime observation only. Volume units remain
`QMT_NATIVE_UNCALIBRATED`, data promotion requires separate evidence and
Operator review, and no credential, account, balance, position, order, or
execution path exists.

Local ordinary QMT compatibility was observed on 2026-07-24. The embedded
runtime is Python 3.6 and does not define `__file__`, so the producer uses a
closed local config candidate set. QMT successfully registered the read-only
`600000.SH` tick subscription and produced exact-schema local events.

The observed run was after market close in QMT simulation mode. Its market
event clocks were about 2.35 to 2.87 hours behind receipt, so the receiver now
checks receive-clock and market-clock freshness independently and rejects the
replay as realtime evidence. Live-session acceptance and volume calibration
remain pending; no data authority was promoted. A bounded local probe now
prepares only value-free, non-authorizing evidence after both clocks pass.
The exact live-session sequence and exit meanings are fixed in
`docs/FCF_FCP_0106_QMT_LIVE_OPERATOR_REVIEW_RUNBOOK.md`.
The saved QMT strategy file was also observed to use a terminal-managed opaque
representation, while the plain local config matched the registered repository
hash exactly. The repository source remains source authority.
