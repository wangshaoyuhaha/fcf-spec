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


## Change Control Rule

All FCF changes must follow controlled governance.

Required flow:

Idea

¡ý

Review

¡ý

Accepted / Rejected / Deferred

¡ý

Control Center Update

¡ý

Implementation


Forbidden:

- Direct implementation from chat discussion.
- Unreviewed architecture change.
- Core modification without governance approval.
- Sidecar expansion without registration.


## Control Center Update Policy

FCF_PROJECT_CONTROL_CENTER.md is the governance index and architecture baseline.

Updates are required when:

- architecture rules change
- safety boundaries change
- Sidecar registry changes
- major decisions are made
- important bugs are recorded


The Control Center does not replace detailed documents.

It provides:

- project state index
- architecture governance
- decision tracking
- change history reference


All future FCF windows must read:

1. FCF_PROJECT_CONTROL_CENTER.md
2. FCF_CURRENT_STATE_MASTER_FINAL.md
3. FCF_FINAL_ARCHITECTURE_GAP_AUDIT_REPORT.md
4. FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
5. FCF_NEW_WINDOW_CHAT_PROMPT.md

before making project changes.


## FCF Control Center Version History

### V0.1 Foundation

Completed:

- Project identity established.
- Core freeze governance recorded.
- Sidecar registry created.
- Safety boundary recorded.
- Idea and gap management introduced.


### V0.2 Architecture Governance

Completed:

- Sidecar topology governance added.
- Dependency rules added.
- Read / Write contract established.
- Artifact ownership concept introduced.
- Architecture decision framework introduced.


### V0.3 Governance Enhancement

Completed:

- Artifact flow governance added.
- Artifact lifecycle rules added.
- Correlation_ID traceability framework added.
- Bug history register added.
- Architecture decision records added.
- Change control policy added.


Current status:

FCF Control Center is the governance baseline for project evolution.

Future changes must follow:

Review

¡ý

Decision

¡ý

Control Center Update

¡ý

Implementation



## Complete Sidecar Dependency DAG

### Sidecar Dependency Direction

FCF Sidecar dependency follows a forward-only artifact flow model.


Each Sidecar must have:

- defined artifact ownership
- defined output artifact
- defined consumer scope

A Sidecar may read approved upstream artifacts.

A Sidecar must not mutate upstream artifacts.

---

### Cross-Layer Sidecar Definition

The following Sidecars are cross-layer governance nodes:

- AI-CONTEXT-1
- DECISION-AUDIT-APP-1
- MODEL-GOVERNANCE-APP-1

These nodes may perform cross-layer read operations for:

- explanation
- governance review
- audit traceability
- model review

They must not:

- modify upstream results
- change score outputs
- change reason_codes
- delete or downgrade risk_flags
- overwrite source artifacts

---

### DAG Rules

Allowed:

Forward Read Dependency


Forbidden:

Circular Dependency

Backward Mutation

Hidden Dependency


FCF Sidecar architecture requires an acyclic dependency graph.

Each dependency must be explicit and traceable.

---

### Dependency Status

Current status:

OPEN

Future refinement required:

- field-level dependency definition
- artifact schema contract
- artifact version contract


## Artifact Dependency Matrix

| Artifact | Producer Sidecar | Consumer Sidecar |
| --- | --- | --- |
| validated_dataset | DATA-APP-1 | DATA-QUALITY-OPS-APP-1, STOCK-APP-1 |
| quality_report | DATA-QUALITY-OPS-APP-1 | SIGNAL-VALIDATION-APP-1, MODEL-GOVERNANCE-APP-1 |
| ranked_watchlist | STOCK-APP-1 | WATCHLIST-LIFECYCLE-APP-1, AI-CONTEXT-1 |
| explanation_report | AI-CONTEXT-1 | OPERATOR-REVIEW-APP-1, UI-APP-1 |
| risk_review_packet | RISK-EXPOSURE-APP-1 | PORTFOLIO-REVIEW-APP-1, OPERATOR-REVIEW-APP-1 |
| operator_review_record | OPERATOR-REVIEW-APP-1 | DECISION-AUDIT-APP-1, REPORT-ARCHIVE-APP-1 |
| archive_manifest | REPORT-ARCHIVE-APP-1 | FINAL-COMPLETION-REVIEW-APP-1 |

## Bug History Register

Fields:

- BUG-ID
- Date
- Source
- Module
- Description
- Severity
- Status
- Resolution

Rule:

Historical bugs must be migrated into project governance records.
Chat history is not the only source of truth.

## Roadmap Governance Framework

Idea Lifecycle:

PROPOSED

¡ý

REVIEWING

¡ý

ACCEPTED

¡ý

REJECTED

¡ý

DEFERRED

Rule:

Future ideas must enter governance review before implementation.


# Artifact Schema Contract

## Artifact Schema Governance

Every Artifact must contain:

- artifact_id
- artifact_type
- owner
- producer
- consumer
- version
- created_time
- validation_status
- lifecycle_status

Principles:

- Artifact must be traceable.
- Artifact must be verifiable.
- Artifact must not be silently overwritten.


# Artifact Version Contract

## Version Governance

Artifact versions follow:

v1
v2
v3

Allowed:

- create new artifact version

Forbidden:

- overwrite previous artifact
- silent modification
- delete historical artifact


# Field Level Dependency Matrix

## Field Dependency Governance

Purpose:

Upgrade dependency governance from Sidecar level to Field level.

Each governed field should define:

- producer
- consumer
- validator
- archive owner

This phase defines governance rules only.
No business field mutation is allowed.


# Historical Bug Migration Framework

## Historical Bug Migration

Historical project issues should be migrated into Bug History Register.

Required fields:

- BUG-ID
- Date
- Source Window
- Module
- Description
- Severity
- Status
- Resolution


# Architecture Decision Record Expansion

## Architecture Decision Record

Required fields:

Decision:

Why:

Impact:

Status:


## Core Freeze Decision

P1-P47 Core remains frozen.

No P48 expansion.

No core mutation.


## Sidecar Architecture Decision

Future extension uses:

Frozen Core
+
Controlled Sidecars


## AI Boundary Decision

AI provides:

- explanation
- summary
- reasoning

AI cannot:

- modify score
- modify reason codes
- remove risk flags


## Human Governance Decision

Operator review remains mandatory.


## Paper-only Decision

FCF remains:

paper-only
local-only
read-only
sidecar-only

No execution capability.

# FCF CONTROL CENTER V0.6 Governance Enhancement

## Governance Audit Checklist

Before any future change, extension, or governance update, the following checks are required:

- [ ] No violation of P1-P47 Core Freeze
- [ ] No violation of Sidecar-only extension rule
- [ ] No circular dependency introduced
- [ ] No backward mutation introduced
- [ ] No historical Artifact modification
- [ ] Artifact Owner exists
- [ ] Artifact Version Contract exists
- [ ] Operator Review requirement evaluated
- [ ] Paper-only boundary preserved


## Control Center Consistency Rules

The Control Center governance layer should maintain consistency between:

- Sidecar Registry and Dependency DAG
- Artifact ownership and lifecycle status
- Roadmap status and decision records
- Architecture decisions and current state


These rules define governance expectations only.

No automatic execution or automatic modification is allowed.


## Artifact Schema Template

All governance artifacts should contain the following metadata:

- artifact_id
- artifact_type
- owner
- producer
- consumer
- version
- created_time
- validation_status
- lifecycle_status


Artifact schema is governance metadata only.

No business trading fields are defined here.


## Historical Bug Migration Policy

Historical issues migrated into the Bug History Register must focus on:

- Architecture related bugs
- Safety boundary related bugs
- Governance process related bugs


Required fields:

- BUG-ID
- Date
- Source Window
- Module
- Description
- Severity
- Status
- Resolution


Normal conversation records are not migrated unless they represent reusable governance knowledge.


## Control Center V1.0 Roadmap

Target:

FCF_PROJECT_CONTROL_CENTER.md becomes the long-term governance index.

V1.0 scope:

- Current State
- Architecture Map
- Core Constitution
- Sidecar Registry
- Dependency Governance
- Artifact Governance
- Bug History
- Decision History
- Roadmap
- Audit Checklist


V1.0 is a governance milestone only.

It does not represent feature completion, deployment, or production execution.

# FCF CONTROL CENTER V0.7 Governance Enhancement

## Global Architecture Map

FCF Architecture:

FCF Core P1-P47 Frozen

¡ý

Sidecar Governance Layer

¡ý

Artifact Governance Layer

¡ý

Operator Review Layer

¡ý

Archive Layer


Core:
Responsible for deterministic computation.

Sidecar:
Responsible for controlled extension.

Governance:
Responsible for constraint and review.

Archive:
Responsible for historical preservation.


## Correlation_ID Contract

Correlation_ID is defined as:

- audit traceability identifier
- artifact chain identifier


Trace chain:

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


Restrictions:

Correlation_ID is not:

- order id
- execution id
- position id
- trading id


## Artifact Governance Contract

Every Artifact must be:

- identifiable
- owned
- versioned
- validated
- traceable
- immutable after archive


Forbidden:

- silent overwrite
- delete history
- ownerless artifact


## Bug Archive Migration Status

Migration states:

- Pending
- Migrated
- Reviewed
- Closed


Migration scope:

- architecture bugs
- safety boundary bugs
- workflow governance bugs


Do not migrate ordinary chat content.


## FCF CONTROL CENTER V1.0 Blueprint

Target structure:

1. Project Identity

2. Core Constitution

3. Architecture Map

4. Sidecar Registry

5. Dependency Governance

6. Artifact Governance

7. Bug History

8. Decision History

9. Roadmap

10. Change Control


V1.0 planning only.

No feature development.

No core modification.


# FCF CONTROL CENTER V0.8 FINAL HARDENING

## Control Center Consistency Audit

¼ì²éÏîÄ¿ÖÎÀíÎÄ¼þÒ»ÖÂÐÔ£º

- Project Identity consistency
- Core Freeze consistency
- Sidecar Registry consistency
- Dependency Matrix consistency
- Artifact Ownership consistency
- Artifact Lifecycle consistency
- Decision Record consistency
- Roadmap status consistency
- Bug Register consistency


## Full Governance Checklist

ÈÎºÎÎ´À´±ä»¯±ØÐë¼ì²é£º

- ÊÇ·ñÎ¥·´ P1-P47 Core Freeze
- ÊÇ·ñÐèÒª Sidecar À©Õ¹
- ÊÇ·ñÓ°Ïì Artifact
- ÊÇ·ñÓ°Ïì Dependency DAG
- ÊÇ·ñ²úÉú Circular Dependency
- ÊÇ·ñÈ±ÉÙ Owner
- ÊÇ·ñÈ±ÉÙ Version Contract
- ÊÇ·ñÐèÒª Operator Review
- ÊÇ·ñÎ¥·´ Paper-only Boundary


## Historical Architecture Decision Migration

### Core Freeze Decision

Decision:
P1-P47 Core Freeze

Why:
±£³ÖºËÐÄÎÈ¶¨£¬·ÀÖ¹ºËÐÄÆ¯ÒÆ¡£

Impact:
Î´À´À©Õ¹Ö»ÄÜÍ¨¹ý Sidecar¡£

Status:
Accepted


### Sidecar Architecture Decision

Decision:
Frozen Core + Controlled Sidecars

Why:
À©Õ¹ÄÜÁ¦²»ÎÛÈ¾ºËÐÄ¡£

Impact:
ÏµÍ³±£³ÖÄ£¿é¸ôÀë¡£

Status:
Accepted


### AI Boundary Decision

Decision:
AI Explanation Boundary

Why:
AI¸ºÔð½âÊÍ¡¢×Ü½á¡¢ÍÆÀí£¬²»¸ºÔð¼ÆËãºÍ¾ö²ß¡£

Impact:
±£³ÖÈ·¶¨ÐÔ¼ÆËãºÍÈË¹¤ÖÎÀí¡£

Status:
Accepted


### Human Governance Decision

Decision:
Operator Review Required

Why:
×îÖÕÔðÈÎ±£ÁôÔÚÈËÀà¡£

Impact:
½ûÖ¹×Ô¶¯ÉóÅú¡£

Status:
Accepted


### Paper-only Decision

Decision:
Paper-only System Boundary

Why:
±ÜÃâ½øÈëÕæÊµ×Ê½ðÖ´ÐÐ¡£

Impact:
±£³ÖÑÐ¾¿ºÍÉó¼ÆÊôÐÔ¡£

Status:
Accepted


## FCF CONTROL CENTER V1.0 Final Structure

¹æ»®½á¹¹£º

1. Project Identity

2. Current State

3. Core Constitution

4. Architecture Map

5. Sidecar Registry

6. Dependency Governance

7. Artifact Governance

8. Audit Checklist

9. Bug History

10. Decision History

11. Roadmap Governance

12. Change Control

Status:
Planning Only


# FCF CONTROL CENTER V1.0 FINAL BASELINE

Status:

FINAL BASELINE


FCF_PROJECT_CONTROL_CENTER.md is the highest governance index of FCF.


It defines:

- project identity
- architecture boundaries
- core governance rules
- sidecar governance
- artifact governance
- change control process


It is not:

- execution engine
- trading system
- automatic decision system


Future changes must follow:

Proposal

¡ý

Review

¡ý

Accepted

¡ý

Controlled Update


Core Freeze remains:

P1-P47 frozen.


Extension rule:

Future capability expansion must follow controlled Sidecar governance.


Safety Boundary remains:

paper-only

local-only

read-only

sidecar-only

operator review required


<!-- FCF_CC_DIFY_UI_HANDOFF_APP_1_MAINLINE_SYNC_BEGIN -->

## Mainline Sync: DIFY-UI-HANDOFF-APP-1

Status: completed and merged into main.

Mainline state:

- Branch: main
- Latest merge commit: 669b9e7 merge DIFY-UI-HANDOFF-APP-1 into main
- Push status: success
- Push range: 45dea72..669b9e7 main -> main
- Validation:
  - python scripts/run_all_checks.py = ALL CHECKS PASSED
  - python -m pytest -q = 1547 passed
- Final git status: clean after restoring generated runtime files
- Tag: none
- Release: none
- Deploy: none

Completed sidecar commits:

- 4330227 add DIFY-UI-HANDOFF-D1 contract
- f045fda add DIFY-UI-HANDOFF-D2 source loader
- b06487d add DIFY-UI-HANDOFF-D3 Dify IO contract
- 7fa0976 fix DIFY-UI-HANDOFF-D3 safe blocked response validation
- 2bbeb08 add DIFY-UI-HANDOFF-D4 prompt template
- d1988af add DIFY-UI-HANDOFF-D5 manual workflow guide
- a768eb2 add DIFY-UI-HANDOFF-D6 final closeout
- 669b9e7 merge DIFY-UI-HANDOFF-APP-1 into main

Final files:

- FCF_CURRENT_STATE_DIFY_UI_HANDOFF_APP_1_FINAL.md
- apps/dify_ui_handoff_app_1/
- docs/dify_ui_handoff_app_1/
- tests/test_dify_ui_handoff_app_1_d1_contract.py
- tests/test_dify_ui_handoff_app_1_d2_source_loader.py
- tests/test_dify_ui_handoff_app_1_d3_dify_contract.py
- tests/test_dify_ui_handoff_app_1_d4_prompt_template.py
- tests/test_dify_ui_handoff_app_1_d5_manual_workflow_guide.py
- tests/test_dify_ui_handoff_app_1_d6_final_closeout.py

Safety confirmation:

- DIFY-UI-HANDOFF-APP-1 is repo-side handoff only.
- It does not open Dify.
- It does not deploy.
- It does not create a Dify app automatically.
- It does not write through the Dify API.
- It does not add real trading capability.
- It remains paper-only, local-only, read-only, and operator-review-only.

Deferred backlog:

- Next sidecar planning: required later, but no automatic development.
- Dify local configuration hardening: optional and deferred until the operator is ready to configure Dify/Ollama locally.

<!-- FCF_CC_DIFY_UI_HANDOFF_APP_1_MAINLINE_SYNC_END -->

<!-- FCF_CC_SIDECAR_TOPOLOGY_REVIEW_APP_1_MAINLINE_SYNC_BEGIN -->

## Mainline Sync: SIDECAR-TOPOLOGY-REVIEW-APP-1

Status: completed and merged into main.

Mainline state:

- Branch: main
- Latest merge commit: df56963 merge SIDECAR-TOPOLOGY-REVIEW-APP-1 into main
- Push status: success
- Push range: 0c40104..df56963 main -> main
- Final git status: clean
- Tag: none
- Release: none
- Deploy: none

Completed sidecar commits:

- b9388f1 add SIDECAR-TOPOLOGY-REVIEW-D1 contract
- ae6f7e6 add SIDECAR-TOPOLOGY-REVIEW-D2 inventory
- d157800 add SIDECAR-TOPOLOGY-REVIEW-D3 isolation zones
- 6186ea6 add SIDECAR-TOPOLOGY-REVIEW-D4 dependency dag
- f0b8b87 add SIDECAR-TOPOLOGY-REVIEW-D5 queue gates
- 07e53c3 add SIDECAR-TOPOLOGY-REVIEW-D6 final closeout
- df56963 merge SIDECAR-TOPOLOGY-REVIEW-APP-1 into main

Final files:

- FCF_CURRENT_STATE_SIDECAR_TOPOLOGY_REVIEW_APP_1_FINAL.md
- apps/sidecar_topology_review_app_1/
- docs/sidecar_topology_review_app_1/
- tests/test_sidecar_topology_review_app_1_d1_contract.py
- tests/test_sidecar_topology_review_app_1_d2_inventory.py
- tests/test_sidecar_topology_review_app_1_d3_isolation_zones.py
- tests/test_sidecar_topology_review_app_1_d4_dag_review.py
- tests/test_sidecar_topology_review_app_1_d5_queue_gates.py
- tests/test_sidecar_topology_review_app_1_d6_closeout.py

Governance result:

- Completed sidecar inventory established.
- Four isolation zones established.
- Dependency DAG review established.
- Circular dependency risk rules established.
- Future sidecar queue and governance gates established.

Deferred backlog remains:

- DIFY-LOCAL-CONFIG-HARDENING-APP-1 stays deferred until operator explicitly starts local Dify/Ollama configuration.
- Future sidecars require explicit operator approval before development.

Safety confirmation:

- paper-only
- local-only
- read-only
- governance-only
- operator-review-only
- no P48
- no core mutation
- no broker API
- no exchange API
- no wallet API
- no real order
- no real execution
- no real balance or position read
- no real money impact
- no Dify API write
- no deploy
- no release
- no tag

<!-- FCF_CC_SIDECAR_TOPOLOGY_REVIEW_APP_1_MAINLINE_SYNC_END -->

<!-- FCF_CC_CONTROL_CENTER_MAINTENANCE_APP_1_MAINLINE_SYNC_BEGIN -->

## Mainline Sync: CONTROL-CENTER-MAINTENANCE-APP-1

Status: completed and merged into main.

Mainline state:
- Branch: main
- Latest merge commit: fb75a85 merge CONTROL-CENTER-MAINTENANCE-APP-1 into main
- Push status: success
- Push range: f2a552b..fb75a85 main -> main
- Final git status: clean
- Tag: none
- Release: none
- Deploy: none

Completed sidecar commits:
- bad55e4 add CONTROL-CENTER-MAINTENANCE-D1 contract
- 3c224fd add CONTROL-CENTER-MAINTENANCE-D2 required sections
- 5cff6c4 add CONTROL-CENTER-MAINTENANCE-D3 merge template
- b5b81d9 add CONTROL-CENTER-MAINTENANCE-D4 backlog rules
- ca51918 add CONTROL-CENTER-MAINTENANCE-D5 validation checklist
- cc7cb8b add CONTROL-CENTER-MAINTENANCE-D6 final closeout
- fb75a85 merge CONTROL-CENTER-MAINTENANCE-APP-1 into main

Governance result:
- Control center update triggers defined.
- Required control center sections defined.
- Merge record template defined.
- Deferred backlog maintenance rules defined.
- Validation and clean-status checklist defined.
- Repo control center remains source of truth.

Safety confirmation:
- paper-only
- local-only
- read-only
- sidecar-only
- governance-only
- operator-review-only
- no P48
- no core mutation
- no real trading
- no real execution
- no deploy
- no release
- no tag

<!-- FCF_CC_CONTROL_CENTER_MAINTENANCE_APP_1_MAINLINE_SYNC_END -->

## CORRELATION-ID-TRACEABILITY-APP-1

Status: completed and merged into main.

Main merge commit:
- b2ef1ce merge CORRELATION-ID-TRACEABILITY-APP-1 into main

Sidecar branch:
- sidecar-correlation-id-traceability-app-1

Completed stages:
- D1 sidecar boundary and traceability contract
- D2 read-only source map
- D3 trace record schema
- D4 chain integrity rules
- D5 trace review packet
- D6 final handoff closeout

Purpose:
- Establish full-chain Correlation_ID traceability across Data, Validation, Review, UI, Archive, and Dify handoff artifacts.

Safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no source content mutation
- no score mutation
- no reason code mutation
- no risk flag deletion or downgrade
- no Dify deploy
- no Dify API write
- no tag
- no release
- no deploy

## SIDECAR-TOPOLOGY-REVIEW-APP-1 Completion Update

Status: completed and merged into main.

Purpose:
- Review completed sidecar dependency topology.
- Define DAG-only sidecar dependency rule.
- Group completed sidecars into isolation zones.
- Prevent circular dependency.
- Preserve paper-only, local-only, read-only, sidecar-only boundary.

Completed stages:
- D1 topology boundary contract
- D2 completed sidecar source loader
- D3 DAG dependency validation rules
- D4 isolation zone model
- D5 topology review packet
- D6 final handoff closeout

Final validation:
- python scripts/run_all_checks.py passed
- python -m pytest -q = 1589 passed

Safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no circular dependency
- no real trading
- no broker connection
- no exchange connection
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## CONTROL-CENTER-MAINTENANCE-APP-2 D1 Next Phase Decision Register

Status: active control-center maintenance layer.

Purpose:
- Preserve next-phase decision order.
- Prevent skipped architecture review details.
- Keep Annie route visible in the control center.
- Separate lightweight control-center work from large D1-D6 sidecar construction.

Accepted next-phase order:
1. SIDECAR-TOPOLOGY-REVIEW-APP-1
2. CONTROL-CENTER-MAINTENANCE-APP-2
3. UI-RISK-FLAG-VISIBILITY-APP-1
4. ARCHIVE-CORRELATION-ROLLUP-APP-1

Completed before this layer:
- SIDECAR-TOPOLOGY-REVIEW-APP-1 completed, merged, validated, pushed, and archived.

Current selected phase:
- CONTROL-CENTER-MAINTENANCE-APP-2

Execution rule:
- Small control-center updates may be completed in the current control window.
- Large implementation work must use a dedicated sidecar development branch or window.
- Architecture gap details must not be skipped.
- Operator confirmation remains required before tag, release, or deploy.

Safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no real trading
- no broker connection
- no exchange connection
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## CONTROL-CENTER-MAINTENANCE-APP-2 D2 Architecture Gap Candidate Queue

Status: active candidate queue.

Purpose:
- Preserve remaining architecture gap candidates.
- Keep candidate priority visible.
- Prevent skipped UI risk flag visibility work.
- Prevent skipped archive correlation rollup work.

Candidate queue:

### 1. UI-RISK-FLAG-VISIBILITY-APP-1
Priority: high.
Reason:
- UI must render risk_flags explicitly.
- UI must render reason_codes explicitly.
- UI must not hide risk flags.
- UI must not downgrade risk flags.
- UI must not delete reason codes.
Expected scope:
- read-only UI visibility contract
- risk flag panel visibility checks
- reason code panel visibility checks
- blocked response visibility checks
- operator review visibility handoff
Execution size: medium sidecar.

### 2. ARCHIVE-CORRELATION-ROLLUP-APP-1
Priority: medium-high.
Reason:
- Correlation_ID should be traceable across archive, report, final state, and control-center records.
- Archive/report outputs should support full-chain trace lookup.
Expected scope:
- read-only archive correlation source loader
- correlation rollup schema
- final-state correlation summary
- archive/report trace packet
- no mutation and no execution boundary
Execution size: medium sidecar.

### 3. CONTROL-CENTER-MAINTENANCE-APP-2 closeout
Priority: current.
Reason:
- Current branch is lightweight control-center hardening.
- Complete control-center updates first, then merge to main.
Execution size: small.

Next selection rule:
- Finish CONTROL-CENTER-MAINTENANCE-APP-2 first.
- Then choose UI-RISK-FLAG-VISIBILITY-APP-1 before ARCHIVE-CORRELATION-ROLLUP-APP-1 unless operator changes priority.
- Large sidecar work must use a dedicated branch.

Safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no risk flag deletion or downgrade
- no reason code deletion
- no real trading
- no broker connection
- no exchange connection
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## CONTROL-CENTER-MAINTENANCE-APP-2 D3 Window Routing Rule

Status: active routing rule.

Purpose:
- Define when work stays in the control window.
- Define when work needs a dedicated development window.
- Prevent accidental large implementation inside the control window.

Control window allowed:
- read-only status recovery
- architecture gap review
- candidate priority selection
- control-center documentation updates
- final state archive updates
- small safety or governance text hardening

Development window required:
- any new medium or large D1-D6 sidecar
- any test-backed implementation module
- any schema/model/loader/packet code addition
- any repair that changes executable app code
- any branch that needs repeated pytest iterations

Mandatory before new development window:
- current branch clean
- current branch pushed
- selected sidecar name fixed
- safety boundary copied
- D1-D6 scope listed
- no tag, release, or deploy unless operator explicitly confirms

Current next planned large sidecar:
- UI-RISK-FLAG-VISIBILITY-APP-1

Safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no real trading
- no broker connection
- no exchange connection
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## CONTROL-CENTER-MAINTENANCE-APP-2 D4 Next Sidecar Handoff Template

Status: active next-sidecar handoff template.

Selected next large sidecar:
- UI-RISK-FLAG-VISIBILITY-APP-1

Purpose:
- Verify UI risk flag visibility.
- Verify reason code visibility.
- Prevent hidden, downgraded, deleted, or softened risk flags.
- Preserve operator review visibility.

Required D1-D6 draft:
- D1 read-only UI visibility boundary contract
- D2 UI source artifact loader
- D3 risk flag visibility schema
- D4 reason code visibility schema
- D5 blocked response and operator review visibility packet
- D6 final workflow handoff and closeout

Must verify:
- risk_flags are rendered explicitly
- reason_codes are rendered explicitly
- blocked response state is visible
- operator_review_required is visible
- risk flag downgrade is forbidden
- risk flag deletion is forbidden
- reason code deletion is forbidden
- UI cannot convert warning into approval
- UI cannot bypass operator review

Forbidden:
- no buy button
- no sell button
- no order button
- no broker connection
- no exchange connection
- no API key storage
- no real account access
- no real position access
- no real execution
- no tag
- no release
- no deploy

Start rule:
- Start UI-RISK-FLAG-VISIBILITY-APP-1 only after CONTROL-CENTER-MAINTENANCE-APP-2 is merged, archived, pushed, and clean.

## CONTROL-CENTER-MAINTENANCE-APP-2 D5 Merge And Archive Readiness Checklist

Status: active merge readiness checklist.

Purpose:
- Define required checks before merging this control-center maintenance layer.
- Preserve clean handoff to the next large sidecar.
- Prevent skipped final-state archive.

Merge readiness checklist:
- branch is control-center-maintenance-app-2
- branch is pushed to origin
- python scripts/run_all_checks.py passed
- python -m pytest -q passed
- git status --short is blank after runtime restore
- no tag created
- no release created
- no deploy performed

Required completion sequence:
1. Finish CONTROL-CENTER-MAINTENANCE-APP-2 D6 closeout.
2. Merge control-center-maintenance-app-2 into main.
3. Run validation on main.
4. Restore runtime generated files.
5. Push main.
6. Add final current-state archive file.
7. Push final current-state archive.
8. Return to control window.
9. Start UI-RISK-FLAG-VISIBILITY-APP-1 only after clean final archive.

Do not skip:
- final current state file
- control-center latest state confirmation
- next sidecar handoff summary
- clean git status confirmation

Safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no real trading
- no broker connection
- no exchange connection
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## CONTROL-CENTER-MAINTENANCE-APP-2 D6 Final Closeout

Status: completed on branch control-center-maintenance-app-2.

Completed scope:
- D1 next phase decision register
- D2 architecture gap candidate queue
- D3 window routing rule
- D4 next sidecar handoff template
- D5 merge and archive readiness checklist
- D6 final closeout

Final control-center result:
- Annie route preserved.
- Next phase order preserved.
- UI-RISK-FLAG-VISIBILITY-APP-1 remains the next large sidecar candidate.
- ARCHIVE-CORRELATION-ROLLUP-APP-1 remains the following candidate.
- Small control-center work and large sidecar work are separated.
- Merge and archive sequence is explicitly documented.

Next required action after this D6:
1. Merge control-center-maintenance-app-2 into main.
2. Validate main.
3. Push main.
4. Add final current-state archive.
5. Return to control window.
6. Start UI-RISK-FLAG-VISIBILITY-APP-1 only after clean archive.

Safety boundary preserved:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no P48 core expansion
- no P1-P47 core mutation
- no real trading
- no broker connection
- no exchange connection
- no API key
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## UI-RISK-FLAG-VISIBILITY-APP-1 Completion Update

Status: completed and merged into main.

Purpose:
- Verify UI risk flag visibility.
- Verify reason code visibility.
- Verify blocked response state visibility.
- Verify operator review required visibility.
- Prevent hidden, downgraded, deleted, or softened risk flags.

Completed stages:
- D1 read-only UI visibility boundary contract
- D2 UI visibility source loader
- D2 fix test module name
- D3 risk flag visibility schema
- D4 reason code visibility schema
- D5 blocked response and operator review visibility packet
- D6 final workflow handoff and closeout

Final validation:
- python scripts/run_all_checks.py passed
- python -m pytest -q = 1595 passed

Safety boundary:
- paper-only
- local-only
- read-only
- sidecar-only
- operator review required
- no risk flag downgrade
- no risk flag deletion
- no reason code deletion
- no operator review bypass
- no buy button
- no sell button
- no order button
- no tag
- no release
- no deploy

## ARCHIVE-CORRELATION-ROLLUP-APP-1 Completion

Status: completed and merged into main.

Purpose:
ARCHIVE-CORRELATION-ROLLUP-APP-1 establishes a read-only Correlation_ID rollup layer across archive, report, final current state, control center, handoff, and validation artifacts.

Completed stages:
- D1 sidecar boundary and rollup contract
- D2 read-only source discovery
- D3 rollup record schema
- D4 trace summary and coverage review
- D5 rollup packet
- D6 final workflow handoff and closeout

Final capability:
- classify eligible artifact paths
- reject runtime files as source of truth
- build Correlation_ID rollup records
- validate rollup record safety state
- summarize trace coverage
- detect partial or blocked traces
- build paper-only rollup packets
- preserve operator review requirement
- keep release and deploy disabled

Safety boundary:
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
