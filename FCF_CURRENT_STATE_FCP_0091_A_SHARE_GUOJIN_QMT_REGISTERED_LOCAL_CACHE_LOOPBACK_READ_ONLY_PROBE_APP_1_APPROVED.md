# FCF Current State FCP 0091 A-Share Guojin QMT Registered Local Cache Loopback Read-Only Probe App 1 Approved

Status: APPROVED_GOVERNANCE_ONLY_NOT_STARTED

Phase: FCF-FCP-0091-A-SHARE-GUOJIN-QMT-REGISTERED-LOCAL-CACHE-LOOPBACK-READ-ONLY-PROBE-APP-1

Approved scope may prepare one bounded single-call local-cache probe using only
`xtquant.xtdata.get_local_data` after FCP-0090 reports terminal liveness. The
probe uses one registered symbol, one date, daily period, the time-only field,
one-row limit, no fill, and no server retrieval.

Only call state, row count, schema presence, timing class, module lineage,
blockers, and canonical hashes may be retained. Returned timestamps and market
values must not be retained. Subscription, download, server retrieval, account
or trading APIs, credentials, provider selection, realtime activation, data
promotion, Gap closure, product, P48, broker, exchange, account, balance,
position, order, execution, tag, release, and deployment are forbidden.
