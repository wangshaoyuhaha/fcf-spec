# P4 Controlled Enhancements Stage 12 D1-D6

## D1 - Governance and Boundary

- five canonical P4 capability identities remain explicit
- stable P0-P3 prerequisite is satisfied by Stage 11
- paper-only, local-only, loopback-only, sidecar-only, and
  registered-artifact-only controls remain mandatory
- automatic and realtime labels do not grant execution authority

## D2 - Case Memory Retrieval

- immutable positive, negative, blocked, failed, and inconclusive cases
- point-in-time filtering by availability time
- retrieval only inside an explicit registered-artifact allowlist
- deterministic filtering, ordering, and limits
- read-only output with no network retrieval

## D3 - Challenger and Schedule Proposals

- deterministic selection from declared change options
- Stage 11 LearningCandidate contract remains authoritative
- candidate-only Challenger output
- proposed experiment windows and dependencies
- no job execution, activation, or promotion

## D4 - Realtime Shadow Validation

- local registered forward observations only
- decision time cannot precede the forward window
- registration after observation and point-in-time as-of enforcement
- pending and contradictory observations remain visible
- no live-market retrieval or real execution

## D5 - Specialist Training Governance

- specialist training plans identify registered datasets, configuration,
  objectives, and Operator trigger
- Stage 12 cannot execute training or invoke a model
- only registered training-result artifacts are evaluated
- missing objectives, negative metrics, and plan mismatches remain visible
- evaluation is advisory and cannot activate a model

## D6 - Acceptance and Presentation

- all five P4 capabilities are accepted independently
- Web Console renders registered P4 sections read-only
- next phase is local AI runtime configuration governance
- Dify/model-provider configuration remains outside Stage 12
