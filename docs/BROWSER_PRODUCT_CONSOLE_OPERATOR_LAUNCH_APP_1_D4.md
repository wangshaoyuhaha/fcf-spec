# BROWSER-PRODUCT-CONSOLE-OPERATOR-LAUNCH-APP-1 D4

Status: IMPLEMENTED ON SIDECAR BRANCH

## Purpose

D4 provides deterministic, non-technical startup diagnostics without leaking
raw tracebacks or weakening fail-closed validation.

## Diagnostic states

- `FCF-LAUNCH-READY`
- `FCF-LAUNCH-ARTIFACT-MISSING`
- `FCF-LAUNCH-ARTIFACT-INTEGRITY`
- `FCF-LAUNCH-ARTIFACT-REGISTRATION`
- `FCF-LAUNCH-FILE-ACCESS`
- `FCF-LAUNCH-PORT-UNAVAILABLE`
- `FCF-LAUNCH-STARTUP-REJECTED`

Every blocked state includes a stable explanation and safe remediation. D4
does not bypass missing files, digest mismatch, path containment, port
collision, or exact loopback enforcement.
