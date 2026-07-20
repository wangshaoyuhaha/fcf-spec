# FCF FCP 0007 A-Share RQData Demo Artifact Intake Replay Acceptance App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Boundary

FCP-0007 accepts one exact Operator-provided RQData official A-share daily
Demo as a registered local evaluation artifact. It adds no network, credential,
provider selection, commercial entitlement, realtime, product, broker,
exchange, account, wallet, position, order, execution, tag, release, or deploy
authority.

The raw provider CSV remains outside the repository. Only deterministic metadata,
hashes, schema observations, quality findings, and missing-coverage facts are
registered. Operator review remains mandatory.

## D2 Exact Artifact And Loader

The registered source has SHA-256
`f229fdf9f86b92562828290159ad2a3d2bcb69a6b57f5e935ce4853a8f280c1e`
and byte length 1897. The loader checks both values before decoding, requires the
exact eleven-column schema, rejects malformed or duplicate rows, and enforces
chronological order and daily-bar invariants.

The source contains 20 leading UTF-8 BOM markers. They are removed only in
memory. The source file is not rewritten.

## D3 Quality Findings

The exact sample contains 19 rows for `000001.XSHE`, from 2022-01-04 through
2022-01-28. It satisfies the bounded daily OHLCV and price-limit schema checks.

It does not provide multi-instrument, intraday, point-in-time availability,
order-book, trade-level, session, universe, sector, adjustment-factor, or
commercial-rights evidence. Product acceptance therefore remains blocked.

## D4 Deterministic Replay

The implementation emits three separate deterministic hashes:

- normalized CSV SHA-256:
  `3333dafe2954ea0ca66766caa3197c3882e4cbde30d55117862bb823e8222a8d`
- canonical row-set SHA-256:
  `5746a6ebdb4e4f9fae7421fc5c46f1d9166cc464e4ac6a794fe35b056eff2255`
- source-bound replay SHA-256:
  `2b846e424d373056000afe8a733a952c3ece1c85510c8a11da0d00de88b970c0`

The result fingerprint is
`172d1a8337e986405a7ba99fc4c528c78fe49507bafde8ba576d2a2b496e2bb1`.

## D5 FCP-0006 Bridge And Operator Packet

Ten FCP-0006 canonical data fields are observed. Fifteen required fields remain
missing. The immutable read-only packet exposes all gaps, unresolved rights,
source linkage, normalization count, and replay evidence without claiming
FCF-FCP-0005 readiness or provider selection.

## D6 Validation And Closeout Boundary

The D1-D6 tests cover fail-closed registration, exact schema and byte identity,
BOM normalization, row validation, deterministic replay, missing evidence,
immutable presentation, and permanent authority boundaries.

Validation evidence:

- FCP-0007 target suite: 17 passed
- FCP-0001 through FCP-0007 targeted governance suite: 168 passed
- full pytest: 5484 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored by the run-all allowlist contract

FCP-0007 remains ACCEPTED_ARCHITECTURE with phase_id NONE. It cannot start a
product phase, select RQData, close referenced gaps, authorize realtime data, or
create V2-R48. P1-P47 remain frozen.
