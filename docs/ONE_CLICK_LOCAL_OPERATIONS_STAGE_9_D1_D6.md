# One-Click Local Operations Stage 9 D1-D6

## Product Entry Points

Windows Operators can double-click:

- 'operations/windows/FCF Start.cmd'
- 'operations/windows/FCF Stop.cmd'
- 'operations/windows/FCF Status.cmd'
- 'operations/windows/FCF Backup.cmd'

Normal use does not require typing Python or PowerShell. The command wrappers
use the project virtual environment when present and otherwise use the
configured local Python runtime.

## D1 - Boundary and State

- exact-loopback, paper-only, sidecar-only operations
- atomic instance-owned lifecycle state
- no public binding, automatic authority transition, or financial execution

## D2 - Preflight

- runtime, registered artifacts, integrity, migration, port, path containment,
  required-model, and database backup-target checks
- explicit missing-model, port, artifact, and database notifications

## D3 - Start, Stop, and Status

- single-instance background service start
- health readiness before browser opening
- instance-token graceful stop request
- no process-name matching or unrelated-process termination
- visible READY, DEGRADED, STOPPED, BLOCKED, and stale-state behavior

## D4 - Health and Recovery Guidance

- exact-loopback health endpoint verification
- bounded readiness and graceful-stop timeouts
- persistent service log and deterministic failure messages

## D5 - Backup and Recovery

- registered configuration and evidence backup
- optional configured database target backup
- pre-upgrade snapshot
- SHA-256 manifest verification
- rollback preparation through isolated recovery staging
- no automatic replacement or activation of an authority baseline
- runtime state export

## D6 - Integration

- Stage 8 FCF Web Console service composition
- Windows double-click entry point acceptance
- local CLI for start, stop, status, preflight, backup, snapshot, recovery, and
  export

## Recovery Procedure

1. Stop the owned local FCF service.
2. Create or select a verified snapshot.
3. Stage recovery into a new empty recovery directory.
4. Inspect manifest digests and registered evidence.
5. Obtain explicit Operator approval before changing any active configuration.
6. Re-run preflight and health checks.

Recovery staging never replaces the active baseline automatically.
