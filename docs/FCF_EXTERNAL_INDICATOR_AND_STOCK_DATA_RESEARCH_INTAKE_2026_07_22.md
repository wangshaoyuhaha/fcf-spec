# FCF External Indicator and Stock Data Research Intake

Status: UNVERIFIED_EXTERNAL_RESEARCH_CANDIDATE

Observation date: 2026-07-22

This note records useful research directions and structural observations only.
It does not register the external package or CSV collection as authoritative
evidence, does not approve an implementation phase, and does not authorize
copying third-party code or formulas.

## External Indicator Package

The downloaded package contains a static indicator catalog, a small Python
example, and a signal-conditioned forward-return example. It is not a complete
backtest engine and provides no observed license or commercial-use grant.

Useful candidate families for independent reimplementation and validation:

- price-volume proxies: VWAP, CMF, MFI, OBV, PVT, and Force Index
- market breadth: ADR, TRIN, STIX, ADIO, and McClellan-style breadth research
- adaptive trend: KAMA
- volatility channel: Keltner Channel
- bounded de-lag comparison: DEMA, TEMA, and HMA
- volume-strength research: VR, EMV, and Klinger-style oscillators

These are candidate ideas, not accepted formulas. CMF, MFI, OBV, PVT, Force
Index, VR, EMV, and Klinger-style values remain OHLCV-derived proxies and must
not be presented as observed capital flow.

Observed package defects and limitations include:

- the example is not a portfolio backtest and omits cash, positions, costs,
  slippage, A-share settlement rules, price limits, and out-of-sample controls
- the sample KDJ smoothing implementation does not match the stated recursive
  smoothing contract
- the sample signal code ignores the catalog's overbought and oversold gates
- multiple catalog formulas contain missing operators, malformed parentheses,
  invalid parameters, broken tokens, or incomplete cells
- no source license or commercial redistribution permission was observed

Any adopted indicator must be independently specified, implemented, tested,
and validated through the Deterministic Engine and existing factor governance.

## External A-Share CSV Collection

The Operator supplied a local CSV collection for read-only inspection. The
collection remains outside the repository and must not be committed to Git.

Observed structural inventory:

- 5,607 CSV files
- 2,979,854,382 total bytes
- 2,375 Shanghai-prefixed files
- 2,984 Shenzhen-prefixed files
- 248 Beijing-prefixed files
- one common 17-column header across all files
- no empty files in the structural scan
- no malformed header or first/last-date records in the structural scan
- earliest observed first date: 1990-12-19
- latest observed last date: 2024-04-24
- 5,357 files end on 2024-04-24; older terminal dates require delisting and
  coverage reconciliation rather than automatic rejection
- filename-and-size manifest SHA-256:
  `1f7b347f530a1a0b8aa05eed88a4ee3f5804eb0998bbc989433498c58d073ce1`

The common schema contains security identity, security name, trade date, raw
OHLC, previous close, volume, amount, free-float market value, total market
value, return, and adjusted OHLC values.

The collection is useful for:

- local parser and normalization research
- deterministic schema and anomaly testing
- historical indicator experiments after quarantine
- cross-provider reconciliation against registered trusted sources
- survivorship, delisting, name-change, and stale-coverage investigations

The collection is not yet suitable for authoritative factor calculation,
training labels, performance claims, or production presentation because the
following evidence is absent or insufficient:

- provider identity, extraction method, version, revision, and availability
  lineage
- license, retention, redistribution, and commercial-use rights
- explicit adjustment factors and corporate-action events
- explicit suspension and trading-status observations
- exchange trading-calendar and expected-date artifacts
- point-in-time publication and first-tradable timestamps
- a complete value-level quality scan and independent-source reconciliation

Sample adjusted prices rise far above corresponding current raw prices for
long-listed securities. This is consistent with a back-adjusted series, but it
is an inference and must not be treated as a verified adjustment contract.

## Adoption Gates

Before any row can become Registered Evidence, a later approved phase must:

1. establish provenance and data-use rights;
2. preserve the source collection read-only outside Git;
3. create a content-addressed manifest without exposing private paths;
4. validate encoding, schema, sorting, duplicates, nulls, OHLC invariants,
   units, stale dates, and market coverage;
5. reconcile listing, delisting, suspension, name changes, corporate actions,
   and expected trading dates;
6. derive or source explicit adjustment factors and prove the adjustment
   policy without future leakage;
7. compare a deterministic sample with an independent registered provider;
8. quarantine all conflicts and require Operator review before promotion.

## Governance Mapping

This intake enriches existing gaps only. It creates no successor phase and no
new runtime authority.

- V2-FR-GAP-008: complete technical indicator library
- V2-FR-GAP-010: factor correlation, clustering, VIF, and ablation validation
- V2-FR-GAP-014: multiple-testing and overfitting controls
- V2-FR-GAP-023: license, permitted use, retention, and cost review
- V2-FR-GAP-089: price and corporate-action lineage
- V2-FR-GAP-090: trading-status and suspension treatment
- V2-FR-GAP-091: immutable layered storage and lineage manifests
- V2-FR-GAP-092: cross-source quality and quarantine runtime
- V2-FR-GAP-093: provider compatibility and evidence matrix

Permanent boundaries remain unchanged: paper-only, local-only, loopback-only,
sidecar-only, registered-artifact-only, read-only product presentation,
mandatory Operator review, Deterministic Engine calculation authority,
Registered Evidence evidence authority, and AI advisory only.
