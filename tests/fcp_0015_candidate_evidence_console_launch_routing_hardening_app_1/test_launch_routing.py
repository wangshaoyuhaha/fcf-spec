import pytest

from scripts.run_fcp_0013_candidate_evidence_bundle import (
    build_operator_url as build_bundle_url,
)
from scripts.run_fcp_0014_candidate_evidence_gap_remediation import (
    build_operator_url as build_remediation_url,
)


@pytest.mark.parametrize("language", ("zh-CN", "en"))
def test_bundle_launcher_targets_exact_registered_route(language: str) -> None:
    assert build_bundle_url(18769, language) == (
        f"http://127.0.0.1:18769/data-source-evidence-bundle?lang={language}"
    )


@pytest.mark.parametrize("language", ("zh-CN", "en"))
def test_remediation_launcher_targets_exact_registered_route(language: str) -> None:
    assert build_remediation_url(18770, language) == (
        f"http://127.0.0.1:18770/data-source-evidence-remediation?lang={language}"
    )


@pytest.mark.parametrize("builder", (build_bundle_url, build_remediation_url))
def test_launch_url_rejects_unregistered_language(builder) -> None:
    with pytest.raises(ValueError, match="language must be zh-CN or en"):
        builder(8765, "unsafe")
