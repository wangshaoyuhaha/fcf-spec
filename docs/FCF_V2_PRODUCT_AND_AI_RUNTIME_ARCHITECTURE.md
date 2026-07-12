# FCF V2 Product and AI Runtime Architecture

## 1. Document Status

Status: AUTHORITATIVE PLANNING BASELINE

This document locks the confirmed FCF V2 product, data, AI governance,
orchestration, usability, validation, and long-term trading evolution
directions.

The six decisions listed in Section 32 remain pending explicit Operator
approval. They must not be silently inferred or implemented.

External DeepSeek and Gemini materials are planning inputs only. They do
not override repository truth, Git history, tests, the Control Center, or
the permanent safety boundaries.

## 2. Current Repository Truth

Repository: wangshaoyuhaha/fcf-spec

Local repository:

C:\Users\Admin\Desktop\btc_finance_platform

Current authoritative baseline before this architecture lock:

- branch: main
- HEAD: 6be27c7889ee3b2b019ee5e8e7b646de68b2467b
- origin/main: synchronized
- pytest: 3273 passed
- run_all_checks: PASSED
- git status: CLEAN
- tag: none
- release: none
- deploy: none

AI-COMPREHENSIVE-REPORT-CONSUMER-ACTIVATION-APP-1 is complete,
validated, merged, synchronized, and closed.

GAP-1 through GAP-5 from that phase are CLOSED.

## 3. Product Vision

FCF V2 is a controlled financial research product for human operators.

The Operator must not need to run Python, PowerShell, pytest, or Git
during normal product use.

Python remains the deterministic engine behind a browser-accessible
product surface.

Target user flow:

1. Data Ingestion
2. Process Monitoring
3. Final Insight and Human Review

The normal product interaction must be browser-based.

## 4. Permanent Constitutional Safety Boundaries

The following boundaries remain authoritative unless a separate,
explicitly approved future architecture changes them:

- P1-P47 remain frozen
- no P48
- no frozen core mutation
- paper-only
- local-only where required by privacy policy
- read-only ingestion
- sidecar-only extensions
- deterministic control
- registered artifacts only
- operator review required
- manual archive authorization required
- no automatic approval
- no automatic archive
- no archive writing by AI
- no model-controlled execution
- no prompt-controlled execution
- no automatic trading routing
- no real order placement
- no real balance access
- no real position access
- no wallet private key access
- no exchange trading credential access

## 5. Authority Hierarchy

The authoritative machine and human power order is:

1. Operator Policy
2. FCF Hard Policy
3. Deterministic Engine
4. Validated Data and Evidence
5. Orchestrator
6. AI Models
7. External Narrative

A lower layer cannot override a higher layer.

Examples:

- An AI recommendation cannot bypass a hard risk rule.
- Model consensus cannot override invalid or stale data.
- External narrative cannot override deterministic facts.
- The Operator may stop or reject a workflow.
- AI may never weaken hard limits.
- AI may never remove a preserved risk flag.
- AI may never silently rewrite another model output.

## 6. Target Product Experience

The target product contains three primary user surfaces.

### 6.1 Data Ingestion

The Operator can:

- upload PDF
- upload Excel
- upload CSV
- upload JSON
- paste text
- select local files
- select approved read-only sources
- later connect approved read-only data gateways

The ingestion process must:

- validate file type
- scan and quarantine unsafe content
- remove credentials and personal data where required
- normalize data
- assign evidence identifiers
- generate checksums
- assign source trust level
- assign freshness status
- pass data-quality gates

### 6.2 Process Monitoring

The Operator can see:

- workflow step
- workflow status
- start time
- elapsed time
- active model role
- model identifier
- prompt version
- input artifact version
- retry count
- failure reason
- cost consumption
- data freshness
- model disagreement
- risk flags
- waiting-for-review status

### 6.3 Final Insight

The final surface must display:

- deterministic calculations
- market state
- candidate ranking
- causal reasoning
- supporting evidence
- contradicting evidence
- assumptions
- uncertainty
- model disagreement
- risk flags
- scenario results
- comprehensive report
- evidence references
- human review controls

No real buy, sell, position, or order button is part of the current FCF
V2 scope.

## 7. Service Architecture

Target logical architecture:

Browser Product Surface
    ->
FCF Web Console or Approved Product UI
    ->
Workflow and Orchestration Layer
    ->
FCF API Gateway
    ->
Sidecar Application Services
    ->
Frozen Deterministic Core

Supporting services:

- Read-Only Data Gateway
- Research Gateway
- Model Gateway
- Local Model Runtime
- Approved Cloud Model Providers
- Evidence Store
- Artifact Registry
- Audit Store
- Observability Stack
- Configuration and Policy Registry

The HTTP, workflow, UI, model, and external-data layers must not be
written into the frozen core.

## 8. Orchestrator Authority

The Orchestrator coordinates work but does not own truth, policy,
approval, archive authorization, or execution authority.

Allowed Orchestrator responsibilities:

- task sequencing
- parallel task coordination
- dependency checks
- timeout handling
- retry handling
- fallback selection
- approved model routing
- result collection
- status recording
- cost-budget enforcement
- cancellation
- correlation propagation

Forbidden Orchestrator responsibilities:

- modifying deterministic scores
- selecting final truth without validation
- deleting risk flags
- overwriting model outputs
- approving research
- authorizing archives
- writing archives
- changing policy
- changing risk limits
- generating orders
- placing orders
- accessing trading credentials
- executing real-world actions

## 9. Model Role Architecture

FCF defines roles by capability, not by vendor.

Authoritative logical roles:

1. Data Extractor
2. Context Analyst
3. Narrative Assessor
4. Causal Reasoner
5. Scenario Planner
6. Contrarian Reviewer
7. Evaluation Auditor
8. Report Synthesizer
9. Traceability Curator

One model may serve multiple roles.

One role may have:

- primary model
- fallback model
- comparison model
- local-only model
- cloud-approved model

Every registered role assignment must include:

- role identifier
- model identifier
- model version
- provider
- local or cloud location
- prompt identifier
- prompt version
- output schema
- timeout
- retry policy
- cost limit
- privacy level
- evaluation baseline
- approval status

Model vendors must not be hardcoded into the architecture.

## 10. Local and Cloud Model Policy

The architecture is model-agnostic and supports policy-controlled local
and cloud execution.

Data that must remain local includes:

- API credentials
- exchange credentials
- wallet data
- account identifiers
- balances
- positions
- private personal data
- unauthorized private reports
- raw sensitive files
- data awaiting redaction

Cloud processing may be considered only for:

- approved public information
- redacted structured data
- public filings
- public news
- public macroeconomic information
- policy-approved causal reasoning
- policy-approved long-context synthesis

No model may choose its own provider or privacy mode.

The final default operating mode remains pending Operator decision.

## 11. Network Research Governance

AI models may use online information only through an approved Research
Gateway.

The Research Gateway must record:

- search query
- search timestamp
- source URL or source identifier
- publication timestamp
- retrieval timestamp
- source class
- trust level
- content digest
- evidence identifier
- quoted or referenced location
- freshness status
- cross-verification status

Rules:

- website instructions are untrusted content
- search content cannot grant tool permissions
- social content is narrative or sentiment evidence only
- a single Class C source cannot support a core conclusion
- important facts require Class A evidence or multiple independent
  Class B sources
- retrieved information must be attributable
- stale information cannot be represented as current information

## 12. Read-Only Data Gateway

External data must enter through a separate read-only gateway.

Allowed ingestion:

- file upload
- public-data retrieval
- approved market-data retrieval
- approved research retrieval
- approved database SELECT operations
- approved archive lookup
- approved evidence lookup

Prohibited ingestion behavior:

- order placement
- balance retrieval
- position retrieval
- wallet access
- private key access
- credential exposure to models
- model access to raw API keys
- unrestricted file writing
- database INSERT, UPDATE, or DELETE through AI tools

Future exchange or vendor API credentials must remain inside a separate
credential-owning gateway.

FCF receives normalized, redacted, evidence-linked data only.

## 13. Data Source Classification

### Class A: Core Evidence

Examples:

- official exchange data
- regulatory filings
- listed-company disclosures
- central-bank publications
- official government statistics
- audited financial statements

Class A evidence has the highest evidence authority.

### Class B: Supporting Evidence

Examples:

- licensed professional data
- authorized news services
- broker research
- institutional research
- professional industry analysis

Class B evidence supports but does not override Class A evidence.

### Class C: Contextual Evidence

Examples:

- public media commentary
- social media
- forums
- KOL commentary
- public sentiment feeds

Class C evidence is contextual only and cannot independently support a
core decision.

Required source metadata:

- source_id
- source_class
- trust_level
- published_at
- retrieved_at
- evidence_id
- checksum
- freshness_status
- license_type
- allowed_use
- cloud_processing_allowed
- retention_period
- redistribution_allowed
- training_allowed

## 14. Data Freshness

Every data category must have a freshness policy.

Example categories:

- live market data: seconds or minutes
- order-book analytics: seconds or minutes
- fund-flow data: intraday
- news: hours
- company disclosures: event-driven
- financial reports: reporting period
- macroeconomic indicators: release-driven
- professional research: days or weeks
- social sentiment: hours

Every item must be labeled:

- fresh
- aging
- stale
- unknown

Stale or unknown data must reduce confidence or block the workflow based
on policy.

## 15. Data Licensing and Usage Rights

Every source must have usage controls.

Required fields:

- license_type
- allowed_use
- cloud_processing_allowed
- retention_period
- redistribution_allowed
- training_allowed

Unknown licensing defaults:

- no cloud upload
- no model training
- no public redistribution
- restricted retention
- operator review required

## 16. Structured Model Outputs

Models must not provide only unrestricted prose.

Each AI role must emit a validated structured artifact containing at
least:

- role
- model_id
- model_version
- prompt_id
- prompt_version
- correlation_id
- source_artifact_ids
- claims
- supporting_evidence_ids
- contradicting_evidence_ids
- assumptions
- uncertainties
- self_reported_confidence
- risk_flags
- status

Example status:

REVIEW_REQUIRED

If output validation fails:

1. retry within the approved limit
2. use an approved fallback model
3. mark quality degradation
4. stop the role if validation still fails
5. do not allow the synthesizer to invent missing output

## 17. Confidence Governance

A model's self-reported confidence is not the FCF confidence score.

System confidence must be calculated deterministically using:

- data completeness
- source authority
- freshness
- evidence coverage
- model evaluation history
- model disagreement
- contradiction results
- risk-review results
- market regime
- unknown or missing information

Model confidence is one input only.

## 18. Disagreement Governance

Model disagreement is a first-class artifact.

Allowed classifications:

- CONSENSUS
- MINOR_DISAGREEMENT
- MATERIAL_DISAGREEMENT
- FUNDAMENTAL_CONTRADICTION
- INSUFFICIENT_EVIDENCE

Material disagreement must:

- remain visible
- reduce system confidence
- trigger review
- preserve all original outputs
- allow additional evidence collection
- prevent forced false consensus

The Report Synthesizer may explain disagreement but may not erase it.

## 19. Stock and Asset Selection Architecture

The candidate-selection pipeline may include:

1. exclusion and data-quality filtering
2. fundamental factors
3. price and technical factors
4. fund-flow factors
5. events and narrative
6. market-regime adjustment
7. deterministic composite ranking

Python and deterministic services own:

- exclusions
- factor calculations
- scoring
- ranking
- risk deductions
- versioned weighting
- repeatable calculations

AI owns:

- event interpretation
- narrative extraction
- causal explanation
- scenario analysis
- contradiction discovery
- uncertainty explanation
- report synthesis

AI cannot directly change scores or live weights.

A proposed weight change requires:

1. documented recommendation
2. evidence
3. human approval
4. versioned configuration
5. backtesting
6. evaluation
7. controlled activation

The exact primary market remains pending Operator decision.

## 20. Portfolio Construction

Portfolio construction is a recommended architecture capability pending
final Operator decision.

Candidate deterministic controls:

- industry concentration
- theme concentration
- factor concentration
- asset correlation
- beta
- volatility
- liquidity
- maximum drawdown
- single-asset limit
- portfolio risk budget
- turnover
- transaction-cost estimates

AI may explain portfolio risks.

AI may not calculate or silently modify final portfolio weights.

## 21. Backtesting and Forward Validation

Every new strategy, factor, weighting policy, or model-supported
adjustment must pass:

- historical backtesting
- time-based train and validation separation
- walk-forward validation
- regime testing
- fee modeling
- slippage modeling
- survivorship-bias review
- look-ahead-bias review
- overfitting review
- paper validation
- shadow validation where approved
- operator approval

AI-generated strategy ideas cannot directly enter real execution.

## 22. Continuous Model Evaluation

Every approved model and role assignment must be continuously evaluated.

Metrics may include:

- extraction accuracy
- structured-output compliance
- citation correctness
- unsupported-claim rate
- hallucination rate
- risk-omission rate
- causal consistency
- contradiction-detection value
- latency
- cost
- timeout rate
- retry rate
- fallback rate
- failure rate

A model version change requires re-evaluation.

A new model cannot replace an approved model solely because it is newer.

## 23. Failure and Degradation Policy

### Cloud Model Failure

- use approved fallback cloud model
- then use approved local model where suitable
- mark degraded quality
- never fabricate a complete result

### Local Model Failure

- check local runtime health
- use approved local fallback
- require redaction before cloud fallback
- stop if privacy rules prevent cloud use

### Data Source Failure

- use cache only when policy permits
- display cache timestamp
- mark stale data
- never represent cached data as live

### Critical Multi-Component Failure

- set status to BLOCKED
- do not create a formal conclusion
- do not approve
- do not archive
- do not route toward execution

## 24. Observability

The runtime must support:

- structured logs
- metrics
- traces
- correlation_id
- model_id
- prompt_id
- artifact identifiers
- health checks
- timeout visibility
- retry visibility
- fallback visibility
- policy-decision visibility
- data freshness visibility
- cost visibility
- alerts

The Operator must be able to determine whether a failure belongs to:

- data
- Python service
- workflow engine
- model
- network
- policy
- storage
- user action

## 25. Cost Governance

The runtime must support:

- per-task budget
- daily budget
- monthly budget
- per-model call limits
- maximum token limits
- maximum retry count
- budget-stop behavior
- local-first processing for low-value tasks
- cost estimate before execution
- actual cost after execution
- cost by model
- cache savings

Exceeding an approved budget must stop or downgrade the workflow based on
policy.

## 26. Caching

Repeated identical work should be cached where safe.

Candidate cache identity fields:

- input_digest
- model_id
- model_version
- prompt_version
- tool_version
- policy_version
- output_schema_version

Financial conclusions require expiration policies.

A cached result must never be represented as newly generated or current
when it is not current.

## 27. Human Review Workflow

The Operator interface should support:

- Approve for Research Archive
- Reject
- Request Re-analysis
- Request More Evidence
- Mark Data as Untrusted
- Compare Models
- Override with Reason
- Freeze Report
- Export
- Stop Workflow

Human overrides require an explicit reason and audit record.

Human approval cannot remove immutable audit history.

## 28. Dify, Open WebUI, and Product UI

Confirmed roles:

### Dify

- workflow prototyping
- model-node orchestration
- HTTP integration
- retry and fallback coordination
- internal workflow operations

### Open WebUI

- model testing
- prompt experiments
- local-model sandbox
- development-only comparisons

Open WebUI must not control the formal FCF production chain.

### Product UI

A browser-accessible product surface is required.

Whether the final permanent surface is a custom FCF Web Console or Dify
remains pending Operator decision.

The architecture must avoid permanent dependency on a single low-code
platform.

## 29. Deployment and One-Click Operation

Target normal operation:

1. Operator starts FCF
2. required services are checked
3. services start
4. health checks run
5. browser opens
6. readiness status is displayed

Required operational capabilities:

- one-click start
- one-click stop
- health checks
- configuration backup
- database backup
- upgrade snapshot
- rollback
- missing-model notification
- service-failure notification
- migration checks
- state export
- recovery documentation

The Operator must not need to manually run Python for normal use.

## 30. Trading Evolution

Candidate long-term levels:

### Level 1: Paper Trading

- current allowed research boundary
- simulated entries and exits
- simulated positions
- simulated performance
- no real money

### Level 2: Shadow Trading

- live market observation
- simulated orders
- no real order transmission
- execution-quality comparison

### Level 3: Human-Confirmed Trading

- system creates an order draft
- human confirmation is mandatory
- an independent gateway transmits approved orders

### Level 4: Restricted Automatic Trading

- hardcoded limits
- white-listed assets
- independent risk controls
- independent Kill Switch
- independent execution logs
- no model control over hard limits

The current FCF repository contains no real execution.

Whether any future execution gateway must be a separate repository and
separate security boundary remains pending final Operator decision.

## 31. Locked Delivery Sequence

The following implementation sequence is locked as the current planning
order:

1. Post-phase state reconciliation and architecture lock
2. AI-ORCHESTRATION-RUNTIME-READINESS-APP-1
3. Read-Only Data Gateway design and implementation planning
4. FCF API Gateway design and implementation planning
5. Multi-Model Workflow design
6. Browser Product Console design
7. Paper and Shadow validation planning
8. Long-term evaluation of a separately governed execution capability

No step after Step 1 begins until the Operator explicitly resumes
development.

AI-ORCHESTRATION-RUNTIME-READINESS-APP-1 must remain readiness-only:

- no actual model invocation
- no prompt execution
- no automatic routing
- no automatic archive
- no archive writing
- no real execution
- no trading API
- no credentials

## 32. Pending Operator Decisions

The following six decisions are explicitly unresolved.

They must be discussed with the Operator in the next planning discussion.

### Decision 1

Should the permanent formal user interface be a custom FCF Web Console,
with Dify operating only as the background workflow engine?

Status: PENDING OPERATOR DECISION

### Decision 2

Should the default model mode be Hybrid, with sensitive data processed
locally and approved public or redacted data eligible for cloud models?

Status: PENDING OPERATOR DECISION

### Decision 3

Should stocks be the first primary market, with BTC and futures retained
as compatible markets?

Status: PENDING OPERATOR DECISION

### Decision 4

Should Portfolio Construction become a formal required stage after
candidate selection and ranking?

Status: PENDING OPERATOR DECISION

### Decision 5

Should every future trading-execution capability be placed in an
independent project, gateway, permission domain, and deployment boundary?

Status: PENDING OPERATOR DECISION

### Decision 6

Should the FCF V2 delivery endpoint be:

- upload data
- retrieve approved online data
- invoke approved local and cloud models
- display a traceable comprehensive report
- support human review
- perform no real order placement

Status: PENDING OPERATOR DECISION

## 33. Explicit Non-Goals for the Current Stage

The current stage does not:

- connect a real model runtime
- execute prompts
- create automatic routing
- connect exchange trading APIs
- access balances
- access positions
- access wallet keys
- place orders
- create Shadow Trading
- create automatic trading
- select final model vendors
- decide the six pending Operator decisions
- modify frozen core
- change Python production behavior

## 34. Truth and Supersession Rules

Repository truth precedence:

1. Git and current checked-out files
2. current tests and validation logs
3. FCF_PROJECT_CONTROL_CENTER.md authoritative current-state blocks
4. current Final Current State documents
5. current handoff block
6. older historical planning sections
7. external reports and slides

Any older OPEN, NOT APPROVED, APPROVED ACTIVE, READY FOR MAIN MERGE, or
other contradictory marker for a phase that has since completed is
historical only.

The newest explicit authoritative completion or reconciliation block
supersedes older contradictory markers.

Historical content may remain for audit purposes but must not be treated
as current project state.
