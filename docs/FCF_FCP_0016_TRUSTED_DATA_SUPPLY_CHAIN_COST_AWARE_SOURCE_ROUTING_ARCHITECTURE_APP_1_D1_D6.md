# FCF FCP 0016 Trusted Data Supply Chain Cost Aware Source Routing Architecture App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Canonical Contract and Provider Isolation

The canonical core uses immutable typed records with exact values, units,
clocks, schema versions, quality state, and lineage. Vendor SDK and DataFrame
objects terminate at provider adapters.

## D2 Point-in-Time and Adjustment Law

Event, publication, availability, first-tradable, ingest, and revision clocks
are distinct. Raw observations, corporate actions, adjustment factors, factor
versions, query policy, and explicit trading status remain reproducible.

## D3 Storage, Reconciliation, and Quarantine

RAW, NORMALIZED, and RESEARCH layers preserve rights, retention, schema,
transformation, parent, and content digests. Material cross-source disagreement
fails closed into `SPLIT_FAULT` quarantine.

## D4 Source Roles and Market Isolation

Provider roles are explicit and evidence-governed. RQData, MiniQMT market data,
Tushare, AkShare, and BaoStock remain candidates. MiniQMT trading surfaces are
prohibited and process-isolated. A-share and BTC keep separate semantics.

## D5 Rights and Incremental Value Gate

Trial access does not imply permanent retention or commercial use. Free and
paid sources must pass rights, quality, reliability, and incremental after-cost
value review. Profitability remains an empirical objective, not a claim.

## D6 Validation and Closeout

Validation order is the isolated FCP-0016 suite, governance targeted suite,
full pytest, `scripts/run_all_checks.py`, generated-output restoration, exact
changed-file verification, and `git diff --check`.

Validated result before full closeout:

- FCP-0016 isolated suite: 2 passed
- FCP governance targeted suite: 398 passed
- architecture guard suite: 9 passed
- full pytest: 5714 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: no tracked output changed; no restoration required
