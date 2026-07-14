# BROWSER-PRODUCT-CONSOLE-EVIDENCE-AUDIT-EXPLORER-APP-1 D2

## Status

COMPLETED_ON_SIDECAR

## Scope

D2 implements deterministic correlation lineage, provenance relationships, and
a registered-artifact-only evidence graph.

## Delivered

- EvidenceArtifactGraph immutable registered evidence graph
- EvidenceCorrelationLineage deterministic correlation summary
- EvidenceProvenanceStep typed traversal step
- EvidenceProvenanceChain deterministic upstream chain
- explicit AVAILABLE, EMPTY, and INCOMPLETE graph states
- registered artifact node construction from ConsoleReadModel
- content SHA-256 and registered path preservation
- explicit relationship field allowlist
- DERIVED_FROM relationships
- VALIDATES relationships
- REVIEWS relationships
- ARCHIVES relationships
- CORRELATES_WITH relationships
- CONTRADICTS relationships
- unresolved registered reference reporting
- duplicate relationship collapse
- self-reference rejection
- malformed relationship field rejection
- deterministic node and edge ordering
- cycle-safe provenance traversal
- bounded provenance depth
- read-only graph lookup and adjacency

## Relationship direction

Each relationship is directed from the evidence artifact containing the
registered relationship field to the referenced registered artifact.

Examples:

- Candidate DERIVED_FROM Data Snapshot
- Paper Validation VALIDATES Candidate
- Operator Review REVIEWS Paper Validation
- Report Archive ARCHIVES Operator Review

Unregistered references are not converted into graph nodes. They are reported
as unresolved and the graph becomes INCOMPLETE.

## Permanent boundary

- P1-P47 frozen
- no P48
- paper-only
- local-only
- loopback-only
- sidecar-only
- registered-artifact-only
- read-only product presentation
- Operator review mandatory
- Deterministic Engine authority preserved
- Registered Evidence remains evidence authority
- AI advisory only
- no evidence mutation
- no source artifact mutation
- no record deletion
- no command or workflow dispatch
- no public network exposure
- no external data fetching
- no broker, exchange, credentials, account, balance, position, wallet,
  order, or real execution path
- no automatic approval, promotion, baseline replacement, model activation,
  Prompt activation, learning activation, or archive
- no tag, release, or deployment

D2 does not parse risk flags, contradiction evidence, or AI evidence. Those
capabilities begin in D3.
