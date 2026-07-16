# MULTI-MARKET-ADAPTERS Stage 6 D1-D6

## Status

COMPLETED_VALIDATED_READY_FOR_MAIN_MERGE

## Scope

This sidecar delivers the six mandatory deterministic market adapters over
registered immutable local artifacts.

## Delivery order

- D1 shared immutable boundary and China A-share adapter
- D2 United States equity adapter
- D3 Hong Kong equity adapter
- D4 gold and commodity adapter
- D5 digital-asset adapter
- D6 futures adapter, ordered registry, review packet, and group acceptance

## Contracts

Each request links:

- one exact market-adapter identity
- one versioned rule profile
- profile evidence identifiers
- one normalized registered-artifact envelope
- one explicit UTC as-of time
- one correlation identity

All rule profiles, normalized records, findings, derived values, outcomes, and
Operator review packets are immutable.

## Deterministic authority

The adapters validate required market fields and apply only rule values from
the supplied versioned profile. Numeric price limits, settlement assumptions,
roll windows, and other market parameters are not constitutional constants.

The sidecar may derive review information such as:

- configured A-share price bands and T+1 identity
- United States regular or extended-session classification
- Hong Kong odd-lot status
- gold instrument-family identity
- digital-asset funding, mark-price, open-interest, and liquidation context
- futures days-to-expiry, roll-window, margin, basis, and term-structure context

These findings do not replace Deterministic Engine calculations, Registered
Evidence, scoring, ranking, portfolio weights, or Operator decisions.

## Fail-closed behavior

The sidecar blocks or degrades review when it encounters:

- an unapproved evidence identity
- a missing versioned rule
- a missing or invalid required record field
- an adapter-linkage mismatch
- an unsupported session, board, instrument family, or expired contract
- stale source status or market-specific review conditions

Original registered records remain visible in the immutable review packet.

## Permanent boundary

- P1-P47 frozen and no P48
- paper-only, local-only, loopback-only, sidecar-only
- registered-artifact-only and read-only
- Operator review mandatory
- Deterministic Engine and Registered Evidence authority preserved
- AI advisory only
- no live data retrieval, model invocation, or Prompt execution
- no credential, account, wallet, broker, exchange connection, balance,
  position, order, execution, tag, release, or deployment path
