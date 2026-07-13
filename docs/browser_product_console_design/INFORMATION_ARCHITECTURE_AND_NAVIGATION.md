# Browser Product Console Information Architecture and Navigation

## Phase

BROWSER-PRODUCT-CONSOLE-DESIGN-APP-1

## Delivery

D2 - Information Architecture and Navigation

## Status

DESIGN_ONLY

NO_RUNTIME_IMPLEMENTATION

## Product shell

The future Browser Product Console uses one governed product shell.

The shell contains:

- product identity
- current workspace
- current user role
- environment badge
- paper-only badge
- Operator review status
- provider-health summary
- cost-status summary
- global search
- notification center
- primary navigation
- contextual secondary navigation
- immutable audit shortcut

The product shell must always display PAPER_ONLY.

The product shell must never display a live-trading mode.

## Primary navigation

### Overview

Route concept:

/overview

Purpose:

- system status summary
- active paper-only research count
- review-required count
- provider-health summary
- cost-status summary
- recent governed activity
- unresolved risk flags
- unresolved contradictions

Overview is informational.

Overview must not provide automatic approval or automatic execution.

### Data Workspace

Route concept:

/data-workspace

Purpose:

- prepare local paper-data submissions
- inspect source identity
- inspect privacy classification
- inspect licensing status
- inspect Schema eligibility
- inspect validation results
- prepare an approved research input package

The browser must not directly browse unrestricted local filesystem paths.

### Research Runs

Route concept:

/research-runs

Purpose:

- list governed paper-only workflows
- inspect deterministic workflow status
- inspect checkpoints
- inspect current stage
- inspect failure reason
- inspect Operator review requirement
- prevent duplicate workflow creation after refresh

Each run is identified by a stable run identifier.

### AI Comparison

Route concept:

/ai-comparison

Purpose:

- compare registered AI outputs
- display model-slot identity
- display model version
- display Prompt version
- display evaluation baseline
- display provider-health status
- display privacy and cloud eligibility
- display cost status
- preserve source candidate identity

AI Comparison must not select, route, invoke, or switch models automatically.

### Evidence and Risk

Route concept:

/evidence-risk

Purpose:

- display correlation identifier
- display evidence references
- display provenance
- display deterministic risk flags
- display contradictions
- display missing-artifact blockers
- display validation baseline
- distinguish raw evidence from summaries

Risk flags must not be hidden by summary text.

### Operator Review

Route concept:

/operator-review

Purpose:

- display complete review packet
- display deterministic findings
- display controlled AI assistance
- display evidence and provenance
- display risk flags and contradictions
- record approve, reject, or return-for-revision decisions
- record human rationale
- record manual fallback choice

No review action is complete without explicit human confirmation.

### Reports and Archive

Route concept:

/reports-archive

Purpose:

- preview paper-only reports
- inspect report versions
- inspect archive eligibility
- inspect immutable archive references
- inspect export readiness
- distinguish draft, review-required, approved, rejected, and archived states

The browser must not archive automatically.

### Governance

Route concept:

/governance

Purpose:

- inspect registered model slots
- inspect Prompt versions
- inspect Schema versions
- inspect evaluation baselines
- inspect configuration snapshots
- inspect Policy Eligibility results
- inspect role assignments
- inspect provider-health and cost policies

Governance visibility does not grant research or review authority.

### Audit History

Route concept:

/audit-history

Purpose:

- inspect immutable activity history
- inspect decision history
- inspect configuration history
- inspect evidence-chain history
- inspect Operator rationale
- inspect failed and blocked actions
- inspect correlation identifiers

Audit records must be read-only from the browser.

## Secondary navigation

Secondary navigation is contextual.

Examples:

- Research Run Summary
- Inputs
- Deterministic Results
- AI Comparison
- Evidence
- Risk
- Review Packet
- Report
- Audit Trail

Changing a tab must not start a workflow or mutate an artifact.

## Role-based visibility

Viewer:

- Overview
- Evidence and Risk
- approved Reports and Archive
- Audit History

Research Analyst:

- Overview
- Data Workspace
- Research Runs
- AI Comparison
- Evidence and Risk
- draft Reports and Archive

Operator Reviewer:

- Overview
- Research Runs
- AI Comparison
- Evidence and Risk
- Operator Review
- Reports and Archive
- Audit History

Governance Administrator:

- Overview
- Governance
- Evidence and Risk
- Reports and Archive
- Audit History

Visibility does not replace server-side authorization.

Hidden navigation does not count as an authorization control.

## Navigation state

Every page must preserve:

- current workspace identifier
- current run identifier when applicable
- current correlation identifier when applicable
- current artifact identifier when applicable
- current user role
- paper-only status
- review status
- validation status

A browser refresh must restore display state without repeating an action.

A deep link may open an existing governed artifact.

A deep link must not create, approve, route, invoke, archive, or execute.

## Status language

Allowed status labels include:

- DRAFT
- VALIDATING
- BLOCKED
- REVIEW_REQUIRED
- APPROVED
- REJECTED
- RETURNED_FOR_REVISION
- ARCHIVE_ELIGIBLE
- ARCHIVED
- PROVIDER_UNAVAILABLE
- POLICY_INELIGIBLE

LIVE, EXECUTING, ORDER_PLACED, POSITION_OPEN, and AUTO_APPROVED are forbidden.

## Empty and failure states

Every primary page must define:

- loading state
- empty state
- permission-denied state
- validation-failed state
- provider-unavailable state
- missing-artifact state
- stale-data state

Failures must remain visible.

A missing artifact must not be represented as a successful empty state.

## D2 acceptance contract

D2 is accepted only when:

- primary navigation is explicit
- route concepts are explicit
- role visibility is explicit
- authorization remains outside presentation logic
- refresh cannot repeat actions
- risk flags remain visible
- paper-only status remains globally visible
- no runtime implementation is created
- no web server is started
- no HTTP port is opened
- no model is invoked
