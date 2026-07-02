# Module Boundaries

Status: P0-D2

## Modules

### safe_boundary

Owns the non-negotiable paper-only safety flags.

### runtime

Runs the minimal paper runtime check.

### future modules

Future modules may be added only if they preserve safe_boundary:

- input_snapshot
- analysis_engine
- risk_policy
- operator_review
- report_renderer

## Rules

No module may:

- connect real exchanges
- store real keys
- place real orders
- read real balances
- read real positions
- bypass operator review
- bypass safe_boundary

Every future module must be testable.
