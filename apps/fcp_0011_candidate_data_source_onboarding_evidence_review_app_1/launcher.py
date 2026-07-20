from pathlib import Path

from apps.browser_product_console_runtime_app_1 import BrowserConsoleRuntime
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (
    MarketDataAdapterReadinessSnapshot,
)
from apps.fcp_0010_simplified_chinese_console_localization_consistency_app_1 import (
    build_simplified_chinese_console_runtime,
)

from .application import CandidateDataSourceOnboardingApplication
from .contracts import CandidateSourceProfile


def build_candidate_data_source_onboarding_runtime(
    *,
    allowed_root: Path,
    index_path: Path,
    snapshot: MarketDataAdapterReadinessSnapshot,
    profiles: tuple[CandidateSourceProfile, ...],
    port: int = 8765,
    title: str = "FCF Browser Product Console",
    locale_id: str = "zh-CN",
) -> BrowserConsoleRuntime:
    base = build_simplified_chinese_console_runtime(
        allowed_root=allowed_root,
        index_path=index_path,
        snapshot=snapshot,
        port=port,
        title=title,
        locale_id=locale_id,
    )
    application = CandidateDataSourceOnboardingApplication(
        base_application=base.application,
        profiles=profiles,
    )
    return BrowserConsoleRuntime(
        config=base.config,
        index_path=base.index_path,
        application=application,
    )
