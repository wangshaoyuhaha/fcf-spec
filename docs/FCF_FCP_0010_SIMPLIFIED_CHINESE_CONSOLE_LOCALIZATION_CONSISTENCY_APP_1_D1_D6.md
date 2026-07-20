# FCF FCP 0010 Simplified Chinese Console Localization Consistency App 1 D1-D6

Status: GOVERNANCE_DELIVERY_VALIDATED_PENDING_MERGE

## D1 Boundary and Route Inventory

The immutable boundary is presentation-only. It preserves registered evidence,
deterministic values, mandatory Operator review, and the explicit English
option. The route inventory contains all registered read-only HTML routes from
the frozen browser runtime plus the FCP-0008 and FCP-0009 sidecars.

## D2 Central Catalog

The catalog uses ASCII source with Unicode escapes. It covers shared navigation,
page headings, table labels, notices, empty states, evidence lifecycle pages,
governance summaries, local intake, and market-data diagnostics. Default Simplified Chinese
is explicit and English remains an explicit presentation.

## D3 Evidence-Safe Composition

The FCP-0010 application composes FCP-0009 over an English base document and
applies localization only at the final HTML presentation boundary. Complete
td and code elements are protected before replacement and restored byte-for-byte.
Hashes, identifiers, payloads, registered evidence values, and deterministic
state values are not translated or reinterpreted.

The lang query is validated and removed before frozen evidence query parsing.
Other registered query filters are preserved. This prevents presentation locale
selection from changing Evidence Audit query authority.

## D4 Coverage Audit

The deterministic coverage audit removes style, script, code, and td regions,
then reports any known untranslated UI labels that remain visible. The audit is
run across all registered read-only HTML routes. It never treats evidence values
as translation failures.

## D5 Browser Acceptance

All routes preserve GET and HEAD only. Simplified Chinese is the default;
`lang=en` is explicit and filter-safe. Invalid or duplicate lang values fail
closed. POST, PUT, PATCH, and DELETE remain rejected. No form, button, script, upload,
automatic registration, approval, trading, or execution control exists.

## D6 Validation and Closeout

Validation order is the FCP-0010 test file, related browser console and FCP
suite, full pytest, `scripts/run_all_checks.py`, generated-output restoration,
exact changed-file review, `git diff --check`, sidecar commit and push, main
merge, merge validation, final authority synchronization, and clean repository
verification.

P1-P47 remain frozen. No P48 is created. Paper-only, local-only, loopback-only,
sidecar-only, registered-artifact-only, read-only presentation, Operator review,
Deterministic Engine authority, Registered Evidence authority, and AI advisory
only remain binding. No provider activation, network, credentials, broker,
exchange, account, balance, position, wallet, order, execution, tag, release, or
deployment path is authorized.
