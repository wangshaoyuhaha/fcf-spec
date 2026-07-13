<!-- FCF-PAPER-AND-SHADOW-VALIDATION-PLANNING-APPROVAL-TRUTH-BEGIN -->
# FCF CURRENT AUTHORITATIVE STATE

This header overrides every older next-phase, candidate, branch-creation,
D1-start, and automatic-resume statement below.

Project:

FCF / Financial Cognitive Framework

Latest completed product phase:

BROWSER-PRODUCT-CONSOLE-DESIGN-APP-1

Completed baseline:

- branch: main
- HEAD before this approval synchronization:
  21e432eb34c800062d6e383cb1d5ba47a5f4e5d9
- product phase status:
  COMPLETE / MERGED / VALIDATED / PUSHED / CLEAN
- full pytest: 3671 passed
- run_all_checks: PASSED
- git status: CLEAN
- main and origin/main: synchronized
- tag: none
- release: none
- deploy: none

Approved next phase:

PAPER-AND-SHADOW-VALIDATION-PLANNING-APP-1

Approval status:

APPROVED / NOT STARTED / PLANNING-ONLY

Planned Sidecar branch:

sidecar-paper-and-shadow-validation-planning-app-1

Purpose:

Define the governed paper and shadow validation architecture for FCF without
creating trading execution, live account access, automatic model authority, or
automatic promotion.

Planned D1 scope:

- paper validation boundary
- shadow observation boundary
- historical replay versus forward observation separation
- deterministic benchmark authority
- baseline and candidate comparison boundary
- registered artifact input and output requirements
- correlation_id traceability
- Operator review requirements
- BLOCKED, DEGRADED, and INVALID behavior
- permanent execution prohibitions

Permanent restrictions:

- P1-P47 remain frozen
- no P48
- no frozen Core mutation
- paper-only
- read-only
- sidecar-only
- deterministic authority preserved
- Operator review required
- no real broker or exchange connection
- no trading credentials
- no balance or position access
- no wallet access
- no order placement
- no real execution
- no automatic model selection
- no automatic provider routing
- no automatic Champion promotion
- no automatic learning activation
- no automatic approval
- no automatic archive
- no tag
- no release
- no deployment

Next action:

- complete this approval synchronization
- do not start D1 before approval synchronization is committed and pushed
- after synchronization, create the approved Sidecar branch
- begin D1 only
<!-- FCF-PAPER-AND-SHADOW-VALIDATION-PLANNING-APPROVAL-TRUTH-END -->

<!-- FCF-BROWSER-PRODUCT-CONSOLE-DESIGN-COMPLETION-TRUTH-BEGIN -->
# FCF CURRENT AUTHORITATIVE STATE

This header overrides every older state, validation, branch,
candidate, next-step, and automatic-resume statement below.

Project:

FCF / Financial Cognitive Framework

Current product state:

- latest completed product phase:
  BROWSER-PRODUCT-CONSOLE-DESIGN-APP-1
- product phase status:
  COMPLETE / MERGED / VALIDATED / PUSHED / CLEAN
- branch: main
- product phase merge commit:
  cd9e7f71b621957b7acd2caa8ec214402ea46fbf
- initial Final Current State commit:
  59587337313f4afce523fa61f0889183b86ea2b7
- D6 final design commit:
  8f0693820f90efffb0e958dd6cc393ba7008436a
- Final Current State file:
  docs/browser_product_console_design/FINAL_CURRENT_STATE.md
- targeted D1-D6 pytest: 18 passed
- full pytest: 3671 passed
- run_all_checks: PASSED
- generated runtime artifacts: RESTORED
- main and origin/main:
  synchronized before Boundary D
- completion synchronization commit:
  the commit containing this header
- git status:
  CLEAN before Boundary D
- tag: none
- release: none
- deploy: none

Delivered design scope:

- governed Browser Product Console boundary
- Viewer role
- Research Analyst role
- Operator Reviewer role
- Governance Administrator role
- Overview workspace
- Data Workspace
- Research Runs workspace
- AI Comparison workspace
- Evidence and Risk workspace
- Operator Review workspace
- Reports and Archive workspace
- Governance workspace
- Audit History workspace
- idempotent governed commands
- first-class risk and contradiction presentation
- registered evidence and provenance presentation
- Operator review and configuration governance
- future implementation sequence

Runtime authority:

- design mode: DESIGN_ONLY
- runtime implementation: NOT CREATED
- web server: NOT CREATED
- HTTP listener: NOT CREATED
- network port: NOT OPENED
- API runtime: NOT CREATED
- model invocation: NOT ALLOWED
- Prompt execution: NOT ALLOWED
- automatic model selection: NOT ALLOWED
- automatic model switching: NOT ALLOWED
- automatic provider routing: NOT ALLOWED
- automatic approval: NOT ALLOWED
- automatic archive: NOT ALLOWED
- real execution: NOT ALLOWED
- Operator review: REQUIRED

Permanent project boundaries:

- P1-P47 frozen
- no P48
- no frozen Core mutation
- paper-only
- read-only
- sidecar-only
- deterministic authority preserved
- Operator review required
- no broker or exchange connection
- no credentials
- no balance or position access
- no wallet access
- no order placement
- no automatic approval
- no automatic archive
- no tag
- no release
- no deployment

Next action:

- BROWSER-PRODUCT-CONSOLE-DESIGN-APP-1 is closed
- Browser Product Console runtime implementation is not approved
- return to architecture and control review
- no next development phase is approved
- do not create a new development branch
- wait for explicit Operator approval
<!-- FCF-BROWSER-PRODUCT-CONSOLE-DESIGN-COMPLETION-TRUTH-END -->

<!-- FCF-EXECUTION-SAFETY-PROTOCOL-COMPLETION-TRUTH-BEGIN -->
# FCF CURRENT AUTHORITATIVE STATE

This header overrides every older state, validation, branch,
candidate, next-step, and automatic-resume statement below.

Project:

FCF / Financial Cognitive Framework

Current product state:

- latest completed product phase:
  AI-MULTI-MODEL-WORKFLOW-PLANNING-APP-1
- product phase status:
  COMPLETE / MERGED / VALIDATED / PUSHED / CLEAN
- product phase merge commit:
  7a0c01d31737ebf23f24a1c5e724b9de304b1e66
- product phase synchronization commit:
  984297743b87d6d9bb2b326ec0f4d4852feb0438

Execution safety maintenance:

- status:
  COMPLETE / MERGED / VALIDATED / PUSHED / CLEAN
- maintenance branch commit:
  5b28ae61d307898024953384b8d621a48d9ef66f
- main merge commit:
  490d66af87a4feb1e06391adc1702365171c6d1f
- protocol:
  docs/FCF_EXECUTION_SAFETY_PROTOCOL.md
- safe process runner:
  scripts/fcf_safe_runner.ps1
- contract tests:
  tests/test_fcf_safe_runner_contract.py
- line-ending rules:
  .gitattributes
- safe runner self-test: PASSED
- targeted contract pytest: 4 passed
- full pytest at Boundary C: 3653 passed
- run_all_checks at Boundary C: PASSED
- generated runtime artifacts: RESTORED
- branch: main
- git status: CLEAN
- main and origin/main:
  synchronized by the commit containing this header
- tag: none
- release: none
- deploy: none

Mandatory execution workflow:

1. Boundary A:
   local preflight, file writes, targeted validation,
   no network, no commit, no push
2. Boundary B:
   explicit staging, cached diff validation, local commit,
   bounded push retries
3. Boundary C:
   main merge, targeted validation, full pytest,
   run_all_checks, generated-file restoration, push main
4. Boundary D:
   authoritative document synchronization,
   validation, commit, push

Permanent execution safeguards:

- command success is determined by process exit code
- stdout and stderr are captured separately
- stderr warning with exit code zero is not a failure
- no network preflight as a local write gate
- no temporary core.autocrlf override
- no repository-wide destructive cleanup
- stage only explicit expected paths
- push failure resumes with push only
- completed boundaries must not be repeated
- long workflows must use checkpoints
- all future generated PowerShell must use the safe runner

Permanent project boundaries:

- P1-P47 frozen
- no P48
- no frozen Core mutation
- paper-only
- read-only
- sidecar-only
- deterministic authority preserved
- Operator review required
- no broker or exchange connection
- no credential access
- no balance or position access
- no wallet access
- no order placement
- no automatic approval
- no automatic archive
- no tag
- no release
- no deployment

Next action:

- execution safety repair is closed
- return to architecture and control review
- next candidate:
  Browser Product Console design
- next development phase is not yet approved
- do not create a new development branch
- do not write new phase code
- wait for explicit Operator approval
<!-- FCF-EXECUTION-SAFETY-PROTOCOL-COMPLETION-TRUTH-END -->

---# FCF V2 Product and AI Runtime Architecture

## 1. Document Status

Status: AUTHORITATIVE CONSTITUTIONAL PLANNING BASELINE

This document locks the approved FCF V2 product, AI runtime, data,
multi-market, portfolio, usability, governance, validation, and
long-term execution-boundary architecture.

The six former pending Operator decisions are approved in Section 32.

External model reports, slides, community skills, and architecture
opinions are advisory inputs only.

They cannot override:

1. explicit Operator approval
2. repository truth
3. deterministic policy
4. validated evidence
5. tests and immutable audit history

## 2. Current Repository Truth

Repository: wangshaoyuhaha/fcf-spec

Local repository:

C:\Users\Admin\Desktop\btc_finance_platform

Authoritative baseline before this constitutional-decision commit:

- branch: main
- HEAD: eeeca0f482d24eb3c51db32a92a558a3ae573034
- origin/main: synchronized
- pytest: 3273 passed
- run_all_checks: PASSED
- git status: CLEAN
- tag: none
- release: none
- deploy: none

AI-COMPREHENSIVE-REPORT-CONSUMER-ACTIVATION-APP-1 is complete,
validated, merged, synchronized, and closed.

GAP-1 through GAP-5 are CLOSED.

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

The permanent formal product interface is a custom browser-based FCF Web
Console.

The Operator must not need to operate Python, PowerShell, pytest, Git, or
Dify internals during normal use.

### 6.1 File and Data Upload

The Web Console must support:

- PDF upload
- Excel upload
- CSV upload
- JSON upload
- text input
- multi-file upload
- approved URL input
- approved local-file selection
- approved read-only dataset connections
- approved read-only market and research gateways

Uploaded data must pass:

- format validation
- unsafe-content quarantine
- credential detection
- privacy redaction
- normalization
- checksum generation
- evidence registration
- source classification
- trust classification
- freshness classification
- licensing checks
- data-quality gates

### 6.2 Controlled Research Conversation

The Web Console must contain a controlled research conversation surface.

The Operator may:

- ask questions about uploaded evidence
- request explanations
- compare model conclusions
- request additional evidence
- request re-analysis
- select approved runtime mode
- inspect disagreement and risks
- mark sources as untrusted
- stop workflows

Conversation cannot:

- bypass hard policy
- modify deterministic scores
- modify live weights
- remove risk flags
- silently modify reports
- expose credentials
- authorize archives
- send restricted data to cloud models
- create or transmit real orders

State-changing, high-cost, archive-sensitive, or policy-sensitive
requests require explicit confirmation and audit recording.

### 6.3 Process Monitoring

The Web Console must display:

- workflow step and status
- start time and elapsed time
- active role and model
- prompt version
- input artifact version
- retries and fallbacks
- failure reasons
- cost
- data freshness
- model disagreement
- risk flags
- policy decisions
- human-review status

### 6.4 Final Insight and Human Review

The Web Console must display:

- deterministic calculations
- candidate ranking
- market state
- causal reasoning
- supporting and contradicting evidence
- assumptions
- uncertainty
- disagreement
- risk flags
- scenario results
- portfolio construction
- paper position proposals
- comprehensive report
- evidence references

The Operator controls must include:

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

FCF V2 contains no real buy, sell, cancel, withdrawal, position-
management, or order-transmission control.

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

The approved default mode is Hybrid.

Supported modes:

- Local Only
- Hybrid
- Cloud Enhanced

Deterministic privacy, licensing, source, and data-classification policy
decides whether data may leave the local environment.

AI cannot decide its own permissions, provider, privacy mode, or cloud
eligibility.

Data that must remain local includes:

- credentials
- trading and withdrawal credentials
- wallet data
- account identifiers
- balances
- positions
- private personal data
- restricted private reports
- raw sensitive files
- data awaiting redaction
- licensed content that forbids cloud use

Cloud processing may be considered only for policy-approved:

- public information
- redacted structured data
- public filings
- public news
- public macroeconomic information
- causal reasoning
- long-context synthesis

Cloud Enhanced cannot override hard restrictions.

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

The approved primary market family is Equities.

Mandatory equity-market adapters:

- China A-shares
- United States equities
- Hong Kong equities

All three are required target-architecture components.

Implementation order may differ, but none may be removed.

### 19.1 Shared Candidate Pipeline

1. exclusion and data-quality filtering
2. fundamental factors
3. price and technical factors
4. fund-flow factors
5. events and narrative
6. market-regime adjustment
7. deterministic composite ranking

Deterministic services own:

- exclusions
- factors
- scoring
- ranking
- risk deductions
- versioned weighting

AI owns:

- event interpretation
- narrative extraction
- causal explanation
- scenario analysis
- contradiction discovery
- uncertainty explanation
- report synthesis

AI cannot directly change scores or active weights.

A weight change requires evidence, explicit approval, versioned
configuration, backtesting, evaluation, and controlled activation.

### 19.2 China A-Share Adapter

Required versioned rules include:

- trading calendar and sessions
- T+1 constraints where applicable
- price limits
- ST and special-treatment status
- suspension
- listing-board differences
- corporate actions
- approved capital-flow data
- liquidity
- fees and settlement
- market-specific risks

### 19.3 United States Equity Adapter

Required versioned rules include:

- trading calendar
- regular, pre-market, and after-hours sessions
- SEC and company filings
- corporate actions
- splits and dividends
- approved options and institutional data
- rate and currency context
- liquidity
- fees and settlement
- market-specific risks

### 19.4 Hong Kong Equity Adapter

Required versioned rules include:

- HKEX structures
- trading calendar
- sessions and auctions
- board lots
- odd lots
- HKD and approved counter structures
- corporate actions
- Stock Connect
- approved capital-flow data
- short-sale eligibility where applicable
- fees
- taxes
- settlement
- liquidity
- market-specific risks

Numeric market rules must not be permanently hardcoded in the
constitution.

They must be configurable, versioned, traceable, and validated against
approved sources.

### 19.5 Compatible Asset Families

Mandatory compatible architecture families:

- gold and commodities
- BTC and digital assets
- futures

Gold support must distinguish:

- spot gold
- gold futures
- gold ETFs
- gold-mining equities

BTC and digital assets require handling for:

- continuous trading
- funding rates
- open interest
- liquidation data
- approved on-chain data
- exchange flows
- venue fragmentation
- custody and counterparty risk

Futures require handling for:

- contract expiry
- roll rules
- dominant-contract identification
- margin
- basis
- term structure
- settlement
- exchange-specific rules

Each family requires a separate deterministic adapter and validation
profile.

## 20. Portfolio Construction

Portfolio Construction is mandatory after deterministic candidate
ranking.

It is an independent stage, not a seventh selection factor.

Approved flow:

candidate screening
    ->
deterministic ranking
    ->
portfolio construction
    ->
stress testing
    ->
paper position proposal
    ->
operator review

Required deterministic, configurable, versioned controls include:

- single-asset concentration
- industry concentration
- theme concentration
- factor concentration
- correlation
- beta
- volatility
- liquidity
- maximum drawdown
- turnover
- transaction-cost assumptions
- portfolio risk budget
- paper position sizing

The constitution does not permanently hardcode percentages.

Thresholds require configuration, market rules, backtesting, evaluation,
Operator approval, and versioned activation.

AI may explain portfolio risks.

AI may not calculate, silently modify, or approve final weights.

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

### Dify

Dify is the preferred initial background workflow implementation.

Approved uses:

- workflow prototyping
- model orchestration
- HTTP integration
- retry and fallback coordination
- structured-output handling
- internal workflow operation

Dify is replaceable.

FCF must not permanently depend on Dify or another single workflow
vendor.

### Open WebUI

Open WebUI is limited to:

- model testing
- prompt experiments
- local-model sandbox
- development comparisons

It must not control the formal FCF chain.

### Custom FCF Web Console

The permanent formal interface is a custom FCF Web Console.

It must support:

- upload
- controlled conversation
- workflow control
- process monitoring
- model comparison
- evidence inspection
- risk visibility
- portfolio display
- reports
- human review
- system configuration
- data-source configuration
- health and cost visibility

The Console communicates through stable FCF APIs.

Replacing Dify must not require rebuilding the product interface.

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

## 30. Trading Evolution and Independent Execution Boundary

### Level 1: Paper Trading

- FCF V2 boundary
- simulated entries and exits
- paper positions
- paper performance
- no real money

### Level 2: Shadow Trading

- future planning candidate
- live observation
- simulated orders
- no order transmission
- execution-quality comparison

### Level 3: Human-Confirmed Trading

- future independent-project candidate
- human-approved order intent
- independent execution-gateway risk validation
- no order transmission by fcf-spec

### Level 4: Restricted Automatic Trading

- future independent-project candidate
- hard limits
- white-listed assets
- independent risk controls
- independent Kill Switch
- independent audit
- no model control of limits

Any future execution capability must use a separate:

- repository
- permission domain
- credential domain
- deployment boundary
- audit boundary
- risk-control boundary

The current fcf-spec repository permanently excludes:

- order placement
- order cancellation
- broker execution
- exchange execution
- live position management
- trading credentials
- withdrawal credentials

A future execution gateway may:

- reject
- reduce quantity
- reduce risk
- delay
- cancel
- block
- activate a Kill Switch

It may never:

- increase risk
- increase quantity
- relax limits
- change the approved asset
- bypass approval
- weaken a stop
- weaken a Kill Switch
- silently change an approved intent

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

## 32. Approved Constitutional Decisions

Status:

APPROVED / AUTHORITATIVE / SUPERSEDES ALL SIX PENDING DECISIONS

### Decision 1: Formal Product Interface

A custom FCF Web Console is the permanent formal interface.

It must provide file upload, controlled research conversation, process
monitoring, model comparison, evidence inspection, risk visibility,
reports, and human review.

Dify is a replaceable background workflow implementation.

### Decision 2: Default Model Mode

Hybrid is the default mode.

Deterministic policy controls cloud eligibility.

AI cannot determine its own permissions.

Supported modes:

- Local Only
- Hybrid
- Cloud Enhanced

### Decision 3: Markets

Equities are the primary market family.

Mandatory equity adapters:

- China A-shares
- United States equities
- Hong Kong equities

Mandatory compatible families:

- gold and commodities
- BTC and digital assets
- futures

Each market requires versioned market-specific rules.

### Decision 4: Portfolio Construction

Portfolio Construction is mandatory after ranking.

It is an independent deterministic stage.

Required controls are mandatory; numeric thresholds remain configurable,
validated, approved, and versioned.

### Decision 5: Independent Execution

Any future execution system must be a separate project and security
boundary.

It may reject or reduce approved risk.

It may never increase risk or bypass approval.

### Decision 6: V2 Delivery Endpoint

FCF V2 ends at a complete, operator-reviewed research and paper-
portfolio workflow.

Required capabilities include:

- browser upload
- approved online research
- approved read-only data
- local models
- approved cloud models
- controlled conversation
- multi-model collaboration
- disagreement display
- deterministic confidence
- traceable reports
- portfolio construction
- paper proposals
- human review
- correlation_id traceability
- one-click start
- health checks

FCF V2 contains no real order placement.

Read-only credentials may exist only inside the isolated read-only data
gateway.

Trading, withdrawal, wallet, and real-account-changing credentials remain
prohibited.

### Constitutional Change Procedure

These decisions are constitutional-level but not technically
irreversible.

Any change requires:

1. explicit Operator approval
2. Architecture Decision Record
3. impact analysis
4. safety and privacy review
5. migration and rollback plan
6. validation
7. Control Center update
8. handoff update
9. versioned activation

No AI model, workflow engine, code generator, external report, or
community skill may silently change them.

## 33. Explicit Non-Goals for the Current Stage

The current stage does not:

- invoke real models
- execute prompts
- create automatic routing
- implement adapters
- implement Portfolio Construction
- implement the Web Console
- implement the Data Gateway
- connect trading-capable APIs
- access balances or positions
- access wallet keys
- place orders
- create Shadow Trading
- create automatic trading
- select final vendors
- modify frozen core
- modify Python production behavior

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

<!-- BEGIN FCF V2 LOCKED FUTURE DELIVERY BACKLOG -->
## 35. Locked Future Delivery Backlog

Status:

AUTHORITATIVE STRUCTURAL BACKLOG

Immediate next phase:

AI-ORCHESTRATION-RUNTIME-READINESS-APP-1

It remains readiness-only:

- no model invocation
- no prompt execution
- no automatic routing
- no archive writing
- no trading API
- no trading credentials
- no real execution

### Runtime and Product Foundation

1. AI-ORCHESTRATION-RUNTIME-READINESS-APP-1
2. READ-ONLY-DATA-GATEWAY-APP-1
3. RESEARCH-GATEWAY-APP-1
4. FCF-API-GATEWAY-APP-1
5. MULTI-MODEL-WORKFLOW-APP-1
6. FCF-WEB-CONSOLE-APP-1
7. ONE-CLICK-LOCAL-OPERATIONS-APP-1

### Mandatory Equity Adapters

- CHINA-A-SHARE-MARKET-ADAPTER-APP-1
- US-EQUITY-MARKET-ADAPTER-APP-1
- HONG-KONG-EQUITY-MARKET-ADAPTER-APP-1

### Mandatory Compatible Adapters

- GOLD-COMMODITY-MARKET-ADAPTER-APP-1
- DIGITAL-ASSET-MARKET-ADAPTER-APP-1
- FUTURES-MARKET-ADAPTER-APP-1

### Data and Research Infrastructure

- SOURCE-LICENSE-GOVERNANCE-APP-1
- DATA-FRESHNESS-POLICY-APP-1
- READ-ONLY-CREDENTIAL-VAULT-APP-1
- ONLINE-EVIDENCE-TRACEABILITY-APP-1

### Portfolio and Validation

- PORTFOLIO-CONSTRUCTION-APP-1
- PORTFOLIO-STRESS-TEST-APP-1
- MULTI-MARKET-VALIDATION-MATRIX-APP-1
- PAPER-PORTFOLIO-REVIEW-APP-1
- SHADOW-VALIDATION-PLANNING-APP-1

### Long-Term Independent Execution

Any execution work remains outside fcf-spec.

Candidate project:

fcf-execution-gateway

It requires separate approval, repository, credentials, deployment,
audit, risk engine, and Kill Switch.

No execution implementation is authorized by this backlog.
<!-- END FCF V2 LOCKED FUTURE DELIVERY BACKLOG -->

<!-- BEGIN FCF V2 LEARNING AND RUNTIME GOVERNANCE MIRROR -->
## 36. Controlled Learning, Backtesting, and Evolution

Status:

AUTHORITATIVE MIRROR OF THE CONTROL CENTER CONTRACT

Status:

APPROVED FUTURE ARCHITECTURE / AUTHORITATIVE STRUCTURAL BACKLOG /
NOT YET IMPLEMENTED

Planning baseline:

- repository baseline before this governance update:
  cd7a6284a339ae14ff8c611aa40ac6eeec21ea1a
- external DeepSeek and Gemini reviews are advisory inputs only
- accepted external findings have been corrected against FCF governance
- repository truth and explicit Operator approval remain authoritative

### 1. Constitutional Objective

FCF must develop a controlled learning, deterministic backtesting, and
governed evolution capability.

Backtesting and learning belong to one closed governance loop.

They must not be implemented as one mixed-authority component.

Authoritative responsibility split:

- backtesting proves and diagnoses
- result registries preserve evidence
- learning summarizes evidence and proposes candidates
- experiments compare Champion and Challenger
- governance gates approve or reject promotion
- version control activates approved changes
- monitoring detects degradation
- rollback protects the approved baseline
- the Operator retains final authority

No result from backtesting, learning, AI evaluation, or model consensus
may directly change production configuration.

### 2. Permanent Authority Boundary

Operator Policy
    >
FCF Hard Policy
    >
Deterministic Engine
    >
Validated Data and Evidence
    >
Experiment and Learning Orchestrator
    >
AI Models
    >
External Narrative

Python and deterministic services own:

- point-in-time data selection
- historical replay
- order and fill simulation
- transaction-cost calculation
- portfolio calculation
- factor calculation
- benchmark comparison
- statistical evaluation
- bias checks
- validation gates
- promotion eligibility calculations

AI may:

- explain results
- identify possible causes
- propose research hypotheses
- propose Challenger candidates
- compare preserved evidence
- identify contradictions
- summarize failure attribution
- suggest additional experiments

AI may not:

- self-score as the only evaluator
- alter backtest calculations
- alter historical results
- alter Outcome labels
- change hard policy
- change risk limits
- change privacy rules
- decide cloud eligibility
- modify Core
- replace Champion
- approve promotion
- activate configuration
- delete failed experiments
- delete audit history
- place or route real orders

### 3. Five-Layer Architecture

The controlled learning and backtesting architecture contains five
separate authority layers.

#### Layer 1: Point-in-Time Data and Rule Foundation

Required capabilities:

- immutable data-source version locking
- point-in-time data snapshots
- market-calendar version registry
- corporate-action version registry
- benchmark version registry
- strategy and runtime configuration snapshots
- universe-membership history
- delisting history
- source licensing metadata
- data freshness metadata
- data availability metadata
- checksums and content digests
- code commit and dependency version recording

Required time fields include:

- event_time
- published_at
- available_at
- ingested_at
- as_of_time
- retrieval_time
- fiscal_period_end where applicable
- report_release_time where applicable

Backtesting may only use information with:

available_at <= as_of_time

A document date or fiscal-period date is not sufficient evidence that
information was available to the system.

#### Layer 2: Deterministic Unified Backtest Engine

The backtest engine must remain deterministic and code-owned.

Required capabilities:

- historical point-in-time replay
- train, validation, and final test separation
- walk-forward validation
- purged and embargoed time-series validation where applicable
- regime-based evaluation
- portfolio-level simulation
- cost and slippage simulation
- liquidity and capacity simulation
- stress testing
- parameter perturbation
- data-delay perturbation
- market-specific fill logic
- deterministic failure attribution
- reproducible random seeds where stochastic simulation is used

AI must not calculate authoritative backtest values.

#### Layer 3: Result, Outcome, and Attribution Registry

Backtest results and subsequent real market outcomes must be immutable
registered artifacts.

Required registry classes:

- backtest result
- failed backtest result
- validation result
- walk-forward result
- stress-test result
- paper result
- shadow result when later approved
- Outcome label
- factor attribution
- portfolio attribution
- model attribution
- Prompt attribution
- data-source attribution
- failure attribution
- bias-review result

The learning layer has read-only access to these registries.

It cannot rewrite or delete registered results.

Failed, negative, blocked, and inconclusive results must be preserved.

Outcome labels are required during V2 paper research.

They must not be delayed until real trading or V3.

Possible Outcome observation horizons include policy-approved:

- short horizon
- medium horizon
- long horizon
- event horizon
- reporting-cycle horizon

Every Outcome label must preserve the original prediction, observation
window, actual result, data version, and evaluation policy.

#### Layer 4: Controlled Learning and Challenger Experiment

The learning layer may learn from:

- data-source reliability
- model-role performance
- Prompt performance
- factor and strategy performance
- portfolio behavior
- market regime
- operator feedback
- subsequent observed outcomes
- operational failures
- cost and latency
- missing or contradictory evidence

Learning outputs are candidates, not production changes.

Supported candidate types:

- model-role assignment candidate
- fallback-model candidate
- Prompt candidate
- data-source policy candidate
- factor candidate
- strategy-configuration candidate
- portfolio-control candidate
- timeout or retry candidate
- market-adapter rule candidate

Every candidate must enter a sandbox experiment.

#### Layer 5: Promotion, Monitoring, and Rollback Gate

A Challenger may become Champion only after:

1. static eligibility review
2. hard-policy review
3. data-license review
4. future-information dependency review
5. declared configuration-difference review
6. historical backtesting
7. independent out-of-sample testing
8. walk-forward testing
9. regime testing
10. cost and liquidity testing
11. bias review
12. counterfactual and robustness testing
13. Champion comparison
14. risk review
15. explicit Operator approval
16. versioned activation
17. post-activation monitoring
18. rollback readiness

Promotion must create a new version.

Promotion must never overwrite the previous Champion.

### 4. Configuration Snapshot Contract

Every backtest and experiment must record a Config Snapshot.

Required fields include:

- config_snapshot_id
- code_commit
- deterministic-engine version
- strategy version
- factor version
- factor weights
- portfolio-policy version
- market-adapter version
- data-source versions
- dataset digests
- universe version
- market-calendar version
- corporate-action version
- benchmark version
- model-role assignments
- model identifiers
- model versions
- known model-training cutoff where available
- model-training-cutoff status when unknown
- Prompt identifiers
- Prompt versions
- tool versions
- policy version
- output-schema version
- fee assumptions
- tax assumptions
- slippage assumptions
- liquidity assumptions
- funding assumptions
- roll assumptions where applicable
- random seed where applicable
- experiment variable manifest

Champion and Challenger comparisons do not require identical snapshots.

They require:

- all unchanged variables to remain locked
- every changed variable to be explicitly declared
- single-variable experiments where practical
- compound-experiment labeling when multiple variables change
- no unsupported attribution of improvement to one variable when several
  variables changed

### 5. Challenger Qualification Review

Before consuming backtest resources, each Challenger must pass static
qualification.

The qualification review must check:

- no Core mutation
- no P48
- no hard-policy conflict
- no unauthorized data source
- no unlicensed data use
- no unauthorized cloud processing
- no future-data dependency
- no hidden change to risk calculation
- no hidden change to benchmark
- no hidden change to costs
- no undeclared model or Prompt change
- no undeclared market-rule change
- no real execution path
- no automatic promotion authority

Rejected qualification records must be preserved.

### 6. Historical AI Replay Modes

FCF must distinguish two AI replay modes.

#### HISTORICAL_REPRODUCTION

Purpose:

Reproduce what the system could have produced at the historical time.

Requirements:

- historical data snapshot
- historical Prompt version
- historical configuration
- historical policy
- historical model version where available
- no online search beyond the historical snapshot
- no current external evidence
- explicit as_of_time

#### COUNTERFACTUAL_CURRENT_MODEL_EVALUATION

Purpose:

Evaluate a current model using only historical evidence.

Requirements:

- current model is explicitly identified
- result is labeled counterfactual
- result must not be represented as a historical production decision
- historical evidence only
- no live internet retrieval
- knowledge-leakage probes
- fact-alignment evaluation
- separate comparison against deterministic-only baseline

A Prompt instruction stating "do not use future information" is not a
sufficient leakage control.

Running a model locally is not a sufficient leakage control because the
model may already contain later knowledge in its trained parameters.

### 7. AI Knowledge-Leakage Guard

Required protections include:

- historical evidence isolation
- no uncontrolled live search during replay
- as_of_time enforcement
- published_at and available_at enforcement
- current-model counterfactual labeling
- model-version registration
- known or unknown training-cutoff status
- future-event sentinel questions
- synthetic false-future probes
- unsupported-future-claim detection
- evidence-link validation
- retrieval-log validation
- prompt and tool-call audit
- critical leakage status = BLOCKED

A replay containing demonstrated future-information leakage cannot be
used for promotion.

### 8. AI Fact and Reason Alignment

Correct economic performance does not prove that AI reasoning was
correct.

Every important AI claim must be separately evaluated for:

- evidence support
- factual correctness
- temporal availability
- causal consistency
- contradiction handling
- unsupported assumptions
- omitted risk
- citation correctness
- explanation stability
- counterevidence visibility

Critical unsupported claims must be zero for promotion eligibility.

A profitable result with incorrect reasoning must be labeled:

RESULT_CORRECT_REASONING_UNSUPPORTED

It cannot be treated as evidence that the AI reasoning process improved.

### 9. Counterfactual and Robustness Testing

No single perturbation test is sufficient.

The robustness suite should include policy-approved combinations of:

- feature ablation
- evidence ablation
- negative-control variables
- label permutation
- time-block permutation
- regime-transfer testing
- parameter perturbation
- execution-delay perturbation
- data-availability-delay perturbation
- cost and slippage stress
- liquidity stress
- missing-data stress
- data-source failure
- model failure
- adversarial evidence
- incorrect contextual narrative
- removal of the strongest supporting evidence

Randomly shuffling industry or macro labels may be one experiment.

It must not be the sole promotion gate.

### 10. Bias Guard

Mandatory bias controls include:

- look-ahead bias
- survivorship bias
- selection bias
- universe-membership leakage
- delisting omission
- corporate-action errors
- data revision leakage
- publication-time leakage
- availability-time leakage
- benchmark leakage
- target leakage
- repeated holdout reuse
- validation-set overfitting
- hyperparameter overfitting
- multiple testing
- data snooping
- cherry-picking
- failed-result deletion
- transaction-cost omission
- liquidity omission
- capacity omission

Final holdout data must not be repeatedly reused for tuning.

When the final holdout has influenced a design decision, it is no longer
a final untouched holdout.

### 11. Validation Structure

Validation should use:

- development data
- validation data
- final untouched test data
- multiple non-overlapping time windows
- walk-forward windows
- market-regime partitions
- stress scenarios
- paper observation
- later Shadow observation when separately approved

The exact number of windows and thresholds must be configurable,
versioned, and approved.

No universal fixed threshold such as 30 percent conflict, 0.5 percent
improvement, or a fixed number of months is part of the constitution.

### 12. Benchmark Governance

Each market and strategy must use a versioned benchmark policy.

The Benchmark Registry must support:

- primary benchmark
- secondary benchmark
- cash or risk-free reference
- industry benchmark where relevant
- asset-class benchmark
- benchmark total-return methodology
- currency treatment
- benchmark rebalancing history
- benchmark constituent history
- benchmark availability time

No specific index is permanently hardcoded into the constitution.

Every report must distinguish:

- absolute performance
- gross performance
- net performance
- benchmark-relative performance
- risk-adjusted performance

### 13. Mandatory Evaluation Dimensions

Financial and portfolio metrics should include:

- gross return
- net return after costs
- benchmark excess return
- maximum drawdown
- volatility
- downside risk
- risk-adjusted return
- turnover
- transaction costs
- liquidity usage
- capacity
- tail loss
- worst regime
- worst evaluation window
- recovery time
- stability across windows
- out-of-sample decay

Prediction and calibration metrics should include where applicable:

- directional accuracy
- precision and recall
- calibration error
- Brier score
- false-positive rate
- false-negative rate
- confidence reliability

AI-governance metrics should include:

- supported-claim rate
- critical unsupported-claim count
- citation correctness
- temporal-leakage count
- risk-omission rate
- contradiction-detection value
- explanation stability
- model disagreement
- AI incremental value
- AI incremental risk
- cost and latency

AI incremental value must compare at least:

- deterministic-only baseline
- deterministic plus AI
- Champion
- Challenger

AI must demonstrate added value after costs and risk, not merely improved
writing quality.

### 14. Statistical Evidence Policy

A single p-value is not a sufficient promotion criterion.

Statistical evidence may include:

- bootstrap confidence intervals
- block bootstrap
- probabilistic Sharpe ratio
- deflated Sharpe ratio
- multiple-testing correction
- effect size
- out-of-sample decay
- parameter stability
- regime stability
- paired-window comparison

Statistical significance does not override:

- hard policy
- unacceptable drawdown
- critical unsupported AI claims
- data leakage
- licensing failure
- operator rejection

### 15. Multi-Market Backtest Rules

Every market requires a versioned adapter and fill model.

#### China A-Shares

Required considerations:

- point-in-time universe membership
- T+1 sell restriction where applicable
- limit-up and limit-down states
- sealed-limit liquidity
- queue and fill uncertainty
- ST and special-treatment status
- suspension
- listing-board rules
- fees and taxes
- corporate actions
- delisting
- trading calendar

A limit-up or limit-down day is not automatically classified as
untradable in every direction.

Fill logic must use market state, direction, price, available volume, and
approved conservative assumptions.

#### Hong Kong Equities

Required considerations:

- board lot by security and effective date
- odd-lot handling
- auction sessions
- trading sessions
- HKD and approved dual-counter structures
- Stock Connect rules where applicable
- fees and taxes
- corporate actions
- short-sale eligibility
- currency effects
- settlement
- liquidity

No fixed board-lot size may be hardcoded for all Hong Kong securities.

#### United States Equities

Required considerations:

- regular session
- pre-market and after-hours sessions
- session-specific liquidity
- exchange calendar
- delisting
- splits and dividends
- corporate actions
- short-borrow availability where applicable
- fees
- currency effects
- settlement
- point-in-time SEC and company filings

#### Gold and Commodities

Gold must distinguish:

- spot gold
- delivery futures
- gold ETFs
- gold-mining equities

Required considerations include:

- trading session
- financing and carry
- futures expiry
- roll cost
- ETF tracking difference
- currency
- contract specification
- liquidity

#### BTC and Digital Assets

Required considerations include:

- continuous trading
- venue fragmentation
- funding rates
- mark price
- index price
- liquidation
- margin
- fees
- order-book depth
- exchange outage
- custody and counterparty risk

Perpetual contracts do not use traditional expiry roll logic.

Delivery futures and dated contracts require expiry and roll treatment.

#### Futures

Required considerations include:

- contract specification
- contract multiplier
- expiry
- roll policy
- margin
- limit moves
- settlement
- basis
- term structure
- dominant-contract method
- continuous-contract construction
- liquidity migration
- fees and slippage

### 16. Human Feedback Governance

Human feedback is evidence, not automatic truth.

Required fields include:

- feedback_id
- operator_id
- feedback_timestamp
- related_artifact_ids
- information available at feedback time
- feedback type
- reason
- evidence
- pre-outcome or post-hoc status
- conflict status
- review status

Post-hoc feedback must be explicitly labeled.

It must not be treated as if it was known at the original decision time.

When human feedback conflicts with deterministic evaluation:

- preserve both
- create a HUMAN_AUTO_EVALUATION_CONFLICT artifact
- record the evidence on both sides
- require explicit conflict review
- require a second confirmation by the Operator where no independent
  second Operator exists
- block promotion until conflict resolution

No universal 30 percent conflict threshold is authorized.

### 17. Feedback Pollution and Self-Reinforcement Guard

The system must prevent:

- a model evaluating itself as the only judge
- one model family acting as proposer, evaluator, and approver
- operator preference being mistaken for market truth
- post-hoc information entering pre-outcome training labels
- successful outcomes hiding incorrect reasoning
- repeated use of the same validation period
- promotion because a Challenger agrees with Champion
- learning only from successful cases
- deletion of failed experiments
- automatic reinforcement of frequently selected models

Evaluation should use deterministic metrics and, where appropriate,
independent comparison models.

No model consensus may replace evidence.

### 18. Learning Pause, Monitor, and Restart

Continuous experimentation is not always beneficial.

The learning system must support:

- ACTIVE_EXPERIMENT
- MONITOR_ONLY
- PAUSED_DATA_QUALITY
- PAUSED_BUDGET
- PAUSED_POLICY
- PAUSED_REPEATED_FAILURE
- RESTART_REQUIRED
- OPERATOR_STOPPED

Possible transition reasons include:

- no material Challenger improvement
- stable Champion
- degraded data quality
- stale data
- unreliable benchmark
- excessive experimentation cost
- repeated overfitting
- repeated validation failure
- unresolved feedback conflict
- model or data drift
- Operator instruction

Exact thresholds must remain configurable and versioned.

Drift detection or explicit Operator approval may restart experiments.

### 19. Read-Only Learning Evidence Flow

Approved flow:

Point-in-Time Data
    ->
Deterministic Backtest
    ->
Bias and Validation Review
    ->
Immutable Result Registry
    ->
Outcome and Attribution
    ->
Controlled Learning
    ->
Challenger Proposal
    ->
Sandbox Experiment
    ->
Promotion Gate
    ->
Operator Approval
    ->
Versioned Activation
    ->
Monitoring
    ->
Rollback When Required

Forbidden flow:

Learning Candidate
    ->
rewrite Backtest Result

Forbidden flow:

AI Recommendation
    ->
automatic Champion replacement

Forbidden flow:

Operator Preference
    ->
rewrite historical Outcome

### 20. Canonical Structural Backlog

The following capabilities must not be omitted.

Related capabilities may be delivered in one larger Sidecar program, but
their contracts and validations must remain explicit.

#### P0: Point-in-Time and Version Foundation

- DATA-SOURCE-VERSION-LOCK-APP-1
- POINT-IN-TIME-SNAPSHOT-APP-1
- MARKET-CALENDAR-REGISTRY-APP-1
- CORPORATE-ACTION-REGISTRY-APP-1
- CONFIG-SNAPSHOT-REGISTRY-APP-1
- BENCHMARK-REGISTRY-APP-1

#### P1: Deterministic Unified Backtest and Outcome Foundation

- UNIFIED-MULTI-MARKET-BACKTEST-APP-1
- BACKTEST-BIAS-GUARD-APP-1
- WALK-FORWARD-VALIDATION-APP-1
- BACKTEST-RESULT-REGISTRY-APP-1
- OUTCOME-LABEL-REGISTRY-APP-1
- FACTOR-AND-PORTFOLIO-ATTRIBUTION-APP-1

#### P2: AI Historical Evaluation

- AI-POINT-IN-TIME-REPLAY-APP-1
- AI-KNOWLEDGE-LEAKAGE-GUARD-APP-1
- AI-FACT-ALIGNMENT-EVALUATION-APP-1
- MODEL-ROLE-PERFORMANCE-APP-1
- AI-INCREMENTAL-VALUE-EVALUATION-APP-1

#### P3: Controlled Learning and Evolution

- HUMAN-FEEDBACK-LEARNING-APP-1
- CHAMPION-CHALLENGER-EXPERIMENT-APP-1
- CONTROLLED-EVOLUTION-GATE-APP-1
- PROMOTION-ROLLBACK-APP-1
- LEARNING-LOOP-AUDIT-APP-1

#### P4: Deferred Enhancements

- CASE-MEMORY-RETRIEVAL-APP-1
- AUTOMATIC-CHALLENGER-PROPOSAL-APP-1
- REALTIME-SHADOW-VALIDATION-APP-1
- AUTOMATIC-EXPERIMENT-SCHEDULER-APP-1
- SPECIALIST-MODEL-TRAINING-APP-1

P4 items require a stable P0-P3 foundation.

### 21. Delivery and Dependency Rules

The immediate implementation phase remains unchanged:

AI-ORCHESTRATION-RUNTIME-READINESS-APP-1

This learning and backtesting architecture does not authorize immediate
implementation of P0-P4.

The current readiness phase remains:

- readiness-only
- no live model invocation
- no Prompt execution
- no automatic routing
- no automatic archive
- no archive writing
- no real execution
- no trading API
- no trading credentials

The future Read-Only Data Gateway must preserve the fields and contracts
required by this architecture, including:

- source version
- availability time
- point-in-time snapshot
- license
- checksum
- market calendar
- corporate action
- universe membership
- benchmark version
- Config Snapshot linkage

This requirement prevents future backtest rework.

### 22. Scope and Supersession

This block:

- records the approved future architecture
- preserves the six previously locked V2 constitutional decisions
- preserves the current development order
- does not mutate Core
- does not start a new Sidecar
- does not approve model invocation
- does not approve automatic learning
- does not approve automatic promotion
- does not approve Shadow Trading
- does not approve real execution
- does not approve tag, release, or deployment

External DeepSeek, Gemini, OpenAI, Claude, local-model, community-skill,
or other opinions remain advisory inputs only.

No external recommendation may silently change this architecture.

Any future change requires:

1. explicit Operator approval
2. Architecture Decision Record
3. impact analysis
4. privacy and safety review
5. migration and rollback plan
6. validation
7. Control Center update
8. handoff update where required
9. versioned activation

## 37. Runtime Governance and Complete Discussion Lock

Status:

AUTHORITATIVE MIRROR OF THE CONTROL CENTER COMPLETENESS LOCK

Status:

APPROVED / AUTHORITATIVE / STRUCTURALLY COMPLETE /
NOT YET IMPLEMENTED

This block consolidates all architecture decisions produced in the
current V2 architecture discussion.

It does not start implementation.

### 1. Product Surface

FCF V2 requires a custom browser-based FCF Web Console.

Required capabilities:

- PDF upload
- Excel upload
- CSV upload
- JSON upload
- text input
- URL input
- multi-file upload
- controlled research conversation
- workflow monitoring
- evidence inspection
- model comparison
- disagreement visibility
- risk-flag visibility
- Portfolio Construction display
- Paper portfolio display
- comprehensive reports
- operator approval and rejection
- re-analysis
- additional-evidence requests
- explicit override reasons
- one-click start and stop
- health, cost, failure, and degradation visibility

Normal product use must not require Python or PowerShell.

### 2. Workflow and Models

- Dify is a replaceable background workflow implementation.
- Open WebUI is development-only.
- FCF uses a stable API boundary.
- Model roles are vendor-neutral.
- Hybrid is the default mode.
- Deterministic policy controls cloud eligibility.
- Models cannot choose their own permissions.
- Structured output is mandatory.
- Model and Prompt versions are registered.
- Retry, fallback, timeout, cost, and cancellation are governed.
- Disagreement remains visible.
- System confidence is deterministic.
- AI does not own truth, approval, archive, policy, or execution.

### 3. Data, Research, and Credentials

Required boundaries:

- isolated Read-Only Data Gateway
- isolated Research Gateway
- credential-owning collector boundary
- Class A, B, and C source governance
- licensing metadata
- permitted-use metadata
- freshness metadata
- available-time metadata
- checksums
- evidence identifiers
- citation traceability
- retrieval traceability

Approved read-only credentials may exist only inside the isolated
gateway.

They must be encrypted, masked, and excluded from AI context, reports,
and normal logs.

Prohibited:

- trading credentials
- withdrawal credentials
- wallet credentials
- account-changing credentials
- unrestricted AI database writes

### 4. Market Coverage

Mandatory versioned adapters:

- China A-shares
- United States equities
- Hong Kong equities
- gold and commodities
- BTC and digital assets
- futures

Market adapters must preserve market-specific:

- calendars
- sessions
- auctions
- settlement
- fees
- taxes
- currency
- corporate actions
- universe membership
- liquidity
- capacity
- fill rules

Specific requirements include:

- A-share T+1 and price-limit behavior
- Hong Kong board-lot and odd-lot behavior
- United States regular and extended sessions
- BTC funding, mark price, liquidation, and venue fragmentation
- futures expiry, margin, basis, and roll rules

Perpetual contracts do not use traditional expiry-roll assumptions.

### 5. Portfolio Construction

Portfolio Construction is mandatory after deterministic ranking.

It is not a seventh selection factor.

Deterministic, configurable, and versioned controls include:

- asset concentration
- industry concentration
- theme concentration
- factor concentration
- correlation
- beta
- volatility
- liquidity
- drawdown
- turnover
- transaction costs
- risk budget
- Paper position sizing

No constitutional percentage is permanently hardcoded.

AI may explain risk.

AI may not calculate, modify, or approve authoritative weights.

### 6. Execution Boundary

FCF V2 ends at:

- research
- evidence
- analysis
- reports
- Paper portfolios
- human review

FCF V2 contains no real order placement.

Any future execution capability requires a separate:

- repository
- permission domain
- credential domain
- deployment boundary
- audit boundary
- risk-control boundary

A future execution gateway may reject, delay, cancel, block, or reduce
approved risk.

It may never increase risk, increase quantity, relax limits, change the
asset, bypass approval, or weaken a Kill Switch.

### 7. Controlled Learning and Backtesting

The complete 22-section learning, deterministic-backtesting, and
governed-evolution architecture already recorded in this Control Center
is authoritative.

It includes:

- point-in-time snapshots
- data-source version locking
- market-calendar registration
- corporate-action registration
- Benchmark Registry
- Config Snapshot
- deterministic multi-market backtesting
- Bias Guard
- train, validation, final holdout, and Walk-forward separation
- regime, stress, cost, liquidity, and capacity tests
- immutable successful and failed results
- Outcome labels during V2 Paper research
- factor, portfolio, model, Prompt, source, and failure attribution
- HISTORICAL_REPRODUCTION
- COUNTERFACTUAL_CURRENT_MODEL_EVALUATION
- AI knowledge-leakage protection
- factual and reasoning alignment evaluation
- AI incremental-value evaluation
- human feedback governance
- post-hoc feedback labeling
- HUMAN_AUTO_EVALUATION_CONFLICT
- Champion and Challenger experiments
- promotion gates
- monitoring
- rollback
- pause and restart
- explicit Operator approval
- no automatic production evolution

### 8. Active Authority Set

Active authority files:

1. docs/FCF_PROJECT_CONTROL_CENTER.md
2. docs/FCF_V2_PRODUCT_AND_AI_RUNTIME_ARCHITECTURE.md
3. docs/HANDOFF_PROMPT.md
4. FCF_PROJECT_BACKEND_HANDOFF_NEXT_WINDOW.md
5. FCF_NEW_WINDOW_CHAT_PROMPT.md

Historical Master Final, Final Current State, audit, and old handoff
documents remain immutable historical evidence.

### 9. Runtime Governance Materialization

The Control Center is authoritative for human and engineering
governance.

Markdown alone is not runtime enforcement.

Future implementation must create:

- machine-readable policy manifests
- stable policy identifiers
- policy versions
- policy content digests
- Config Snapshot policy linkage
- startup policy checks
- pre-workflow policy checks
- fail-closed behavior
- privacy-routing blocks
- missing-evidence blocks
- promotion blocks
- archive-authorization blocks
- execution-path blocks inside fcf-spec
- Web Console policy status
- BLOCKED and DEGRADED states
- policy audit records
- Markdown-to-runtime drift detection
- approved policy activation
- policy rollback

AI may read approved policy.

AI may not modify, activate, weaken, or bypass policy.

### 10. Mandatory Runtime-Governance Backlog

The following requirements must not be omitted:

- CONTROL-CENTER-MACHINE-READABLE-MANIFEST-APP-1
- GOVERNANCE-POLICY-REGISTRY-APP-1
- GOVERNANCE-CONTRACT-CI-GUARD-APP-1
- CONTROL-HANDOFF-TRUTH-SYNC-GUARD-APP-1
- ARCHITECTURE-BACKLOG-DEPENDENCY-GUARD-APP-1
- RUNTIME-POLICY-GATE-APP-1
- STARTUP-CONFIG-VERSION-CHECK-APP-1
- POLICY-VIOLATION-BLOCK-APP-1
- CONSOLE-GOVERNANCE-STATUS-APP-1
- POLICY-AUDIT-ROLLBACK-APP-1

These contracts may be delivered inside larger Sidecar phases, but their
contracts and tests must remain explicit.

### 11. Dependency Requirements

AI-ORCHESTRATION-RUNTIME-READINESS-APP-1 must prepare:

- machine-readable role contracts
- policy identifiers
- routing eligibility
- timeout, retry, fallback, and cost contracts
- BLOCKED and DEGRADED states
- policy and Config Snapshot linkage

It remains readiness-only:

- no model invocation
- no Prompt execution
- no automatic routing

Read-Only Data Gateway must preserve:

- source version
- published time
- available time
- ingestion time
- checksum
- license
- retention permission
- cloud-processing permission
- market calendar
- universe membership
- corporate actions
- benchmark version
- point-in-time snapshot linkage

FCF API Gateway must enforce:

- authentication
- authorization
- policy
- schemas
- correlation
- idempotency where required
- rate and cost limits
- audit emission
- fail-closed behavior

Multi-Model Workflow routes only through approved policy gates.

Web Console displays policy, evidence, disagreement, risk, cost, health,
degradation, and review status.

Backtesting and learning use the same registered policy, data, code,
model, Prompt, market-adapter, and Config Snapshot versions.

### 12. Cross-Document Synchronization

A major architectural decision is incomplete until all active authority
files are synchronized.

Future synchronization must verify:

- current Control Center truth
- current V2 architecture truth
- current docs handoff truth
- current backend handoff truth
- current new-window truth
- current validation baseline
- current restrictions
- current next phase
- absence of contradictory active headers

The newest explicit top truth header overrides older historical sections.

### 13. Current Development Order

Immediate next phase:

AI-ORCHESTRATION-RUNTIME-READINESS-APP-1

Status:

PLANNED / NOT STARTED / READINESS-ONLY

Not currently authorized:

- live model invocation
- Prompt execution
- automatic routing
- automatic archive
- archive writing
- automatic learning activation
- automatic Champion promotion
- Shadow Trading
- real execution
- trading APIs
- trading credentials
- tag
- release
- deployment

### 14. Supersession

External models, reports, slides, community skills, workflow tools, and
future chat windows are advisory only.

They cannot silently remove, weaken, or replace these requirements.

Any divergence between the Control Center and this mirror must produce a BLOCKED governance state until reconciled.
<!-- END FCF V2 LEARNING AND RUNTIME GOVERNANCE MIRROR -->
