# FCF Current State FCP 0091 A-Share Guojin QMT Registered Local Cache Loopback Read-Only Probe App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Phase: FCF-FCP-0091-A-SHARE-GUOJIN-QMT-REGISTERED-LOCAL-CACHE-LOOPBACK-READ-ONLY-PROBE-APP-1

The immutable registered local-cache probe is implemented, validated, merged
to main, and synchronized. It requires FCP-0090 terminal liveness before SDK
loading, verifies exact registered SDK lineage, permits one time-only local
cache call, and reduces any result to value-free bounded evidence.

Validation evidence:

- isolated FCP-0091 tests: 24 passed
- affected A-share and governance tests: 603 passed
- all FCP tests: 1795 passed
- full pytest: 7132 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED before and after merge
- generated outputs: restored; no tracked generated changes remained

Contract SHA-256:
`da5b77a26f14446303ffd62b5b75a94230837a99afeff1c4e0c49ecab4bdb6d4`.
Reference evidence hash:
`00631fa523696fc27a01d5cdb88b04473442338d8f9ccfaed94607295caae515`.
Reference output SHA-256:
`ea7f6d7e2b816f24c7f3b6aed36291671b26c17642415d2894e764280121147a`.
Observed terminal snapshot SHA-256:
`5fac5f12b854bddf477a48bac42d0178277b2c2878c85aa10039248f81b7b153`.
Observed evidence hash:
`ede7dc35af027edd3025be947d728075ea41964a807a00bf749ac873fb2b30bf`.

Evidence commits:

- approval: `a4a361ac089e995265c2633379fd7e7043d2157f`
- sidecar delivery: `be17c9fb4ea327e74e1aa3ad567ab7fd6fb53265`
- main merge: `ab80995a8a4f7a152785e8b8f6da1161ab1834f5`

The observed gate emitted NOT_RUN with call count zero because no registered
QMT terminal family was active. The SDK was not loaded and no probe call was
made. GAP-104 remains RESEARCH_REQUIRED; entitlement, rights, retention, and
market-data availability remain unproven.

The all-checks wiring defect that previously passed FCP-0089 and FCP-0090 guard
paths as extra FCP-0088 arguments is repaired; all three guards and FCP-0091
now execute independently.

No returned timestamp, market value, arbitrary exception text, SDK path,
credential, subscription, download, server retrieval, account or trading API,
provider, realtime, promotion, product, P48, broker, exchange, account,
balance, position, order, execution, tag, release, or deployment authority was
created.
