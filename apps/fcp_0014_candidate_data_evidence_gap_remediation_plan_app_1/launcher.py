from pathlib import Path

from apps.browser_product_console_runtime_app_1 import BrowserConsoleRuntime
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (
    MarketDataAdapterReadinessSnapshot,
)
from apps.fcp_0011_candidate_data_source_onboarding_evidence_review_app_1 import (
    CandidateSourceProfile,
)
from apps.fcp_0012_sanitized_candidate_data_session_evidence_intake_app_1 import (
    CandidateSessionEvidence,
    RegisteredSessionEvidenceArtifact,
)
from apps.fcp_0013_candidate_data_evidence_bundle_reconciliation_app_1 import (
    CandidateEvidenceBundle,
    build_candidate_evidence_bundle_runtime,
)

from .application import EvidenceGapRemediationApplication
from .contracts import CandidateEvidenceGapRemediationPlan


def build_evidence_gap_remediation_runtime(
    *,
    allowed_root: Path,
    index_path: Path,
    snapshot: MarketDataAdapterReadinessSnapshot,
    profiles: tuple[CandidateSourceProfile, ...],
    profile: CandidateSourceProfile,
    registration: RegisteredSessionEvidenceArtifact,
    evidence: CandidateSessionEvidence,
    bundle: CandidateEvidenceBundle,
    plan: CandidateEvidenceGapRemediationPlan,
    port: int = 8765,
    title: str = "FCF Browser Product Console",
    locale_id: str = "zh-CN",
) -> BrowserConsoleRuntime:
    base = build_candidate_evidence_bundle_runtime(
        allowed_root=allowed_root,
        index_path=index_path,
        snapshot=snapshot,
        profiles=profiles,
        profile=profile,
        registration=registration,
        evidence=evidence,
        bundle=bundle,
        port=port,
        title=title,
        locale_id=locale_id,
    )
    application = EvidenceGapRemediationApplication(base.application, plan)
    return BrowserConsoleRuntime(config=base.config, index_path=base.index_path, application=application)
