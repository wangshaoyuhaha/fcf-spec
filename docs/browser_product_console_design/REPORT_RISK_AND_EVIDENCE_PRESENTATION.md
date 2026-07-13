# Browser Product Console Report, Risk, and Evidence Presentation

## Phase

BROWSER-PRODUCT-CONSOLE-DESIGN-APP-1

## Delivery

D4 - Report, Risk, Contradiction, and Evidence Presentation

## Status

DESIGN_ONLY

NO_RUNTIME_IMPLEMENTATION

## Presentation authority

The Browser Product Console presents registered artifacts.

It does not calculate authoritative financial results.

It does not replace deterministic validation.

It does not convert AI text into an approved conclusion.

It does not replace Operator review.

## Report workspace

The report workspace must distinguish:

- report title
- report identifier
- report version
- report state
- workspace identifier
- run identifier
- correlation identifier
- creation timestamp
- last validation timestamp
- deterministic result version
- AI comparison version
- Config Snapshot
- Schema version
- Prompt version
- Operator review status
- archive eligibility

Report states include:

- DRAFT
- VALIDATING
- BLOCKED
- REVIEW_REQUIRED
- RETURNED_FOR_REVISION
- APPROVED
- REJECTED
- ARCHIVE_ELIGIBLE
- ARCHIVED

The console must not display a draft as approved.

The console must not display REVIEW_REQUIRED as complete.

## Report sections

A report view may contain:

- executive summary
- deterministic findings
- market context
- controlled AI comparison
- causal reasoning chain
- scenario simulation
- contrarian challenge
- risk register
- contradiction register
- evidence references
- provenance
- validation results
- Operator rationale
- limitations
- archive references

Every generated summary must remain traceable to registered source artifacts.

## Risk presentation

Risk flags must be presented as first-class governed data.

Each visible risk item must include:

- risk identifier
- risk category
- severity
- source artifact
- source field
- deterministic or AI origin
- status
- blocking status
- explanation
- evidence references
- correlation identifier
- review requirement

Allowed severity labels are:

- INFO
- LOW
- MEDIUM
- HIGH
- CRITICAL

A CRITICAL risk must not be hidden, collapsed by default, or replaced by
summary language.

A blocking risk must remain visible until the governing state changes.

The console must not reduce multiple raw risk flags into an untraceable score.

## Contradiction presentation

Contradictions must be displayed separately from ordinary risk flags.

Each contradiction must identify:

- contradiction identifier
- left-side claim
- right-side claim
- source artifacts
- source versions
- contradiction category
- severity
- unresolved or resolved status
- resolution rationale
- resolving actor
- correlation identifier

An unresolved contradiction must remain visible in the report and review packet.

AI agreement must not resolve a deterministic contradiction automatically.

Operator approval must include explicit acknowledgement of unresolved
contradictions when policy permits approval.

## Evidence chain

Every report conclusion must expose an evidence path.

The evidence path may reference:

- Data Snapshot
- Candidate artifact
- deterministic result
- AI explanation
- scenario result
- contrarian challenge
- UI packet
- review packet
- report packet
- archive packet
- handoff record
- final current-state record

Each evidence node must display:

- artifact identifier
- artifact type
- artifact version
- content hash when available
- producer
- production timestamp
- correlation identifier
- parent references
- validation status
- archive status

The console must preserve the distinction between evidence, interpretation,
summary, and decision.

## Provenance presentation

Provenance must show:

- source identity
- source type
- collection timestamp
- licensing status
- privacy classification
- transformation history
- Schema version
- validation history
- Config Snapshot
- model registration when applicable
- Prompt version when applicable
- Operator decision history

Missing provenance must block complete-status presentation.

## AI output presentation

Controlled AI outputs must display:

- model slot
- provider
- model version
- Prompt version
- evaluation baseline
- privacy eligibility
- cloud eligibility
- provider-health state
- cost state
- source candidate identity
- response status
- limitations
- risk flags
- evidence references

AI output must be visually labelled ASSISTIVE_ONLY.

AI output must not be labelled authoritative, approved, or final.

Provider unavailability must remain visible.

## Operator review packet

The review packet must display:

- deterministic conclusion
- AI comparison
- raw risk flags
- contradictions
- evidence chain
- provenance
- missing-artifact blockers
- validation results
- report version
- correlation identifier
- prior review history

Approve, reject, and return-for-revision actions require explicit human confirmation and rationale.

The review packet must not contain an automatic approval control.

## Export boundary

A future export may produce a paper-only report package.

Export eligibility requires:

- required artifacts present
- validation complete
- Operator decision recorded
- unresolved blockers absent
- correlation identifier present
- report version fixed
- evidence references fixed

Export is not archive.

Export is not release.

Export is not deployment.

Export must not create a real trading instruction.

## Failure and stale states

The console must identify:

- missing artifact
- stale artifact
- failed validation
- broken evidence reference
- mismatched correlation identifier
- unsupported Schema version
- unavailable provider
- unresolved contradiction
- incomplete Operator review

A stale or incomplete report must not be presented as current and complete.

## D4 acceptance contract

D4 is accepted only when:

- report states are explicit
- risk flags remain first-class data
- contradictions remain separately visible
- evidence paths are traceable
- provenance is explicit
- AI outputs remain assistive only
- Operator review requires explicit confirmation
- export remains paper-only
- missing or stale artifacts block complete presentation
- no runtime implementation is created
