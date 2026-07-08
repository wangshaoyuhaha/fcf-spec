# SIDECAR-DAG-DEPENDENCY-GUARD-APP-1 D4 Scanner Repair

## Purpose

This repair reduces false positives in the D4 import boundary scanner.

## Fixed Issue

Safety boundary documentation and tests may contain forbidden words such as api_key, broker_api, exchange_api, or real_trading.

The scanner should not fail because a document says these items are forbidden.

## Repair Rule

The scanner blocks enabled risk patterns only when the line looks like assignment or callable activation.

Examples blocked:

- real_trading = True
- exchange_api = True
- api_key = 'forbidden'
- broker_api()

Examples allowed:

- no real trading
- no exchange API
- no API key
- forbidden: broker API

## Safety Boundary

- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no source mutation
- no score mutation
- no reason code mutation
- no risk flag deletion
- no risk flag downgrade
- no real trading
- no real execution
- no broker API
- no exchange API
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy
