# DIFY-UI-HANDOFF-APP-1 D5 Manual Workflow Guide

## Purpose

D5 stores the manual local Dify configuration guide inside the repository.

This is not a deployment step.

This is not an automated Dify app creation step.

This is not a Dify API integration step.

## Stage

DIFY-UI-HANDOFF-D5

## Required local Dify variables

- operator_question
- fcf_report_text
- fcf_manifest_text
- review_context
- paper_only_ack

## Manual workflow

1. Create a local manual Dify chatflow or workflow app.
2. Add the required variables.
3. Paste the D4 system prompt and safety prompt.
4. Paste local FCF report text or manifest text only.
5. Require all D3 output sections.
6. Keep operator review before any next step.

## Required output sections

- scope_status
- artifact_summary
- risk_flags
- reason_codes
- operator_review_notes
- blocked_actions
- next_safe_step
- paper_only_notice

## Blocked configuration

- no Dify API write
- no automatic app creation
- no external tool call
- no broker connection
- no exchange connection
- no API key variable
- no wallet private key variable
- no real account variable
- no real position variable
- no order execution node
- no trade action button
- no operator review bypass

## Safety boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- manual configuration only
- no real execution
- no trade action

## Next stage

D6 will close out the DIFY-UI-HANDOFF-APP-1 sidecar with final handoff and validation.
