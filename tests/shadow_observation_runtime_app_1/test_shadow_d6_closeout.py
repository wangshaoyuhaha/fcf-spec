import pytest

from apps.shadow_observation_runtime_app_1 import (
    LifecycleEvent,
    LifecycleTrace,
    ShadowRuntimeBoundary,
    WrittenShadowBundle,
)


def test_d6_runtime_boundary_rejects_network_access():
    with pytest.raises(
        ValueError,
        match="prohibited runtime capability",
    ):
        ShadowRuntimeBoundary(
            network_access_allowed=True,
        )


def test_d6_lifecycle_rejects_automatic_promotion():
    event = LifecycleEvent(
        sequence=1,
        from_state="CREATED",
        to_state="REVIEW_PACKET_READY",
        reason="Operator review required",
    )

    with pytest.raises(
        ValueError,
        match="automatic governance transition",
    ):
        LifecycleTrace(
            run_id="run-d6",
            correlation_id="corr-d6",
            state="REVIEW_PACKET_READY",
            events=(event,),
            automatic_transition_to_promotion_allowed=True,
        )


def test_d6_bundle_rejects_archive_authority():
    with pytest.raises(
        ValueError,
        match="must not be automatically archived",
    ):
        WrittenShadowBundle(
            run_id="run-d6",
            correlation_id="corr-d6",
            output_directory="output/run-d6",
            observation_result_file="observation_result.json",
            operator_review_file="operator_review.json",
            lifecycle_file="lifecycle.json",
            manifest_file="manifest.json",
            observation_result_sha256="a" * 64,
            operator_review_sha256="b" * 64,
            lifecycle_sha256="c" * 64,
            reused_existing_bundle=False,
            archive_status="ARCHIVED",
        )
