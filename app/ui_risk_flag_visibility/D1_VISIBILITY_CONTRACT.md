# UI-RISK-FLAG-VISIBILITY-APP-1 D1 Contract

Purpose: verify read-only UI visibility for risk flags, reason codes, blocked response state, and operator review state.

Required visibility:
- risk_flags must be rendered explicitly
- reason_codes must be rendered explicitly
- blocked_response_state must be rendered explicitly
- operator_review_required must be rendered explicitly
- risk flag downgrade is forbidden
- risk flag deletion is forbidden
- reason code deletion is forbidden
- UI warning-to-approval conversion is forbidden
- operator review bypass is forbidden

Safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no buy button
- no sell button
- no order button
- no broker connection
- no exchange connection
- no API key storage
- no real account access
- no real position access
- no real execution
- no tag
- no release
- no deploy
