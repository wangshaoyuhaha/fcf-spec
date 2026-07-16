from dataclasses import replace
from types import MappingProxyType

import pytest

from apps.research_and_evidence_gateways import (
    RESEARCH_AND_EVIDENCE_BOUNDARY,
    ResearchQuery,
    ResearchSource,
    SourceClass,
    require_https_url,
)


def _source(**updates):
    values = dict(
        source_id="source-a", source_url="https://research.example.com/report",
        source_class=SourceClass.A, trust_level="high",
        license_policy_id="license-policy-a", freshness_policy_id="freshness-policy-a",
        evidence_id="source-evidence-a",
    )
    values.update(updates)
    return ResearchSource(**values)


def test_d1_boundary_rejects_transport_credentials_and_execution():
    for field in ("arbitrary_network_transport_allowed", "authenticated_request_allowed", "credential_material_allowed", "browser_automation_allowed", "scraping_allowed", "order_path_allowed"):
        with pytest.raises(ValueError, match="prohibited research gateway"):
            replace(RESEARCH_AND_EVIDENCE_BOUNDARY, **{field: True})


def test_d1_source_is_immutable_normalized_and_reviewable():
    source = _source()
    assert source.trust_level == "HIGH"
    assert isinstance(source.as_payload(), MappingProxyType)
    with pytest.raises(TypeError):
        source.as_payload()["source_id"] = "tampered"


@pytest.mark.parametrize("url", (
    "http://research.example.com/report", "https://user@research.example.com/report",
    "https://research.example.com/report#section", "https://localhost/report",
    "https://RESEARCH.example.com/report",
))
def test_d1_url_contract_rejects_unsafe_or_noncanonical_values(url):
    with pytest.raises(ValueError, match="source_url"):
        require_https_url(url)


def test_d1_query_is_normalized_sorted_and_loopback_only():
    query = ResearchQuery("query-a", "correlation-a", "  BTC   evidence  ", "2026-07-16T10:00:00Z", ("source-b", "source-a", "source-a"))
    assert query.query_text == "BTC evidence"
    assert query.approved_source_ids == ("source-a", "source-b")
    with pytest.raises(ValueError, match="exactly 127.0.0.1"):
        replace(query, peer_host="localhost")


def test_d1_query_requires_sources_utc_and_review():
    with pytest.raises(ValueError, match="must not be empty"):
        ResearchQuery("query-a", "correlation-a", "BTC", "2026-07-16T10:00:00Z", ())
    with pytest.raises(ValueError, match="must be UTC"):
        ResearchQuery("query-a", "correlation-a", "BTC", "2026-07-16T18:00:00+08:00", ("source-a",))
    with pytest.raises(ValueError, match="operator_review_required"):
        replace(ResearchQuery("query-a", "correlation-a", "BTC", "2026-07-16T10:00:00Z", ("source-a",)), operator_review_required=False)
