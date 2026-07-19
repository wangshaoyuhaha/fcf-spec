# FCF FCP 0003 Correlated Evidence Confidence Budget Foundation App 1 D1-D6

Status: IMPLEMENTED_PENDING_VALIDATION

## D1 Boundary and Contracts

- immutable registered evidence claims and Operator-authored budget policy
- macro, sector, instrument, and microstructure scope attribution
- supporting, opposing, neutral, ambiguous, missing, and blocked states

## D2 Registered Dependence Groups

- exact one-group membership for every claim
- shared-source evidence must remain in one non-independent group
- one immutable evaluation time rejects future-available evidence
- exact registered evidence hashes and deterministic registry identity

## D3 Deterministic Confidence Budget

- integer basis-point arithmetic with deterministic largest-remainder allocation
- group caps apply before the global cap
- supporting, opposing, and neutral allocations remain separately visible
- confidence-budget diagnostics never become calculation or scoring authority

## D4 Uncertainty and Abstention

- ambiguous taxonomy, missing evidence, blocked evidence, low usable confidence,
  and material support/opposition conflict remain visible
- ambiguous or conflicting evaluations abstain
- no usable evidence produces a blocked result

## D5 Review and Acceptance

- immutable read-only Operator review packet
- explicit scoring, weight-change, network, phase, and automatic approval denial
- Deterministic Engine and Registered Evidence authorities remain unchanged

## D6 Closeout Boundary

Validation does not activate factors, change scoring or weights, select a
market, close gaps, or authorize a product phase. FCF-FCP-0003 remains
NEEDS_RESEARCH with phase_id NONE and Operator decision PENDING.
