# BROWSER-PRODUCT-CONSOLE-RUNTIME-HARDENING-APP-1 D3

Status: COMPLETED ON SIDECAR BRANCH

## Purpose

D3 hardens the local HTTP request and bounded resource boundary.

## Delivered

- GET and HEAD only runtime enforcement
- deterministic HTTP 405 with Allow response
- malformed and absolute request target rejection
- bounded request target size
- bounded header count and header line size
- request body rejection
- duplicate and invalid Content-Length rejection
- Transfer-Encoding rejection
- Expect rejection
- deterministic 400, 405, 413, 414, 417, 431, and 503 responses
- bounded socket timeout
- bounded concurrent request workers
- deterministic over-capacity rejection
- active and rejected request diagnostics
- Connection close after each local response
- security header preservation on success and rejection

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
- no external network binding
- no broker, exchange, credential, account, balance, position, wallet,
  order, or real execution path
- no tag, release, or deployment

## Next

D4 implements registered-artifact path containment, symlink escape rejection,
artifact size limits, and SHA-256 integrity revalidation.
