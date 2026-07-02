# BTC Finance Platform

Status: new independent BTC / finance platform project.

This is not FCF / fcf-spec.

FCF / fcf-spec is already final archived and closed at commit 3287896.

## Project Goal

Build a paper-only BTC / finance analysis and operator-review platform.

## Safety Boundary

This project must remain paper-only until explicitly changed by a reviewed future decision.

It must not:

- connect to real exchange APIs
- store real API keys
- read wallet private keys
- place real orders
- read real account balances
- read real positions
- claim real execution success
- claim real financial impact
- configure CI secrets
- deploy to production
- auto-trade live capital
- bypass operator review
- bypass policy, risk, or safe_boundary checks
- interpret paper-only results as real trading signals
- interpret paper-only results as real fills or executions
