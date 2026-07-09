# CONTROL-CENTER-ENCODING-GUARD-APP-1 D3 Encoding Probe

## Scope

D3 adds a read-only encoding probe for guarded governance files.

The probe detects strict UTF-8 status, UTF-8 BOM, newline style, byte size, and guard status.

## Probe Fields

Each probe record contains:

- path
- exists
- byte_size
- strict_utf8_status
- has_utf8_bom
- newline_style
- guard_status

## Newline Styles

Supported newline style values:

- EMPTY
- LF
- CRLF
- MIXED
- MIXED_OR_CR
- NO_NEWLINE
- UNKNOWN

## Guard Status

Supported guard status values:

- PASS
- WARN_BOM
- WARN_NEWLINE
- BLOCK

## Blocking Rules

A guarded file is blocked when:

- it is missing
- it cannot be decoded with strict UTF-8

## Warning Rules

A guarded file warns when:

- it contains UTF-8 BOM
- it uses CRLF, mixed newline, or raw CR newline style

## Sidecar Boundary

This probe is read-only.

It does not rewrite governed files in D3.
It only reports encoding and newline conditions.

## Forbidden Scope

- no core mutation
- no source overwrite
- no source deletion
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
- no broker connection
- no exchange connection
- no API key
- no wallet key
- no real account
- no real position
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy