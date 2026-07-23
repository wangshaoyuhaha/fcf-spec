# FCF Current State FCP 0101 Registered Technical Indicator Core Runtime App 1 Final

Status: COMPLETED_MERGED_VALIDATED

Phase: FCF-FCP-0101-REGISTERED-TECHNICAL-INDICATOR-CORE-RUNTIME-APP-1

Delivery commit:
`e8c197667cd7e5636435f1c8af00ee01f13308b5`.
Merge commit:
`492ab650d0cac94602ca47d5c65aa59fc122bb1f`.

The registered-artifact-only sidecar verifies exact ASCII JSON bars and
calculates deterministic SMA, EMA, Bollinger, RSI, ATR, and VWAP evidence with
Decimal arithmetic, strict point-in-time ordering, and suspension exclusion.

Reference artifact SHA-256:
`4c537b0e80db53fe2f7e4faf38355f3f5f36e63871b8087514a8b3fc0e48d852`.
Runtime snapshot hash:
`261a2044b12634905e8b94fd54bacaa2aaf4cce2134c246c439418960dfab6dc`.
Rendered output SHA-256:
`8834b0b8d1bac8dfbd2bbbd1f264f8932c85a3c55e5daaa7112e4a348aea3c26`.

Validation: 8 isolated tests, 100 affected-chain tests, 1888 all-FCP tests,
7225 full-pytest tests, and `run_all_checks.py` passed.

GAP-008 and GAP-009 remain open pending the complete registered factor catalog
and normalization and missing-state implementation. Deterministic Engine
remains calculation authority and Operator review remains mandatory. No
scoring, ranking, recommendation, account, order, or execution authority was
created. No tag, release, or deployment was run.
