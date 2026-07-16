# READ-ONLY-DATA-GATEWAY-APP-1 D2

Status: COMPLETED_VALIDATED

## Scope

- exact registered-source lookup before artifact resolution
- strict allowed-root containment
- symbolic root and artifact path rejection
- regular-file requirement
- bounded binary reading with an eight MiB default limit
- size consistency check during the read
- expected SHA-256 verification before returning content
- immutable verified bytes and evidence-linked receipt
- stable fail-closed reason codes without absolute-path disclosure

## Runtime state

D2 reads only a locally registered CSV or JSON artifact. It does not parse or
normalize content, access a network or credential, or write any artifact.
Deterministic normalization begins in D3.

## Validation

- D2 pytest: 12 passed, 2 skipped
- targeted pytest: 183 passed, 2 skipped
- full pytest: 4309 passed, 5 skipped
- scripts/run_all_checks.py: PASSED
- generated outputs: RESTORED

## Permanent boundary

- P1-P47 frozen and no P48
- paper-only, local-only, loopback-only, sidecar-only, and read-only
- registered-artifact-only
- Operator review mandatory
- Deterministic Engine and Registered Evidence authority preserved
- AI advisory only
- no network, vendor, credential, account, wallet, broker, exchange, order, or
  execution path
- no tag, release, or deployment
