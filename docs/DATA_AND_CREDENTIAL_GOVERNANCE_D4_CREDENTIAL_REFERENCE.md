# DATA-AND-CREDENTIAL-GOVERNANCE D4 Credential Reference

## Status

IMPLEMENTED

## Delivered

- opaque credential-reference metadata contract
- deterministic metadata registry checksum
- declared availability, unavailability, unknown, and expiry decisions
- fail-closed required-reference gate
- explicit no-material and no-retrieval-locator invariants

This component never accepts, stores, retrieves, reveals, or uses a credential
or secret. It does not read environment variables or files and cannot perform an
authenticated request.
