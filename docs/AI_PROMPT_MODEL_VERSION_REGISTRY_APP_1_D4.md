# AI-PROMPT-MODEL-VERSION-REGISTRY-APP-1 D4

## Purpose

Evaluate compatibility and governance conflicts across a selected
prompt, model, contract, and registry version bundle.

## Required bundle

A complete version bundle contains one record of each kind:

- PROMPT
- MODEL
- CONTRACT
- REGISTRY

Missing or duplicate kinds require review and block compatibility.

## Conflict checks

- blocked, deprecated, or archived version selected
- review-required version selected
- contract reference mismatch
- registry reference mismatch
- validation baseline mismatch
- correlation identifier mismatch
- identical content registered under different version keys

## Result

The report returns:

- compatibility_report_id
- compatibility_report_hash
- compatible
- compatibility_status
- selected versions
- kind and status summaries
- findings
- highest severity

A compatible result means compatible for paper review only.

It does not activate, promote, execute, deploy, or connect any model.

## Safety locks

- human review required
- operator review bypass forbidden
- archive required
- model execution forbidden
- automatic activation forbidden
- automatic promotion forbidden
- automatic rollback forbidden
- source mutation forbidden
- real trading forbidden
- real execution forbidden
