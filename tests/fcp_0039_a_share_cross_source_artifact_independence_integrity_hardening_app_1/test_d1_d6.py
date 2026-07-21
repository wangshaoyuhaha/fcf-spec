from __future__ import annotations

from dataclasses import replace

import pytest

from apps.fcp_0039_a_share_cross_source_artifact_independence_integrity_hardening_app_1 import (
    CrossSourceArtifactIndependenceProof,
    build_cross_source_artifact_independence_proof,
)


QMT_ROLE = "1" * 64
INDEPENDENT_ROLE = "2" * 64
QMT_ARTIFACT = "a" * 64
SECOND_QMT_ARTIFACT = "b" * 64
INDEPENDENT_ARTIFACT = "c" * 64


def _proof() -> CrossSourceArtifactIndependenceProof:
    return build_cross_source_artifact_independence_proof(
        qmt_role_hash=QMT_ROLE,
        independent_role_hash=INDEPENDENT_ROLE,
        qmt_source_artifact_hashes=(QMT_ARTIFACT, SECOND_QMT_ARTIFACT),
        independent_source_artifact_hashes=(INDEPENDENT_ARTIFACT,),
    )


def test_disjoint_registered_artifacts_produce_typed_proof() -> None:
    proof = _proof()

    assert proof.quality_state == "DISJOINT_REGISTERED_ARTIFACT_LINEAGE"
    assert proof.qmt_source_artifact_hashes == (
        QMT_ARTIFACT,
        SECOND_QMT_ARTIFACT,
    )
    assert proof.independent_source_artifact_hashes == (INDEPENDENT_ARTIFACT,)
    assert proof.operator_review_required is True
    assert proof.source_selected is False


def test_proof_is_deterministic() -> None:
    assert _proof() == _proof()


def test_shared_source_artifact_is_rejected() -> None:
    with pytest.raises(ValueError, match="share source-artifact lineage"):
        build_cross_source_artifact_independence_proof(
            qmt_role_hash=QMT_ROLE,
            independent_role_hash=INDEPENDENT_ROLE,
            qmt_source_artifact_hashes=(QMT_ARTIFACT,),
            independent_source_artifact_hashes=(QMT_ARTIFACT,),
        )


@pytest.mark.parametrize(
    "qmt_hashes",
    (
        (),
        (SECOND_QMT_ARTIFACT, QMT_ARTIFACT),
        (QMT_ARTIFACT, QMT_ARTIFACT),
    ),
)
def test_source_artifact_sets_must_be_nonempty_ordered_and_unique(
    qmt_hashes: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError, match="ordered and unique"):
        build_cross_source_artifact_independence_proof(
            qmt_role_hash=QMT_ROLE,
            independent_role_hash=INDEPENDENT_ROLE,
            qmt_source_artifact_hashes=qmt_hashes,
            independent_source_artifact_hashes=(INDEPENDENT_ARTIFACT,),
        )


def test_equal_role_hashes_are_rejected() -> None:
    with pytest.raises(ValueError, match="role hashes must be distinct"):
        build_cross_source_artifact_independence_proof(
            qmt_role_hash=QMT_ROLE,
            independent_role_hash=QMT_ROLE,
            qmt_source_artifact_hashes=(QMT_ARTIFACT,),
            independent_source_artifact_hashes=(INDEPENDENT_ARTIFACT,),
        )


def test_proof_authority_boundary_is_immutable() -> None:
    proof = _proof()

    with pytest.raises(ValueError, match="quality state is immutable"):
        replace(proof, quality_state="CONSISTENT")
    with pytest.raises(ValueError, match="cannot bypass review"):
        replace(proof, operator_review_required=False)
    with pytest.raises(ValueError, match="cannot bypass review"):
        replace(proof, source_selected=True)
