# BROWSER-PRODUCT-CONSOLE-RUNTIME-HARDENING-APP-1 D4

Status: COMPLETED ON SIDECAR BRANCH

## Purpose

D4 hardens registered artifact containment, integrity, size, and symbolic path
handling for the read-only Browser Product Console runtime.

## Delivered

- canonical registered relative path validation
- absolute, traversal, drive, UNC, and alternate stream rejection
- allowed-root containment enforcement
- direct and intermediate symbolic path rejection
- regular-file-only loading
- bounded artifact and index reads
- size verification before and after reads
- deterministic changed-during-read rejection
- SHA-256 verification from the exact bytes parsed as JSON
- optional bounded limits for controlled validation
- registered-artifact-only loading preserved

## Permanent Boundary

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
- Registered Evidence authority preserved
- AI advisory only
- no source artifact mutation
- no broker, exchange, credential, account, balance, position, wallet,
  order, or real execution path
- no tag, release, or deployment

## Next

D5 implements deterministic fault isolation, read-only diagnostics, negative
paths, and runtime integration hardening.
