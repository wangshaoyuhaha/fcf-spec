# FCF PROJECT CONTROL CENTER

Version:
V0.1

Project:
FCF / Financial Cognitive Framework

Repository:
wangshaoyuhaha/fcf-spec

Local Path:
C:\Users\Admin\Desktop\btc_finance_platform

Branch:
main

System Type:
Multi-asset financial market paper-only cognitive framework


---

# 0. CONTROL CONSTITUTION

This document is the highest-level control document of FCF.

Purpose:

- maintain project truth
- maintain architecture boundary
- maintain safety rules
- maintain roadmap
- prevent uncontrolled expansion


All future FCF windows must read this file first.


Priority order:

1. FCF_PROJECT_CONTROL_CENTER.md
2. FCF_CURRENT_STATE_MASTER_FINAL.md
3. FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md
4. FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
5. Sidecar final state documents
6. Chat history


---

# 0.1 FCF SUPREME PRINCIPLES


## Human Sovereignty Principle


FCF is designed as:

A self-evolving digital asset cognition operating system.


FCF uses:

- Code for deterministic calculation
- AI for reasoning and explanation
- Governance for risk control


Final decision authority and real capital execution authority belong only to human operators.


FCF can:

- analyze
- explain
- simulate
- review
- archive


FCF cannot:

- automatically decide
- automatically execute
- automatically manage capital
- replace human responsibility


---

# Math by Code, Reasoning by LLM


Deterministic calculations must be completed by code.


Python owns:

- probability calculation
- scoring calculation
- risk calculation
- ranking calculation
- backtest statistics
- data quality calculation


AI owns:

- explanation
- summarization
- logical reasoning
- scenario discussion


AI cannot:

- invent numbers
- modify calculated results
- create unsupported data


---

# Data Quality Gate Principle


Bad data must not enter intelligence processing.


Flow:


Raw Data

ï¿½?

Data Quality Gate

ï¿½?

Validated Data

ï¿½?

Research Analysis

ï¿½?

AI Explanation

ï¿½?

Human Review


Invalid data must be:

- blocked
- quarantined
- reviewed


AI must never generate confident explanations from invalid data.


---

# 1. PROJECT IDENTITY


FCF is:

A multi-asset financial market paper-only research and cognition framework.


Supported assets:

- Stocks
- BTC
- Futures
- Other financial assets


FCF is NOT:

- trading bot
- execution system
- broker system
- exchange system
- automatic investment system


---

# 2. CURRENT CONFIRMED STATE


Branch:

main


Latest audit commit:

3123704 add final architecture gap audit report


Master current state commit:

414fee9 add master final current state


Validation:

ALL CHECKS PASSED


Pytest:

1505 passed


Git:

clean


Origin:

synced


Tag:

none


Release:

none


Deploy:

none


---

# 3. CORE FREEZE CONSTITUTION


P1-P47 Core is frozen.


Forbidden:

- P48 expansion
- core mutation
- score mutation
- reason code mutation
- risk flag deletion
- risk flag downgrade
- source overwrite


Future expansion must happen through Sidecar only.# 4. SIDE-CAR ARCHITECTURE REGISTRY


## Sidecar Expansion Rule


After P1-P47 Core Freeze:

All future capability expansion must use Sidecar architecture.


Sidecar can:

- read approved artifacts
- analyze
- explain
- review
- archive


Sidecar cannot:

- modify core
- replace core
- bypass governance
- create execution path



---

# 5. COMPLETED SIDECAR REGISTRY


## Data Foundation

- DATA-APP-1
- DATA-QUALITY-OPS-APP-1


Purpose:

Data intake

Data validation

Data quality control



---

## Research Intelligence


- STOCK-APP-1
- MARKET-SCENARIO-APP-1
- BACKTEST-REVIEW-APP-1
- SIGNAL-VALIDATION-APP-1
- WATCHLIST-LIFECYCLE-APP-1


Purpose:

Research artifact generation

Scenario analysis

Historical review

Signal validation



---

## AI Reasoning


- AI-CONTEXT-1


Purpose:

Explanation

Summary

Logical reasoning


Restrictions:

AI cannot:

- calculate authoritative numbers
- invent missing data
- modify score
- modify reason code
- remove risk flag



---

## Governance


- OPERATOR-REVIEW-APP-1
- MODEL-GOVERNANCE-APP-1
- RISK-EXPOSURE-APP-1
- PORTFOLIO-REVIEW-APP-1
- DECISION-AUDIT-APP-1


Purpose:

Human review

Risk governance

Audit traceability



---

## Workflow


- RESEARCH-WORKFLOW-APP-1



Purpose:

Research process organization



---

## Presentation and Archive


- UI-APP-1
- DASHBOARD-STATUS-APP-1
- REPORT-ARCHIVE-APP-1
- FINAL-COMPLETION-REVIEW-APP-1


Purpose:

Read-only display

Immutable archive

Final review record



---

# 6. SIDECAR TOPOLOGY RULE


FCF uses:

Directed Acyclic Graph (DAG)


Circular dependency is forbidden.



Official flow:


LOCAL PAPER DATA

ï¿½?

DATA QUALITY GATE

ï¿½?

RESEARCH LAYER

ï¿½?

AI REASONING LAYER

ï¿½?

GOVERNANCE REVIEW

ï¿½?

PRESENTATION

ï¿½?

ARCHIVE



---

# 7. FORBIDDEN DEPENDENCY


Forbidden:


AI-CONTEXT

ï¿½?

modify

ï¿½?

STOCK calculation



Reason:

AI reasoning cannot become calculation source.



Forbidden:


UI

ï¿½?

modify

ï¿½?

Risk Flag



Reason:

Presentation has no authority.



Forbidden:


Archive

ï¿½?

overwrite

ï¿½?

Historical Record



Reason:

Archive must remain immutable.



---

# 8. READ / WRITE CONTRACT


Universal rule:


Each Sidecar:


READ:

Only approved input artifacts.


WRITE:

Only own generated artifacts.


Forbidden:

Writing into another component output.



---

# 9. AUTHORITY MODEL


Python:

Owns deterministic calculation.


AI:

Owns explanation and reasoning.


Human Operator:

Owns final decision authority.



FCF never owns:

- real trading authority
- execution authority
- capital management authority



---

# 10. OPERATOR REVIEW STATES


Allowed:


REVIEW_REQUIRED

REVIEW_RECORDED

REJECTED

ARCHIVED


Avoid:


APPROVED


Reason:

Approval language may imply execution authorization.# 11. GAP REGISTER


Purpose:

Track known architecture gaps.

Gap does not mean failure.

Gap means:

Known area requiring future review or design.



---

## GAP-001

Name:

Complete Sidecar Dependency DAG


Description:

Finalize exact input and output dependency relationship for every Sidecar.


Status:

IN PROGRESS



---

## GAP-002

Name:

Correlation_ID Traceability System


Description:

Create unified audit trace identifier across:


- Data Snapshot
- Research Artifact
- AI Explanation
- Risk Review
- Operator Review
- Archive Record


Rule:

Correlation_ID is audit trace only.


Forbidden:

- execution ID
- order ID
- trading workflow ID


Status:

PLANNING



---

## GAP-003

Name:

Global Lifecycle State Model


Description:

Unify lifecycle states across:


- data quality
- research
- review
- archive


Status:

PLANNING



---

## GAP-004

Name:

Stock Mainstream Roadmap


Description:

Define future stock research direction.


Possible areas:


- data enhancement
- research workflow
- risk governance
- multi-market extension


Restriction:

No automatic trading.


Status:

PLANNING



---

# 12. BUG REGISTER


Purpose:

All bugs and architecture risks must be recorded here.


No important bug should exist only inside chat history.



Template:


BUG-ID:


Date:


Source:


Affected Component:


Description:


Severity:


Status:


Resolution:




---

# 13. IDEA INBOX


Purpose:

All new ideas enter here before development.



Idea Lifecycle:


PROPOSED

ï¿½?

REVIEWING

ï¿½?

ACCEPTED

or

REJECTED

or

DEFERRED



Template:


IDEA-ID:


Date:


Source:


Description:


Category:


Status:


Decision:




---

# 14. ACCEPTED ARCHITECTURE IDEAS


## IDEA-A001

Four Zone Sidecar Architecture


Status:

Accepted


Description:


18 Sidecars are grouped into:


1. Data Ingestion & Quarantine


2. Context & Interpretation


3. Governance & Review Gate


4. Presentation & Immutable Archive




---

## IDEA-A002

Sidecar DAG Rule


Status:

Accepted


Description:


All Sidecar dependency must be directional.

Circular dependency is forbidden.




---

## IDEA-A003

Math by Code, Reasoning by LLM


Status:

Accepted


Description:


Python owns deterministic calculation.

AI owns explanation and reasoning.




---

## IDEA-A004

Data Quality Gate First


Status:

Accepted


Description:


Invalid data must be blocked before analysis.




---

# 15. REJECTED / MODIFIED IDEAS


## REJECTED-001


Idea:

AI directly generates financial scores.


Decision:

Rejected.


Reason:

Violates deterministic calculation principle.




---

## REJECTED-002


Idea:

AI explanation can modify original research result.


Decision:

Rejected.


Reason:

Explanation layer cannot become calculation layer.




---

## REJECTED-003


Idea:

Operator review equals automatic authorization.


Decision:

Rejected.


Reason:

Human review is not execution permission.




---

# 16. FUTURE ROADMAP


Current Phase:


Architecture Governance Phase



Current Focus:


FCF Project Control Center



No feature development.



---

Future Candidates:


Priority 0:

SIDECAR-TOPOLOGY-REVIEW-APP-1



Priority 1:

STOCK-MAINSTREAM-ROADMAP-APP-1



Priority 2:

DATA-SOURCE-TRUST-REVIEW-APP-1



Priority 3:

OPERATOR-DECISION-REVIEW-FORMAT-APP-1



Priority 4:

ARCHIVE-INDEX-CONSOLIDATION-APP-1




---

# 17. CHANGE MANAGEMENT RULE


No direct development from chat discussion.



Required process:


New Idea

ï¿½?

Control Center Record

ï¿½?

Architecture Review

ï¿½?

Accept / Reject / Defer

ï¿½?

Roadmap

ï¿½?

Development



---

# 18. NEXT WINDOW PROTOCOL


Every new FCF conversation must start with:


Continue FCF / Financial Cognitive Framework project.


First read:


1.

FCF_PROJECT_CONTROL_CENTER.md


2.

FCF_CURRENT_STATE_MASTER_FINAL.md


3.

FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md


4.

FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md


5.

FCF_NEW_WINDOW_CHAT_PROMPT.md



If conflicts exist:


Stop.

Report conflict.

Do not continue automatically.



---

# 19. CHANGE LOG


## 2026-07-07


Created:

FCF Project Control Center V0.1


Added:


- Project Constitution
- Human Sovereignty Principle
- Math by Code, Reasoning by LLM
- Data Quality Gate
- Core Freeze Rules
- Sidecar Registry
- Sidecar DAG Rules
- Read/Write Contract
- Gap Register
- Bug Register
- Idea Management System
- Future Roadmap


---
# 20. SIDECAR DEPENDENCY MATRIX

V0.2-D1 Architecture Draft Accepted.

## Four Zone Topology

Zone A:
Data Foundation

- DATA-APP-1
- DATA-QUALITY-OPS-APP-1
- SIGNAL-VALIDATION-APP-1


Zone B:
Research Intelligence

- STOCK-APP-1
- MARKET-SCENARIO-APP-1
- WATCHLIST-LIFECYCLE-APP-1
- BACKTEST-REVIEW-APP-1


Zone C:
Governance Review Gate

- AI-CONTEXT-1
- MODEL-GOVERNANCE-APP-1
- RISK-EXPOSURE-APP-1
- PORTFOLIO-REVIEW-APP-1
- OPERATOR-REVIEW-APP-1
- DECISION-AUDIT-APP-1


Zone D:
Presentation and Immutable Archive

- UI-APP-1
- DASHBOARD-STATUS-APP-1
- RESEARCH-WORKFLOW-APP-1
- REPORT-ARCHIVE-APP-1
- FINAL-COMPLETION-REVIEW-APP-1


## Dependency Rules

Allowed direction:

DATA
ï¿½ï¿½
QUALITY
ï¿½ï¿½
RESEARCH
ï¿½ï¿½
AI CONTEXT
ï¿½ï¿½
GOVERNANCE
ï¿½ï¿½
PRESENTATION
ï¿½ï¿½
ARCHIVE


Forbidden:

AI-CONTEXT-1 -> STOCK-APP-1

Reason:
AI explanation cannot modify calculation results.


UI-APP-1 -> CORE

Reason:
Presentation layer has no mutation authority.


ARCHIVE -> SOURCE

Reason:
Archive cannot rewrite history.


OPERATOR -> EXECUTION

Reason:
Review is not execution.


## Artifact Ownership

Every artifact has one owner.

Examples:

validated_dataset:
DATA-APP-1

ranked_watchlist:
STOCK-APP-1

explanation_report:
AI-CONTEXT-1

risk_review_packet:
RISK-EXPOSURE-APP-1

operator_review_record:
OPERATOR-REVIEW-APP-1

archive_manifest:
REPORT-ARCHIVE-APP-1


## Artifact Lifecycle

CREATED

ï¿½ï¿½

VALIDATED

ï¿½ï¿½

REVIEWED

ï¿½ï¿½

ARCHIVED

ï¿½ï¿½

IMMUTABLE


Immutable rule:

Archived artifacts cannot be overwritten.


## Decision History

P1-P47 Core Freeze:

Future expansion must use Sidecar only.


AI Boundary:

AI explains.
AI does not modify scores or risk flags.


Human Governance:

Operator retains final review authority.


## CHANGE LOG

2026-07-07

Added:

- Sidecar Dependency Matrix
- Artifact Ownership Model
- Artifact Lifecycle Model
- Decision History Framework

Status:

FCF_PROJECT_CONTROL_CENTER_V0.2
## Artifact Flow Model

FCF artifacts follow a one-way governance flow:

Input Source

â†“

Validated Artifact

â†“

Research Artifact

â†“

Explanation Artifact

â†“

Review Artifact

â†“

Audit Artifact

â†“

Archive Artifact

Rules:

- Artifact flow is unidirectional.
- Downstream artifacts must not contaminate upstream layers.
- Historical artifacts must not modify previous stages.
- Archive artifacts are for traceability and review only.


## Artifact Ownership Model

Every artifact must have:

- unique owner
- clear generator
- defined read scope
- defined lifecycle


| Artifact | Owner |
| --- | --- |
| validated_dataset | DATA-APP-1 |
| quality_report | DATA-QUALITY-OPS-APP-1 |
| ranked_watchlist | STOCK-APP-1 |
| explanation_report | AI-CONTEXT-1 |
| risk_review_packet | RISK-EXPOSURE-APP-1 |
| operator_review_record | OPERATOR-REVIEW-APP-1 |
| archive_manifest | REPORT-ARCHIVE-APP-1 |


Artifact ownership means responsibility for generation and version control.

Ownership does not grant permission to modify Core outputs.


## Artifact Lifecycle Model

Standard lifecycle:

CREATED

â†“

VALIDATED

â†“

REVIEWED

â†“

ARCHIVED

â†“

IMMUTABLE


After ARCHIVED:

Forbidden:

- overwrite
- delete
- silent modification

Archived artifacts are immutable governance records.


## Artifact Modification Rules

Allowed:

- Artifact owner may create a new version.
- New review packets may be generated.
- New archive snapshots may be created.


Forbidden:

- modifying historical artifacts
- overwriting existing archives
- deleting audit records
- reducing risk information
- modifying Core outputs
- changing score results
- changing reason codes
- deleting or downgrading risk flags
## Correlation_ID Traceability Model

Correlation_ID is a governance traceability identifier.

Purpose:

- audit traceability identifier
- artifact chain identifier

Correlation_ID connects:

Data Snapshot

¡ý

Validated Artifact

¡ý

Research Artifact

¡ý

AI Explanation

¡ý

Risk Review

¡ý

Operator Review

¡ý

Archive


Rules:

- Correlation_ID is only for governance traceability.
- Correlation_ID is not an execution identifier.
- Correlation_ID does not create trading authority.

Forbidden usage:

- execution id
- order id
- position id
- broker id


## Bug History Register

FCF maintains a centralized Bug History Register.

Required fields:

| Field | Description |
| --- | --- |
| BUG-ID | Unique bug identifier |
| Date | Discovery date |
| Source | Origin of issue |
| Module | Related component |
| Description | Problem description |
| Severity | Impact level |
| Status | Current state |
| Resolution | Handling result |


Purpose:

- Preserve historical bug lessons.
- Prevent repeated failures.
- Move critical knowledge from chat history into project governance.


## Architecture Decision Record

FCF maintains Architecture Decision Records.


### Core Freeze Decision

P1-P47 Core is frozen.

Future expansion uses controlled Sidecars only.


### Sidecar Architecture Decision

FCF uses:

Frozen Core

+

Controlled Sidecars


### AI Boundary Decision

AI provides:

- explanation
- summary
- reasoning
- context analysis

AI must not:

- modify scores
- modify reason codes
- remove risk flags


### Human Governance Decision

Operator review remains mandatory.

No automated approval bypass.

