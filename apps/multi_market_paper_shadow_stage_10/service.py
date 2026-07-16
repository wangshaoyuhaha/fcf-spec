from __future__ import annotations

from decimal import Decimal
from types import MappingProxyType

from apps.multi_market_adapters_stage_6 import AdapterStatus, MarketAdapterId

from .boundary import MULTI_MARKET_PAPER_SHADOW_BOUNDARY
from .contracts import (
    MarketValidationFinding,
    MultiMarketValidationOutcome,
    MultiMarketValidationRequest,
    ShadowMaturity,
    ValidationStatus,
    utc_time,
)


_EXPECTED_MARKETS = frozenset(MarketAdapterId)


class MultiMarketPaperShadowValidationService:
    def evaluate(
        self,
        request: MultiMarketValidationRequest,
    ) -> MultiMarketValidationOutcome:
        MULTI_MARKET_PAPER_SHADOW_BOUNDARY.__post_init__()
        paper = {item.adapter_id: item for item in request.paper_markets}
        shadow = {item.adapter_id: item for item in request.shadow_markets}
        missing_paper = _EXPECTED_MARKETS - set(paper)
        missing_shadow = _EXPECTED_MARKETS - set(shadow)
        findings = []
        global_reasons = []
        paper_excess_values = []
        mature_errors = []
        signs = set()

        if missing_paper:
            global_reasons.append("missing-paper-market-coverage")
        if missing_shadow:
            global_reasons.append("missing-shadow-market-coverage")

        for adapter_id in sorted(_EXPECTED_MARKETS, key=lambda item: item.value):
            paper_item = paper.get(adapter_id)
            shadow_item = shadow.get(adapter_id)
            reasons = []
            evidence = set()
            excess = None
            shadow_error = None
            if paper_item is None:
                reasons.append("paper-market-missing")
            else:
                evidence.update(paper_item.evidence_ids)
                excess = paper_item.candidate_return - paper_item.benchmark_return
                paper_excess_values.append(excess)
                signs.add(excess.compare(Decimal("0")))
                if paper_item.adapter_status is AdapterStatus.BLOCKED:
                    reasons.append("market-adapter-blocked")
                elif paper_item.adapter_status is AdapterStatus.DEGRADED:
                    reasons.append("market-adapter-degraded")
                if paper_item.data_quality_state == "BLOCKED":
                    reasons.append("data-quality-blocked")
                elif paper_item.data_quality_state == "DEGRADED":
                    reasons.append("data-quality-degraded")
                if paper_item.freshness_state != "CURRENT":
                    reasons.append("data-freshness-review")
                if excess < 0:
                    reasons.append("paper-underperformed-benchmark")
                reasons.extend(paper_item.exposure_breach_codes)
            if shadow_item is None:
                reasons.append("shadow-market-missing")
            else:
                evidence.update(shadow_item.evidence_ids)
                if paper_item is not None and utc_time(
                    shadow_item.decision_time_utc,
                    "decision_time_utc",
                ) < utc_time(paper_item.end_time_utc, "end_time_utc"):
                    reasons.append("historical-forward-window-overlap")
                if shadow_item.maturity is ShadowMaturity.PENDING:
                    reasons.append("shadow-window-pending")
                else:
                    shadow_error = (
                        shadow_item.observed_return - shadow_item.expected_return
                    )
                    mature_errors.append(shadow_error)
                    if (
                        shadow_item.expected_return != 0
                        and shadow_item.observed_return != 0
                        and (
                            shadow_item.expected_return > 0
                        ) != (
                            shadow_item.observed_return > 0
                        )
                    ):
                        reasons.append("shadow-direction-contradiction")
            blocked = any(
                reason in {
                    "paper-market-missing",
                    "shadow-market-missing",
                    "market-adapter-blocked",
                    "data-quality-blocked",
                    "historical-forward-window-overlap",
                }
                for reason in reasons
            )
            status = (
                ValidationStatus.BLOCKED_REVIEW_REQUIRED
                if blocked
                else (
                    ValidationStatus.DEGRADED_REVIEW_REQUIRED
                    if reasons
                    else ValidationStatus.PASS_REVIEW_REQUIRED
                )
            )
            findings.append(
                MarketValidationFinding(
                    adapter_id=adapter_id,
                    status=status,
                    paper_excess_return=excess,
                    shadow_error=shadow_error,
                    reason_codes=tuple(sorted(set(reasons))),
                    evidence_ids=tuple(sorted(evidence)),
                )
            )

        if any(
            item.status is ValidationStatus.BLOCKED_REVIEW_REQUIRED
            for item in findings
        ):
            status = ValidationStatus.BLOCKED_REVIEW_REQUIRED
        elif any(
            item.status is ValidationStatus.DEGRADED_REVIEW_REQUIRED
            for item in findings
        ):
            status = ValidationStatus.DEGRADED_REVIEW_REQUIRED
        else:
            status = ValidationStatus.PASS_REVIEW_REQUIRED
        disagreement = len(signs - {Decimal("0")}) > 1
        if disagreement:
            global_reasons.append("cross-market-paper-disagreement")
            if status is ValidationStatus.PASS_REVIEW_REQUIRED:
                status = ValidationStatus.DEGRADED_REVIEW_REQUIRED
        global_reasons.extend(
            reason for finding in findings for reason in finding.reason_codes
        )
        denominator = Decimal(len(_EXPECTED_MARKETS))
        paper_coverage = Decimal(len(paper)) / denominator
        shadow_coverage = Decimal(len(shadow)) / denominator
        mature_coverage = Decimal(
            sum(
                item.maturity is ShadowMaturity.MATURE
                for item in shadow.values()
            )
        ) / denominator
        aggregate_paper = (
            sum(paper_excess_values, Decimal("0"))
            / Decimal(len(paper_excess_values))
            if paper_excess_values
            else Decimal("0")
        )
        aggregate_shadow = (
            sum(mature_errors, Decimal("0")) / Decimal(len(mature_errors))
            if mature_errors
            else None
        )
        packet = MappingProxyType(
            {
                "automatic_approval_allowed": False,
                "automatic_learning_allowed": False,
                "automatic_promotion_allowed": False,
                "correlation_id": request.correlation_id,
                "disagreement_visible": disagreement,
                "finding_count": len(findings),
                "mature_shadow_coverage": str(mature_coverage),
                "operator_review_required": True,
                "paper_market_coverage": str(paper_coverage),
                "portfolio_artifact_id": request.portfolio_artifact_id,
                "reason_codes": tuple(sorted(set(global_reasons))),
                "request_id": request.request_id,
                "shadow_market_coverage": str(shadow_coverage),
                "status": status.value,
            }
        )
        return MultiMarketValidationOutcome(
            request=request,
            status=status,
            findings=tuple(findings),
            paper_market_coverage=paper_coverage,
            shadow_market_coverage=shadow_coverage,
            mature_shadow_coverage=mature_coverage,
            aggregate_paper_excess_return=aggregate_paper,
            aggregate_shadow_error=aggregate_shadow,
            disagreement_visible=disagreement,
            reason_codes=tuple(global_reasons),
            operator_review_packet=packet,
        )


def build_console_sections(
    outcome: MultiMarketValidationOutcome,
):
    return MappingProxyType(
        {
            "multi_market_validation": (
                MappingProxyType(
                    {
                        "correlation_id": outcome.request.correlation_id,
                        "disagreement_visible": outcome.disagreement_visible,
                        "market_count": len(outcome.findings),
                        "reason_codes": outcome.reason_codes,
                        "status": outcome.status.value,
                    }
                ),
            ),
            "paper_portfolio_validation": (
                MappingProxyType(
                    {
                        "aggregate_excess_return": str(
                            outcome.aggregate_paper_excess_return
                        ),
                        "coverage": str(outcome.paper_market_coverage),
                        "operator_review_required": True,
                    }
                ),
            ),
            "shadow_market_observation": (
                MappingProxyType(
                    {
                        "aggregate_shadow_error": (
                            None
                            if outcome.aggregate_shadow_error is None
                            else str(outcome.aggregate_shadow_error)
                        ),
                        "mature_coverage": str(outcome.mature_shadow_coverage),
                        "network_access_used": False,
                        "real_execution_used": False,
                    }
                ),
            ),
        }
    )
