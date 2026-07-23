# FCF FCP 0103 Registered Technical Indicator Catalog Runtime App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

Phase: FCF-FCP-0103-REGISTERED-TECHNICAL-INDICATOR-CATALOG-RUNTIME-APP-1

## D1 Exact Registered Catalog Artifact

Require exact Operator-registered ASCII JSON bytes, byte length, SHA-256,
rights identity, closed schemas, unique kinds, and versioned factor refs.

## D2 Exact Runtime Registry Composition

Bind the exact FCP-0096 factor registry identity and reject unregistered or
transitively invalidated factor references.

## D3 Existing Foundation Mapping

Map only the completed V2-R12 through V2-R20 deterministic indicator
foundations and the FCP-0101 VWAP implementation. Do not duplicate formulas.

## D4 Explicit Coverage Gap

Expose all supported kinds and all accepted but missing candidates. A partial
catalog must remain `CATALOG_PARTIAL`; unsupported candidates are never
silently promoted or treated as implemented.

## D5 Immutable Evidence

Bind the catalog artifact, registry snapshot, foundation references, factor
references, missing candidates, reason codes, and deterministic snapshot
hash in immutable mappings and tuples.

## D6 Authority Boundary

Deterministic Engine remains calculation authority and Operator review
remains mandatory. The catalog cannot activate calculation, score, rank,
recommend, connect accounts, place orders, or execute. P48, tag, release, and
deployment remain forbidden.

## Validation

Completed with 10 isolated tests, 136 affected-chain tests, 1908 all-FCP
tests, 7245 full-pytest tests, and `run_all_checks.py` passing. Delivery
commit: `14d5692e8208e248a54056ff636840315620d6ad`. Merge commit:
`5a4d323ad0893c7036b13b3e5be2ddf05a9616a6`.
