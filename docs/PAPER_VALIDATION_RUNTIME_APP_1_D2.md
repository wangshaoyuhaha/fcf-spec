# PAPER-VALIDATION-RUNTIME-APP-1 D2

## Scope

D2 implements registered local input loading and evaluation-window enforcement.

## Registered input requirements

Each input artifact must provide:

- artifact_id
- artifact_version
- correlation_id
- content_type
- evaluation_window
- samples

The registry entry must provide the expected relative path and SHA-256 digest.

## Local read-only controls

The loader:

- resolves files only under an allowed local root
- rejects symbolic links
- rejects paths outside the allowed root
- verifies SHA-256 before parsing
- verifies artifact identity against the registry
- preserves correlation_id
- does not write to the source artifact

## Leakage controls

For every sample:

- decision time must be within the registered decision period
- decision time must not exceed the decision cutoff
- outcome time must occur after the decision cutoff
- outcome time must not exceed the observation cutoff or window end
- sample_id values must be unique

Any violation fails closed.
