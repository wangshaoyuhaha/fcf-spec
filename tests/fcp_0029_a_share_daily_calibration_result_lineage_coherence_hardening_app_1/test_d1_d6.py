from dataclasses import replace

import pytest

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1 import (
    calibrate_registered_a_share_daily_csv,
)
from tests.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.test_d1_d6 import (
    _csv,
    _registered,
    _write,
)


def calibration_result(tmp_path):
    raw = _csv()
    return calibrate_registered_a_share_daily_csv(
        _write(tmp_path, raw),
        _registered(raw),
        as_of_utc="2026-07-18T02:00:00Z",
    )


def test_exact_calibration_result_remains_valid(tmp_path):
    result = calibration_result(tmp_path)

    assert result.manifests[0].record_count == len(result.observations)
    assert result.result_sha256


class FakeObservation:
    pass


def test_result_rejects_structural_observation_impersonation(tmp_path):
    result = calibration_result(tmp_path)

    with pytest.raises(ValueError, match="typed observations"):
        replace(result, observations=(FakeObservation(),))


def test_result_rejects_manifest_count_disagreement(tmp_path):
    result = calibration_result(tmp_path)
    manifests = (replace(result.manifests[0], record_count=99), *result.manifests[1:])

    with pytest.raises(ValueError, match="counts disagree"):
        replace(result, manifests=manifests)


@pytest.mark.parametrize(
    "field,value",
    [
        ("content_sha256", "a" * 64),
        ("parent_sha256", "b" * 64),
    ],
)
def test_result_rejects_manifest_digest_lineage_disagreement(tmp_path, field, value):
    result = calibration_result(tmp_path)
    normalized = replace(result.manifests[1], **{field: value})

    with pytest.raises(ValueError, match="digest lineage disagrees"):
        replace(result, manifests=(result.manifests[0], normalized, result.manifests[2]))


def test_result_rejects_manifest_artifact_lineage_disagreement(tmp_path):
    result = calibration_result(tmp_path)
    normalized = replace(result.manifests[1], artifact_id="different-normalized")

    with pytest.raises(ValueError, match="artifact lineage disagrees"):
        replace(result, manifests=(result.manifests[0], normalized, result.manifests[2]))


def test_result_rejects_observation_source_lineage_disagreement(tmp_path):
    result = calibration_result(tmp_path)
    observation = replace(result.observations[0], source_artifact_sha256="c" * 64)

    with pytest.raises(ValueError, match="source lineage disagrees"):
        replace(result, observations=(observation,))


def test_result_rejects_post_as_of_observation(tmp_path):
    result = calibration_result(tmp_path)
    observation = replace(
        result.observations[0],
        revision_at_utc="2026-07-18T03:00:00Z",
    )

    with pytest.raises(ValueError, match="point-in-time boundary"):
        replace(result, observations=(observation,))


def test_result_rejects_finding_disagreement(tmp_path):
    result = calibration_result(tmp_path)

    with pytest.raises(ValueError, match="findings disagree"):
        replace(result, quality_state="BLOCKED", finding_codes=("UNREGISTERED",))
