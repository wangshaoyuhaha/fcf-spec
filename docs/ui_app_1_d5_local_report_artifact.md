# UI-APP-D5 Local Read-Only Report Artifact

## Purpose

UI-APP-D5 generates local read-only report artifacts for operator review.

## Outputs

- local HTML report
- local text report
- local manifest JSON

## Safety boundary

The report artifact is display-only.

It does not provide:

- buy buttons
- sell buttons
- order buttons
- broker connection
- exchange connection
- credential access
- real execution
- core mutation
- operator review bypass

The artifact remains paper-only, local-only, read-only, sidecar-only, and operator-review-required.
