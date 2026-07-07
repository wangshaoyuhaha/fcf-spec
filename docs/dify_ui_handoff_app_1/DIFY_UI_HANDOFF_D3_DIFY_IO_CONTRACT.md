# DIFY-UI-HANDOFF-APP-1 D3 Dify IO Contract

## Purpose

D3 defines the manual local Dify input and output contract for FCF report reading.

This stage is not a live trading integration. It is a local operator assistant contract.

## Input fields

- operator_question
- fcf_report_text
- fcf_manifest_text
- review_context
- paper_only_ack

## Required output sections

- scope_status
- artifact_summary
- risk_flags
- reason_codes
- operator_review_notes
- blocked_actions
- next_safe_step
- paper_only_notice

## Required behavior

The Dify app may summarize and explain local FCF artifacts.

The Dify app must preserve:

- paper-only
- local-only
- read-only
- operator review required
- risk flags
- reason codes
- no real execution

## Forbidden output

The Dify app must not output:

- buy instruction
- sell instruction
- order instruction
- position sizing instruction
- portfolio rebalance instruction
- broker connection instruction
- exchange connection instruction
- api key request
- wallet private key request
- real account access request
- real position access request
- profit guarantee
- future return guarantee
- operator review bypass
- risk flag downgrade
- reason code deletion

## Next stage

D4 will create the Dify system prompt and safety prompt template.
