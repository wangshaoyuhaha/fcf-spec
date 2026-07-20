from dataclasses import FrozenInstanceError, replace
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType

import pytest

from apps.browser_product_console_runtime_app_1 import (
    BrowserProductConsoleApplication,
    ConsoleReadModel,
)
from apps.fcp_0008_chinese_browser_console_local_data_intake_preview_app_1 import (
    LocalizedBrowserConsoleApplication,
)
from apps.fcp_0009_provider_neutral_market_data_adapter_readiness_app_1 import (
    FCP_0009_BOUNDARY,
    AdapterActivationGate,
    MarketDataDiagnosticsConsoleApplication,
    MarketDataFieldMap,
    ProviderNeutralMarketDataAdapter,
    ProviderNeutralMarketDataAdapterBoundary,
    RegisteredMarketDataObservation,
    build_registered_local_replay_fixture,
    evaluate_market_data_adapter_readiness,
)
from apps.v2_r24_local_multi_clock_event_state_foundation_app_1 import (
    LocalMultiClockEventStateRegistry,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import (
    BoundedLocalEventIngress,
    LocalEventEnvelope,
    LocalEventRights,
)


def _tick_map() -> MarketDataFieldMap:
    return MarketDataFieldMap(
        mapping_id="tick-map-test",
        market="A-SHARE",
        observation_kind="TICK",
        registered_artifact_id="registered-market-fixture",
        canonical_to_source={
            "instrument_id": "symbol",
            "event_at": "timestamp",
            "last": "price",
            "volume": "volume",
        },
        rights=LocalEventRights(
            license_id="registered-test-fixture-only",
            permitted_use="synthetic-local-evaluation-only",
            retention_days=1,
        ),
    )


def _tick(**updates: object) -> RegisteredMarketDataObservation:
    values = {
        "observation_id": "tick-observation-test-1",
        "mapping_id": "tick-map-test",
        "source_sequence": 1,
        "received_at_utc": "2026-07-20T06:00:01Z",
        "processed_at_utc": "2026-07-20T06:00:02Z",
        "payload": {
            "symbol": "000001.XSHE",
            "timestamp": "2026-07-20T06:00:00Z",
            "price": "12.34",
            "volume": "100",
        },
    }
    values.update(updates)
    return RegisteredMarketDataObservation(**values)  # type: ignore[arg-type]


def _adapter() -> ProviderNeutralMarketDataAdapter:
    return ProviderNeutralMarketDataAdapter(
        mappings=(_tick_map(),),
        ingress=BoundedLocalEventIngress(capacity=8, ttl_seconds=3600),
    )


def _console() -> MarketDataDiagnosticsConsoleApplication:
    model = ConsoleReadModel(
        correlation_id="corr-fcp-0009-test",
        candidates=(),
        sections=MappingProxyType({}),
        source_artifact_ids=(),
    )
    base = LocalizedBrowserConsoleApplication(
        base_application=BrowserProductConsoleApplication(model)
    )
    _, snapshot = build_registered_local_replay_fixture()
    return MarketDataDiagnosticsConsoleApplication(base, snapshot)


def test_d1_boundary_is_closed_and_immutable() -> None:
    assert FCP_0009_BOUNDARY.composes_v2_r3_ingress is True
    assert FCP_0009_BOUNDARY.composes_v2_r24_clock_state is True
    assert FCP_0009_BOUNDARY.external_network_allowed is False
    assert FCP_0009_BOUNDARY.trading_or_execution_allowed is False
    with pytest.raises(FrozenInstanceError):
        FCP_0009_BOUNDARY.local_only = False  # type: ignore[misc]


@pytest.mark.parametrize(
    "update",
    (
        {"external_network_allowed": True},
        {"credentials_allowed": True},
        {"provider_selection_allowed": True},
        {"realtime_activation_allowed": True},
        {"trading_or_execution_allowed": True},
    ),
)
def test_d1_boundary_rejects_added_authority(update: dict[str, bool]) -> None:
    with pytest.raises(ValueError, match="cannot be weakened"):
        ProviderNeutralMarketDataAdapterBoundary(**update)


def test_d1_activation_gate_is_closed() -> None:
    gate = AdapterActivationGate()
    assert gate.external_activation_state == "BLOCKED"
    assert gate.provider_selection_state == "UNSELECTED"
    with pytest.raises(ValueError, match="cannot be opened"):
        AdapterActivationGate(network_state="ENABLED")


def test_d2_field_map_is_exact_immutable_and_hashed() -> None:
    mapping = _tick_map()
    assert isinstance(mapping.canonical_to_source, MappingProxyType)
    assert len(mapping.mapping_hash) == 64
    with pytest.raises(TypeError):
        mapping.canonical_to_source["last"] = "other"  # type: ignore[index]


def test_d2_field_map_rejects_missing_or_duplicate_source_fields() -> None:
    with pytest.raises(ValueError, match="closed canonical schema"):
        MarketDataFieldMap(
            mapping_id="bad-map",
            market="A-SHARE",
            observation_kind="TICK",
            registered_artifact_id="artifact",
            canonical_to_source={"instrument_id": "symbol"},
            rights=_tick_map().rights,
        )
    with pytest.raises(ValueError, match="source fields must be unique"):
        MarketDataFieldMap(
            mapping_id="bad-map",
            market="A-SHARE",
            observation_kind="TICK",
            registered_artifact_id="artifact",
            canonical_to_source={
                "instrument_id": "same",
                "event_at": "timestamp",
                "last": "same",
                "volume": "volume",
            },
            rights=_tick_map().rights,
        )


def test_d2_field_map_cannot_select_provider() -> None:
    with pytest.raises(ValueError, match="cannot select a provider"):
        replace(_tick_map(), provider_selection_state="SELECTED")


def test_d2_field_map_requires_explicit_registered_local_rights() -> None:
    with pytest.raises(ValueError, match="explicit registered local rights"):
        replace(_tick_map(), rights="implicit")  # type: ignore[arg-type]


def test_d2_normalizes_tick_to_v2_r3_envelope() -> None:
    normalized = _adapter().normalize(_tick())
    assert isinstance(normalized.envelope, LocalEventEnvelope)
    assert normalized.envelope.source_id == "provider-neutral-local-replay"
    assert normalized.envelope.event_type == "MARKET_DATA_TICK"
    assert normalized.envelope.payload["last"] == Decimal("12.34")
    assert normalized.envelope.rights.network_retrieval_allowed is False
    assert normalized.envelope.rights is normalized.mapping.rights


def test_d2_rejects_binary_float_and_missing_source_field() -> None:
    payload = dict(_tick().payload)
    payload["price"] = 12.34
    with pytest.raises(ValueError, match="binary float"):
        _adapter().normalize(_tick(payload=payload))
    payload.pop("price")
    with pytest.raises(ValueError, match="missing mapped source"):
        _adapter().normalize(_tick(payload=payload))


def test_d3_registered_local_replay_composes_v2_r3_sequence_guard() -> None:
    adapter, _, receipt = _adapter().replay(
        _tick(), as_of_utc="2026-07-20T06:00:03Z"
    )
    assert receipt.status == "ACCEPTED"
    assert adapter.ingress.last_sequences[
        "market:A-SHARE:000001.XSHE:tick"
    ] == 1
    with pytest.raises(ValueError, match="duplicate event_id"):
        adapter.replay(_tick(), as_of_utc="2026-07-20T06:00:03Z")


def test_d3_adapter_composes_v2_r24_registry_without_selecting_state() -> None:
    adapter = _adapter()
    assert isinstance(adapter.clock_registry, LocalMultiClockEventStateRegistry)
    snapshot = evaluate_market_data_adapter_readiness(
        adapter,
        market="A-SHARE",
        as_of_utc="2026-07-20T06:00:03Z",
    )
    assert snapshot.clock_state == "MISSING"
    assert "NO_ACTIVE_MULTI_CLOCK_STATE" in snapshot.degradation_codes


def test_d4_complete_local_fixture_is_ready_but_external_activation_blocked() -> None:
    adapter, snapshot = build_registered_local_replay_fixture()
    assert len(adapter.ingress.events) == 3
    assert snapshot.local_replay_state == "READY_FOR_LOCAL_REPLAY"
    assert snapshot.external_activation_state == "BLOCKED"
    assert snapshot.entitlement_state == "UNRESOLVED"
    assert snapshot.provider_selection_state == "UNSELECTED"
    assert snapshot.max_transport_latency_ms == 1000


def test_d4_stale_heartbeat_degrades_local_replay() -> None:
    adapter, _ = build_registered_local_replay_fixture()
    snapshot = evaluate_market_data_adapter_readiness(
        adapter,
        market="A-SHARE",
        as_of_utc="2026-07-20T07:00:03Z",
        heartbeat_timeout_seconds=120,
    )
    assert snapshot.local_replay_state == "DEGRADED"
    assert "STALE_LOCAL_HEARTBEAT" in snapshot.degradation_codes


def test_d4_snapshot_collections_are_immutable_and_hash_is_stable() -> None:
    _, first = build_registered_local_replay_fixture()
    _, second = build_registered_local_replay_fixture()
    assert first.snapshot_hash == second.snapshot_hash
    assert isinstance(first.mapping_coverage, MappingProxyType)
    with pytest.raises(TypeError):
        first.mapping_coverage["TICK"] = "MISSING"  # type: ignore[index]


def test_d5_diagnostics_page_is_chinese_read_only_and_safe() -> None:
    response = _console().dispatch("GET", "/market-data-diagnostics")
    body = response.body.decode("utf-8")
    assert response.status == 200
    assert "\u5e02\u573a\u6570\u636e\u8bca\u65ad" in body
    assert "READY_FOR_LOCAL_REPLAY" in body
    assert "BLOCKED" in body
    assert "<form" not in body and "<button" not in body and "<script" not in body


def test_d5_diagnostics_supports_english_head_and_rejects_post() -> None:
    english = _console().dispatch("GET", "/market-data-diagnostics?lang=en")
    assert english.status == 200
    assert "Market Data Diagnostics" in english.body.decode("utf-8")
    head = _console().dispatch("HEAD", "/market-data-diagnostics")
    assert head.status == 200 and head.body == b""
    post = _console().dispatch("POST", "/market-data-diagnostics")
    assert post.status == 405


def test_d5_existing_health_route_remains_machine_readable() -> None:
    response = _console().dispatch("GET", "/health")
    assert response.status == 200
    assert response.content_type == "application/json; charset=utf-8"
    assert b'"operator_review_required": true' in response.body


def test_d5_existing_html_routes_gain_diagnostics_navigation() -> None:
    response = _console().dispatch("GET", "/?lang=en")
    assert response.status == 200
    assert "/market-data-diagnostics" in response.body.decode("utf-8")


def test_d6_sources_are_ascii_and_contain_no_network_clients() -> None:
    app_root = Path(
        "apps/fcp_0009_provider_neutral_market_data_adapter_readiness_app_1"
    )
    paths = tuple(app_root.glob("*.py")) + (
        Path("scripts/run_fcp_0009_market_data_adapter_readiness.py"),
        Path("scripts/run_fcp_0009_market_data_diagnostics_console.py"),
    )
    text = "\n".join(path.read_text(encoding="ascii") for path in paths).lower()
    for prohibited in (
        "import requests",
        "import socket",
        "urllib.request",
        "websocket",
        "api_key",
        "access_token",
    ):
        assert prohibited not in text


def test_d6_fixture_and_snapshot_do_not_claim_product_evidence() -> None:
    adapter, snapshot = build_registered_local_replay_fixture()
    assert adapter.activation_gate.product_evidence_state == "BLOCKED"
    assert snapshot.operator_review_required is True
