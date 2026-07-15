from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImplementationStage:
    order: int
    stage_id: str
    required_capabilities: tuple[str, ...]


IMPLEMENTATION_STAGES = (
    ImplementationStage(1, "READ-ONLY-DATA-GATEWAY-APP-1", (
        "point-in-time-source-envelope",
        "registered-read-only-input",
        "license-and-freshness-fields",
    )),
    ImplementationStage(2, "DATA-AND-CREDENTIAL-GOVERNANCE", (
        "SOURCE-LICENSE-GOVERNANCE-APP-1",
        "DATA-FRESHNESS-POLICY-APP-1",
        "READ-ONLY-CREDENTIAL-VAULT-APP-1",
    )),
    ImplementationStage(3, "RESEARCH-AND-EVIDENCE-GATEWAYS", (
        "RESEARCH-GATEWAY-APP-1",
        "ONLINE-EVIDENCE-TRACEABILITY-APP-1",
    )),
    ImplementationStage(4, "FCF-API-GATEWAY-APP-1", (
        "authentication",
        "authorization",
        "policy-gate",
        "correlation",
        "idempotency",
    )),
    ImplementationStage(5, "MULTI-MODEL-WORKFLOW-APP-1", (
        "policy-approved-routing",
        "bounded-timeout-retry-fallback",
        "cost-and-health-status",
    )),
    ImplementationStage(6, "MULTI-MARKET-ADAPTERS", (
        "CHINA-A-SHARE-MARKET-ADAPTER-APP-1",
        "US-EQUITY-MARKET-ADAPTER-APP-1",
        "HONG-KONG-EQUITY-MARKET-ADAPTER-APP-1",
        "GOLD-COMMODITY-MARKET-ADAPTER-APP-1",
        "DIGITAL-ASSET-MARKET-ADAPTER-APP-1",
        "FUTURES-MARKET-ADAPTER-APP-1",
    )),
    ImplementationStage(7, "PORTFOLIO-AND-STRESS", (
        "PORTFOLIO-CONSTRUCTION-APP-1",
        "PORTFOLIO-STRESS-TEST-APP-1",
    )),
    ImplementationStage(8, "FCF-WEB-CONSOLE-APP-1", (
        "file-upload",
        "controlled-research-conversation",
        "workflow-control",
        "governance-status",
    )),
    ImplementationStage(9, "ONE-CLICK-LOCAL-OPERATIONS-APP-1", (
        "non-technical-start-stop",
        "health-check",
        "failure-guidance",
    )),
    ImplementationStage(10, "MULTI-MARKET-PAPER-VALIDATION", (
        "MULTI-MARKET-VALIDATION-MATRIX-APP-1",
        "PAPER-PORTFOLIO-REVIEW-APP-1",
        "SHADOW-VALIDATION-PLANNING-APP-1",
    )),
    ImplementationStage(11, "CONTROLLED-LEARNING-P0-P3", (
        "point-in-time-foundation",
        "deterministic-unified-backtest",
        "AI-historical-evaluation",
        "Champion-Challenger-governance",
    )),
    ImplementationStage(12, "DEFERRED-LEARNING-P4", (
        "stable-P0-P3-required",
        "separate-Operator-approval-required",
    )),
)


@dataclass(frozen=True)
class ImplementationOrderReport:
    status: str
    stage_count: int
    reason_codes: tuple[str, ...]


def validate_implementation_order(
    stages: tuple[ImplementationStage, ...] = IMPLEMENTATION_STAGES,
) -> ImplementationOrderReport:
    reasons: list[str] = []
    orders = tuple(stage.order for stage in stages)
    stage_ids = tuple(stage.stage_id for stage in stages)

    if orders != tuple(range(1, len(stages) + 1)):
        reasons.append("NON_CONTIGUOUS_ORDER")
    if len(set(stage_ids)) != len(stage_ids):
        reasons.append("DUPLICATE_STAGE_ID")
    if not stages or stages[0].stage_id != "READ-ONLY-DATA-GATEWAY-APP-1":
        reasons.append("INVALID_FIRST_RUNTIME_STAGE")
    if stages and stages[-1].stage_id != "DEFERRED-LEARNING-P4":
        reasons.append("DEFERRED_STAGE_NOT_LAST")
    if any(not stage.required_capabilities for stage in stages):
        reasons.append("EMPTY_STAGE_CAPABILITIES")

    return ImplementationOrderReport(
        status="PASS" if not reasons else "BLOCKED",
        stage_count=len(stages),
        reason_codes=tuple(reasons),
    )
