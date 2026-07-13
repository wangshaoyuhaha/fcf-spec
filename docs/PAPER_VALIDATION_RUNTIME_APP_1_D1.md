# PAPER-VALIDATION-RUNTIME-APP-1 D1

## Scope

D1 establishes the local paper validation runtime boundary and typed domain
model.

## Authority

- Operator Policy remains highest authority.
- FCF Hard Policy remains binding.
- The deterministic engine remains calculation authority.
- Registered artifacts remain evidence authority.
- Operator review remains mandatory.
- AI remains advisory only.

## Runtime boundary

The runtime is:

- local-only
- paper-only
- read-only for source artifacts
- explicitly Operator-triggered
- deterministic
- sidecar-only

The runtime does not allow:

- scheduler, queue, worker, daemon, or listener
- web server, API endpoint, or network port
- external data fetch
- broker or exchange connectivity
- credential, wallet, account, balance, or position access
- order creation, order placement, or real execution
- automatic approval, promotion, baseline replacement, learning activation,
  archive, or shadow observation

## Typed model

D1 defines:

- RuntimeBoundary
- EvaluationWindow
- RegisteredArtifact
- ValidationSample
- ComparisonPolicy
- ValidationRunRequest

All authority escalation fields fail closed.
