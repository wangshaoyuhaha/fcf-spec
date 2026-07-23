# FCF FCP 0093 BTC Coin Metrics Reference Rate Local CSV Validation App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Exact Local Registration

Bind one bounded regular non-symlink local CSV to exact byte length, SHA-256,
typed local rights, registration time, media type, and closed schema identity.

## D2 Closed CSV Contract

Require the exact `asset,time,ReferenceRateUSD` header, BTC rows, UTF-8 without
BOM or NUL bytes, positive non-exponent decimal lexemes, and final newline.

## D3 Temporal Integrity

Require at least two unique strictly ordered UTC observations, no observation
after validation time, and exact 3600-second cadence.

## D4 Value-Free Durable Evidence

Emit only artifact identity, hashes, byte and row counts, UTC bounds, cadence,
quality, neutral observation kind, and mandatory-review metadata. Retain no
source rows, values, or paths.

## D5 Non-Authority Boundary

Keep GAP-095 RESEARCH_REQUIRED. Create no SDK, network, provider, venue,
realtime, promotion, mark or index, signal, product, wallet, account, order,
or execution authority.

## D6 Validation And Closeout

Run isolated, affected BTC and governance, all FCP, full pytest, and
all-checks suites; restore generated outputs; audit exact files, ASCII, hashes,
and `git diff --check`; then commit, push, merge, revalidate, and synchronize.
