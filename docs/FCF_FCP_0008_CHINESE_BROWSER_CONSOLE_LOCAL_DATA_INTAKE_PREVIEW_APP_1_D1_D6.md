# FCF FCP 0008 Chinese Browser Console Local Data Intake Preview App 1 D1-D6

Status: COMPLETED_MERGED_VALIDATED

## D1 Boundary And Composition

FCP-0008 is a sidecar around the frozen browser console. It preserves the
existing read model, registered-artifact loader, loopback server, health
contract, and all authority boundaries. Browser presentation remains read-only
and accepts only GET and HEAD.

## D2 ASCII-Source Localization

The localization catalog is ASCII-only Python source. Simplified Chinese is
encoded with Unicode escape sequences and rendered as UTF-8 at the presentation
boundary. The default locale is `zh-CN`; an explicit `en` option preserves the
existing English presentation.

Localization changes presentation text only. It does not translate identifiers,
registered evidence, deterministic values, hashes, reason codes, or source data.

## D3 Registered Local CSV Preview

The provider-neutral inspector requires an exact registered SHA-256 and byte
length before decoding. It requires UTF-8, bounded unique columns, consistent
row width, and at least one data row. The source file is never copied or
rewritten. Leading BOM markers are normalized only in memory.

The preview exposes source and normalized hashes, a deterministic schema hash,
columns, row count, BOM count, unresolved rights and retention, and a blocked
product-evidence state. It does not select a provider or grant storage,
redistribution, commercial, realtime, or product authority.

## D4 Read-Only Intake Workspace

`/local-data-intake` presents registered previews inside the existing console
layout. Existing HTML routes are localized through the sidecar. The health JSON
remains unchanged. The new page contains no form, button, script, upload, write,
registration, promotion, approval, or execution control.

## D5 Explicit Local Tools

`scripts/run_fcp_0008_local_csv_preview.py` prints a deterministic JSON preview
for one exact registered local CSV. `scripts/run_fcp_0008_localized_console.py`
starts or checks the localized console on exact loopback and can attach one
exact registered local CSV preview. Both fail closed on incomplete registration
or integrity mismatch.

## D6 Validation And Closeout Boundary

The target tests cover immutable boundaries, ASCII source, locale selection,
exact-byte inspection, invalid CSV rejection, source preservation, immutable
preview facts, localized GET and HEAD, unchanged health metadata, and write
method rejection.

Validation evidence:

- FCP-0008 target suite: 22 passed
- browser console targeted suite: 562 passed
- FCP-0001 through FCP-0008 governance suite: 169 passed
- full pytest: 5506 passed
- `scripts/run_all_checks.py`: ALL CHECKS PASSED
- generated runtime outputs: restored by the run-all allowlist contract
- exact Operator-provided CSV preview: 19 rows and 20 in-memory BOM removals

FCP-0008 remains ACCEPTED_ARCHITECTURE with phase_id NONE. It cannot create a
product phase, close a referenced gap, authorize realtime data, or create V2-R48.
P1-P47 remain frozen.
