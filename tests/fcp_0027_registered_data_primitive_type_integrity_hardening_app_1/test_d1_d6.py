import pytest

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1 import (
    DailyLayerManifest,
    RegisteredDailyArtifact,
)
from apps.fcp_0018_btc_trusted_market_data_substrate_local_replay_app_1 import (
    BTCBookDelta,
    BTCObservationHeader,
    BTCRegisteredArtifact,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1 import (
    LocalDailyExportBridgeManifest,
    LocalDailyExportProfile,
    RegisteredLocalDailyExport,
)
from apps.fcp_0019_a_share_local_export_canonicalization_bridge_app_1.contracts import (
    REQUIRED_PRICE_SEMANTICS,
)
from apps.fcp_0022_btc_local_export_canonicalization_bridge_app_1 import (
    BTCLocalExportBridgeManifest,
    RegisteredBTCLocalExport,
)
from apps.v2_r3_local_event_ingress_foundation_app_1 import LocalEventRights


DIGEST = "a" * 64
UPPER_DIGEST = "A" * 64
UTC = "2026-07-21T00:00:00Z"


def rights() -> LocalEventRights:
    return LocalEventRights("license-local", "research", 1)


def btc_header(**updates) -> BTCObservationHeader:
    values = {
        "observation_id": "observation-1",
        "artifact_id": "artifact-1",
        "venue_id": "venue-1",
        "instrument_id": "BTC-USD",
        "instrument_kind": "SPOT",
        "observation_kind": "TRADE",
        "source_sequence": 1,
        "event_at_utc": UTC,
        "received_at_utc": UTC,
        "ingested_at_utc": UTC,
        "schema_version": 1,
    }
    values.update(updates)
    return BTCObservationHeader(**values)


@pytest.mark.parametrize("value", [UPPER_DIGEST, " " + DIGEST, DIGEST.encode("ascii")])
def test_btc_substrate_rejects_nonexact_digest(value):
    with pytest.raises(ValueError, match="lowercase SHA-256"):
        BTCRegisteredArtifact("artifact-1", value, 1, rights())


@pytest.mark.parametrize("value", [UPPER_DIGEST, " " + DIGEST, DIGEST.encode("ascii")])
def test_btc_bridge_rejects_nonexact_registration_digest(value):
    with pytest.raises(ValueError, match="lowercase SHA-256"):
        RegisteredBTCLocalExport(
            "artifact-1", "source-1", value, 1, UTC, rights()
        )


def test_btc_bridge_manifest_rejects_nonexact_digests():
    with pytest.raises(ValueError, match="lowercase SHA-256"):
        BTCLocalExportBridgeManifest(
            "source-artifact",
            UPPER_DIGEST,
            "canonical-artifact",
            DIGEST,
            DIGEST,
            (DIGEST,),
            UTC,
        )


@pytest.mark.parametrize(
    "factory",
    [
        lambda: RegisteredDailyArtifact(
            "artifact-1",
            "source-1",
            DIGEST,
            1.5,
            UTC,
            "UNRESOLVED",
            "UNRESOLVED",
        ),
        lambda: DailyLayerManifest(
            "RAW",
            "artifact-1",
            DIGEST,
            DIGEST,
            1.5,
            "v1",
            "transform-1",
            "UNRESOLVED",
            "UNRESOLVED",
        ),
        lambda: RegisteredLocalDailyExport(
            "artifact-1",
            "source-1",
            DIGEST,
            1.5,
            UTC,
            "UNRESOLVED",
            "UNRESOLVED",
        ),
        lambda: LocalDailyExportBridgeManifest(
            DIGEST, DIGEST, DIGEST, DIGEST, 1.5, ()
        ),
        lambda: BTCRegisteredArtifact("artifact-1", DIGEST, 1.5, rights()),
        lambda: RegisteredBTCLocalExport(
            "artifact-1", "source-1", DIGEST, 1.5, UTC, rights()
        ),
        lambda: btc_header(source_sequence=1.5),
        lambda: btc_header(schema_version=1.5),
    ],
)
def test_fractional_integral_contract_values_are_rejected(factory):
    with pytest.raises(ValueError):
        factory()


def test_btc_book_delta_rejects_fractional_previous_sequence():
    header = btc_header(
        observation_kind="BOOK_DELTA",
        source_sequence=2,
    )
    with pytest.raises(ValueError, match="previous_sequence"):
        BTCBookDelta(header, 1.5, (), ())


@pytest.mark.parametrize(
    "field",
    ["raw_repository_storage_allowed", "provider_selected"],
)
def test_a_share_export_rejects_false_like_closed_flags(field):
    updates = {field: 0}
    with pytest.raises(ValueError, match="cannot grant"):
        RegisteredLocalDailyExport(
            "artifact-1",
            "source-1",
            DIGEST,
            1,
            UTC,
            "UNRESOLVED",
            "UNRESOLVED",
            **updates,
        )


def test_a_share_profile_rejects_false_like_provider_selection():
    fields = (*REQUIRED_PRICE_SEMANTICS, "instrument_id")
    with pytest.raises(ValueError, match="provider-unselected"):
        LocalDailyExportProfile(
            "profile-1",
            "source-1",
            fields,
            {name: name for name in fields},
            provider_selected=0,
        )


@pytest.mark.parametrize(
    "field",
    ["raw_repository_storage_allowed", "provider_selected"],
)
def test_btc_export_rejects_false_like_closed_flags(field):
    updates = {field: 0}
    with pytest.raises(ValueError, match="registered-local"):
        RegisteredBTCLocalExport(
            "artifact-1", "source-1", DIGEST, 1, UTC, rights(), **updates
        )


def test_btc_manifest_rejects_false_like_provider_selection():
    with pytest.raises(ValueError, match="cannot bypass"):
        BTCLocalExportBridgeManifest(
            "source-artifact",
            DIGEST,
            "canonical-artifact",
            DIGEST,
            DIGEST,
            (DIGEST,),
            UTC,
            provider_selected=0,
        )


def test_exact_registered_values_remain_valid():
    RegisteredDailyArtifact(
        "artifact-1",
        "source-1",
        DIGEST,
        1,
        UTC,
        "UNRESOLVED",
        "UNRESOLVED",
    )
    BTCRegisteredArtifact("artifact-1", DIGEST, 1, rights())
    RegisteredLocalDailyExport(
        "artifact-1",
        "source-1",
        DIGEST,
        1,
        UTC,
        "UNRESOLVED",
        "UNRESOLVED",
    )
    RegisteredBTCLocalExport(
        "artifact-1", "source-1", DIGEST, 1, UTC, rights()
    )
