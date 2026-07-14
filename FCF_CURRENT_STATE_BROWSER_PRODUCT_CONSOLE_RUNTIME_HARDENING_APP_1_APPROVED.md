# FCF Current State - BROWSER-PRODUCT-CONSOLE-RUNTIME-HARDENING-APP-1 Approved

## Status

APPROVED_NOT_STARTED

## Approved parent

5624566b4df94e2e4795a6dbb7622845f8b04cd1

## Planned branch

sidecar-browser-product-console-runtime-hardening-app-1

## Purpose

Harden the completed loopback-only Browser Product Console runtime against
malformed local requests, lifecycle faults, bounded resource abuse, path
escape, registered-artifact integrity drift, and nondeterministic failures.

The phase preserves the existing read-only product surface and does not add
research, mutation, dispatch, networking, or execution authority.

## Planned stages

- D1 runtime hardening boundary, threat model, and security contracts
- D2 loopback binding, Host validation, lifecycle, and port-collision controls
- D3 bounded HTTP parsing, timeout, concurrency, and resource controls
- D4 registered-artifact containment, integrity, size, and symlink defenses
- D5 deterministic fault isolation, diagnostics, negative paths, and integration hardening
- D6 acceptance, closeout, merge, and authority synchronization

## Required successor order

1. BROWSER-PRODUCT-CONSOLE-INTEGRATION-ACCEPTANCE-APP-1

The successor phase requires separate explicit approval and must not start
automatically.

## Permanent boundary

- P1-P47 frozen
- no P48
- paper-only
- local-only
- loopback-only
- sidecar-only
- registered-artifact-only
- read-only product presentation
- Operator review mandatory
- Deterministic Engine authority preserved
- Registered Evidence remains evidence authority
- AI advisory only
- no evidence or source artifact mutation
- no command or workflow dispatch
- no external data fetching
- no public network exposure
- no broker, exchange, credentials, account, balance, position, wallet,
  order, or real execution path
- no automatic approval, promotion, baseline replacement, model activation,
  Prompt activation, learning activation, or archive
- no tag, release, or deployment

No runtime-hardening implementation is included in this approval record.
