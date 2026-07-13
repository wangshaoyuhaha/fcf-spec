# Browser Product Console Boundary and Role Contract

## Phase

BROWSER-PRODUCT-CONSOLE-DESIGN-APP-1

## Delivery

D1 - Boundary, User Roles, and Prohibited Capabilities

## Status

DESIGN_ONLY

NO_RUNTIME_IMPLEMENTATION

## Authority

The deterministic FCF engine remains the calculation and policy authority.

Registered artifacts remain the evidence authority.

The Operator remains the final review authority.

The Browser Product Console is a presentation and human-review interface only.

It must not silently create, modify, approve, route, execute, or archive an
FCF decision.

## User roles

### Viewer

May inspect approved paper-only reports, visible risk flags, evidence,
workflow status, and immutable audit history.

May not change configuration, start workflows, or submit approval decisions.

### Research Analyst

May prepare paper-data submissions, start explicitly permitted paper-only
research workflows, inspect deterministic and controlled AI outputs, and
prepare reports for Operator review.

May not bypass validation, approve their own governed output, invoke an
unregistered model, or activate automatic routing.

### Operator Reviewer

May approve, reject, or return a paper-only report, inspect evidence and risk
flags, and record review rationale.

May not authorize real execution, suppress mandatory risk flags, or delegate
approval to an AI model.

### Governance Administrator

May manage role assignments and registered configuration, model-slot,
Prompt-version, Schema-version, and evaluation-baseline visibility.

May not modify frozen P1-P47 Core, create P48, remove Operator review, or
enable live trading.

## Separation of duties

Research preparation, deterministic evaluation, controlled AI assistance,
Operator review, governance administration, and archival evidence remain
separate authority domains.

An AI result is not a deterministic decision.

A Research Analyst action is not an Operator approval.

A Governance Administrator configuration is not a research conclusion.

## Prohibited capabilities

The console must not provide:

- real broker or exchange connectivity
- real order placement
- balance or position access
- wallet or private-key access
- trading credential entry
- automatic model selection, switching, routing, or invocation
- automatic Prompt execution
- automatic approval
- automatic archive
- arbitrary shell, Python, or PowerShell execution
- direct Git mutation
- hidden background execution
- HTTP service startup during this design phase
- port binding during this design phase
- tag, release, or deployment actions

## Runtime boundary

It does not start a web server.

It does not open a network port.

It does not create an API runtime.

It does not invoke a model.

## Permanent acceptance boundaries

- paper-only remains mandatory
- Operator review remains mandatory
- no P1-P47 frozen Core file is changed
- no P48 is created
- no runtime implementation is created
