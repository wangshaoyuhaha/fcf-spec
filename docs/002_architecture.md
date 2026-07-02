# BTC Finance Platform Architecture

Status: P0-D2

Mode: paper-only
Scope: architecture and module boundary definition

## Purpose

This project is a BTC / finance platform skeleton for paper-only analysis, operator review, and safe runtime validation.

It is independent from FCF / fcf-spec.

FCF / fcf-spec remains final archived and closed.

## Core Boundary

The platform must preserve this separation:

1. Input Layer
   - accepts paper-only market snapshots
   - accepts user-provided scenario information
   - does not connect to real exchange APIs

2. Analysis Layer
   - computes paper-only indicators, scenarios, and risk context
   - does not read real balances
   - does not read real positions

3. Policy / Risk Layer
   - checks safe_boundary
   - requires operator review
   - blocks unsafe behavior

4. Decision Draft Layer
   - may produce paper-only proposals
   - must not claim real execution
   - must not claim real financial impact

5. Output Layer
   - renders reports
   - must not convert paper-only output into live trading instructions

## Forbidden Behaviors

- real exchange API connection
- real API key storage
- wallet private key access
- real order placement
- real account balance read
- real position read
- real execution success claim
- real financial impact claim
- CI secret configuration
- production deployment
- live auto-trading
- operator review bypass
- policy, risk, or safe_boundary bypass

## Current P0-D2 Result

The first architecture boundary is documented.

Implementation remains minimal and paper-only.
