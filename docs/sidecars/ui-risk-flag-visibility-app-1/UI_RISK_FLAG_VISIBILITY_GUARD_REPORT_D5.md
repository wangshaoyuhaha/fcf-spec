# UI-RISK-FLAG-VISIBILITY-APP-1 D5 Visibility Guard Report

Status: D5
Scope: sidecar-only
Core boundary: P1-P47 frozen; no P48; no core mutation.
Safety boundary: paper-only, local-only, read-only, operator review required.

## Purpose

D5 defines a sidecar-only visibility guard report.

The report summarizes whether rendered UI, handoff, review, dashboard, export, archive, and operator-facing packets preserve protected risk metadata.

## Report requirements

The report must include:

- total_packets
- passed_packets
- failed_packets
- operator_review_required_packets
- display_blocked_packets
- visibility_errors
- packet_results

## Guard behavior

- Any missing protected risk metadata creates visibility_errors.
- Any REVIEW_REQUIRED downgrade creates visibility_errors.
- Any CIRCUIT_BREAK downgrade creates visibility_errors.
- Any removed risk_flags creates visibility_errors.
- Any removed reason_codes creates visibility_errors.
- Any missing operator review requirement creates visibility_errors.
- Packets with visibility_errors must be display blocked.

## D5 acceptance criteria

D5 passes when tests prove the report detects clean packets, failed packets, removed reason_codes, removed risk_flags, REVIEW_REQUIRED downgrade, CIRCUIT_BREAK downgrade, and missing operator review routing.
