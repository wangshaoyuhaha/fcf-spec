import hashlib
from dataclasses import replace

import pytest

from apps.fcp_0022_btc_local_export_canonicalization_bridge_app_1 import (
    BTCLocalExportBridgeResult,
)
from apps.fcp_0022_btc_local_export_canonicalization_bridge_app_1.contracts import (
    canonical_observations_ndjson,
)
from tests.fcp_0019_a_share_local_export_canonicalization_bridge_app_1.test_d1_d6 import (
    _bridge as a_share_bridge,
)
from tests.fcp_0019_a_share_local_export_canonicalization_bridge_app_1.test_d1_d6 import (
    _bytes as a_share_bytes,
)
from tests.fcp_0019_a_share_local_export_canonicalization_bridge_app_1.test_d1_d6 import (
    _write as write_a_share,
)
from tests.fcp_0022_btc_local_export_canonicalization_bridge_app_1.test_d1_d6 import (
    _bridge as btc_bridge,
)
from tests.fcp_0022_btc_local_export_canonicalization_bridge_app_1.test_d1_d6 import (
    _bytes as btc_bytes,
)


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def a_share_result(tmp_path):
    raw = a_share_bytes()
    return a_share_bridge(write_a_share(tmp_path / "source.csv", raw), raw)


def btc_result(tmp_path):
    raw = btc_bytes()
    path = tmp_path / "source.ndjson"
    path.write_bytes(raw)
    return btc_bridge(path, raw)


def test_exact_bridge_results_remain_valid(tmp_path):
    a_share_result(tmp_path)
    btc_result(tmp_path)


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("artifact_sha256", "a" * 64, "registration digest"),
        ("byte_length", 1, "byte length"),
    ],
)
def test_a_share_result_rejects_registration_disagreement(
    tmp_path, field, value, match
):
    result = a_share_result(tmp_path)
    registration = replace(result.canonical_registration, **{field: value})

    with pytest.raises(ValueError, match=match):
        replace(result, canonical_registration=registration)


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("canonical_artifact_sha256", "b" * 64, "manifest digest"),
        ("row_count", 99, "row count"),
    ],
)
def test_a_share_result_rejects_manifest_disagreement(
    tmp_path, field, value, match
):
    result = a_share_result(tmp_path)
    manifest = replace(result.manifest, **{field: value})

    with pytest.raises(ValueError, match=match):
        replace(result, manifest=manifest)


class FakeObservation:
    observation_hash = "c" * 64


def test_btc_result_rejects_structural_observation_impersonation(tmp_path):
    result = btc_result(tmp_path)

    with pytest.raises(ValueError, match="typed observations"):
        replace(result, observations=(FakeObservation(),))


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("content_sha256", "d" * 64, "registration digest"),
        ("byte_length", 1, "byte length"),
    ],
)
def test_btc_result_rejects_registration_disagreement(tmp_path, field, value, match):
    result = btc_result(tmp_path)
    registration = replace(result.canonical_registration, **{field: value})

    with pytest.raises(ValueError, match=match):
        replace(result, canonical_registration=registration)


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("canonical_artifact_id", "different-artifact", "artifact identity"),
        ("canonical_artifact_sha256", "e" * 64, "manifest digest"),
        ("observation_hashes", ("f" * 64,), "observation hashes"),
    ],
)
def test_btc_result_rejects_manifest_disagreement(tmp_path, field, value, match):
    result = btc_result(tmp_path)
    manifest = replace(result.manifest, **{field: value})

    with pytest.raises(ValueError, match=match):
        replace(result, manifest=manifest)


def test_btc_result_rejects_observation_artifact_lineage_disagreement(tmp_path):
    result = btc_result(tmp_path)
    first = result.observations[0]
    changed_first = replace(
        first,
        header=replace(first.header, artifact_id="different-artifact"),
    )
    observations = (changed_first, *result.observations[1:])
    canonical = canonical_observations_ndjson(observations)
    registration = replace(
        result.canonical_registration,
        content_sha256=digest(canonical),
        byte_length=len(canonical),
    )
    manifest = replace(
        result.manifest,
        canonical_artifact_sha256=digest(canonical),
        observation_hashes=tuple(item.observation_hash for item in observations),
    )

    with pytest.raises(ValueError, match="artifact lineage"):
        BTCLocalExportBridgeResult(canonical, registration, observations, manifest)


def test_btc_result_rejects_bytes_that_disagree_with_typed_observations(tmp_path):
    result = btc_result(tmp_path)
    canonical = b'{}\n'
    registration = replace(
        result.canonical_registration,
        content_sha256=digest(canonical),
        byte_length=len(canonical),
    )
    manifest = replace(
        result.manifest,
        canonical_artifact_sha256=digest(canonical),
    )

    with pytest.raises(ValueError, match="typed observations"):
        BTCLocalExportBridgeResult(
            canonical,
            registration,
            result.observations,
            manifest,
        )
