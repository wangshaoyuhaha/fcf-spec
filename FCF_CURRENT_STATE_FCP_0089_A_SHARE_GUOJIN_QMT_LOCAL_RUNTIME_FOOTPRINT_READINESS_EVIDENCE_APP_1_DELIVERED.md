# FCF Current State FCP 0089 A-Share Guojin QMT Local Runtime Footprint Readiness Evidence App 1 Delivered

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

Phase: FCF-FCP-0089-A-SHARE-GUOJIN-QMT-LOCAL-RUNTIME-FOOTPRINT-READINESS-EVIDENCE-APP-1

The sidecar implements immutable registration, snapshot, readiness evidence,
a bounded non-recursive metadata scanner, and a path-free canonical renderer
over one Operator-designated local Guojin QMT `userdata_mini` directory.

Contract SHA-256:
`8e711a0463613aa1f60eded5b798378c246aaa981c88ffa5ddeefba1fd6f7e17`.
Reference evidence hash:
`e1a4de03cd08c483dcda80032cdec8d5a031da72bb3e5ef310aae3563a676887`.
Reference output SHA-256:
`b2575598a635c43069b92ef8886d0de8d9fcceb62659f8dc1a488280ed2ff74e`.

Observed registered-local footprint evidence:

- top-level entries: 20
- directories: 6
- regular files: 14
- aggregate regular-file bytes: 340752361
- latest metadata time UTC: 2026-07-21T10:56:41.850343Z
- required directories present: DATADIR, DATAS, DUMPS, LOG, QUOTER, USERS
- required cache families present: STOCK_LIST_SH, STOCK_LIST_SZ, TRADE_DATE_LIST
- missing required footprint classes: none
- manifest SHA-256: `e615110671b90557c134a4696201e25f70a81f99842040bf8e3f7d2ab8629454`
- evidence hash: `09d6c3f8555ec9f50366a51c0a388702d13b565db93db5d2240bb5d82a701511`
- readiness state: READY_FOR_OPERATOR_PROBE
- blockers: MINIQMT_ENTITLEMENT_UNPROVEN, QMT_TERMINAL_LIVENESS_UNPROVEN

No file content, recursive traversal, arbitrary entry name, local path, SDK
invocation, process inspection, network, credential, account, or market value
was used or retained. GAP-104 remains RESEARCH_REQUIRED. No provider,
realtime, promotion, product, P48, broker, exchange, balance, position, order,
execution, tag, release, or deployment authority is created.
