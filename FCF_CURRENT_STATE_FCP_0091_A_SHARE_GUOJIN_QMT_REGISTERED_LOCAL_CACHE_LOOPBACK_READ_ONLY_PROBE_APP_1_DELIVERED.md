# FCF Current State FCP 0091 A-Share Guojin QMT Registered Local Cache Loopback Read-Only Probe App 1 Delivered

Status: COMPLETED_MERGED_VALIDATED

Phase: FCF-FCP-0091-A-SHARE-GUOJIN-QMT-REGISTERED-LOCAL-CACHE-LOOPBACK-READ-ONLY-PROBE-APP-1

The sidecar implements an immutable exact probe registration, an FCP-0090
terminal-liveness gate, registered SDK lineage verification, one local-cache
call boundary, value-free result reduction, and canonical evidence rendering.

Contract SHA-256:
`da5b77a26f14446303ffd62b5b75a94230837a99afeff1c4e0c49ecab4bdb6d4`.
Reference evidence hash:
`00631fa523696fc27a01d5cdb88b04473442338d8f9ccfaed94607295caae515`.
Reference output SHA-256:
`ea7f6d7e2b816f24c7f3b6aed36291671b26c17642415d2894e764280121147a`.

Registered-local probe evidence:

- terminal snapshot SHA-256: `5fac5f12b854bddf477a48bac42d0178277b2c2878c85aa10039248f81b7b153`
- evidence hash: `ede7dc35af027edd3025be947d728075ea41964a807a00bf749ac873fb2b30bf`
- call state: NOT_RUN
- call attempted: false
- call count: 0
- row count: 0
- schema state: NOT_INSPECTED
- timing class: NOT_MEASURED
- blockers: MINIQMT_ENTITLEMENT_UNPROVEN, QMT_TERMINAL_NOT_OBSERVED, RIGHTS_AND_RETENTION_UNPROVEN

The terminal gate prevented SDK loading and invocation. No returned timestamp,
market value, arbitrary exception text, SDK path, process identity, account
identifier, or credential was retained. GAP-104 remains RESEARCH_REQUIRED.

The all-checks command list now runs FCP-0089, FCP-0090, and FCP-0091 guards as
independent commands. No provider, realtime, promotion, product, P48, broker,
exchange, account, balance, position, order, execution, tag, release, or
deployment authority is created.
