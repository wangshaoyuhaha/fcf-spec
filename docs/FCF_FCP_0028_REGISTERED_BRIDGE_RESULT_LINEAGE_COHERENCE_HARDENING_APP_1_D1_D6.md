# FCF FCP 0028 Registered Bridge Result Lineage Coherence Hardening App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Canonical Byte Registration Coherence

A-share and BTC bridge results require their immutable canonical bytes to
match the registered artifact digest and byte length exactly.

## D2 Manifest Coherence

Canonical manifest digests must match the canonical bytes. BTC canonical
artifact identity must also match its registered artifact identity.

## D3 Count and Observation Coherence

A-share manifest row counts match canonical CSV data rows. BTC manifest
observation hashes match the typed observation sequence exactly.

## D4 Deterministic BTC Payload Lineage

BTC results accept only the five registered observation classes. Every
observation carries the canonical artifact identity, and deterministic NDJSON
reconstruction must equal the registered canonical bytes.

## D5 Regression Guard

The dedicated guard verifies synchronized authority evidence, production
markers, isolated tests, and all-check wiring.

## D6 Validation and Closeout

Validation order is the FCP-0028 isolated suite, affected A-share and BTC
bridge suites, FCP governance target suite, full pytest,
`scripts/run_all_checks.py`, generated-output restoration, exact changed-file
verification, and `git diff --check`.

Validated result:

- FCP-0028 isolated suite: 15 passed
- affected A-share and BTC bridge suite: 54 passed
- FCP governance stage suite: 606 passed
- project governance suite: 21 passed
- full pytest: 5943 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: final run left no tracked generated changes
