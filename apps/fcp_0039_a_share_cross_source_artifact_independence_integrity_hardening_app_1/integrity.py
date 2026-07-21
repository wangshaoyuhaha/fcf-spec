from __future__ import annotations

from dataclasses import dataclass, field

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
)


@dataclass(frozen=True)
class CrossSourceArtifactIndependenceProof:
    qmt_role_hash: str
    independent_role_hash: str
    qmt_source_artifact_hashes: tuple[str, ...]
    independent_source_artifact_hashes: tuple[str, ...]
    quality_state: str = "DISJOINT_REGISTERED_ARTIFACT_LINEAGE"
    operator_review_required: bool = True
    source_selected: bool = False
    proof_hash: str = field(init=False)

    def __post_init__(self) -> None:
        qmt_role = digest(self.qmt_role_hash, "qmt_role_hash")
        independent_role = digest(
            self.independent_role_hash, "independent_role_hash"
        )
        if qmt_role == independent_role:
            raise ValueError("cross-source role hashes must be distinct")
        object.__setattr__(self, "qmt_role_hash", qmt_role)
        object.__setattr__(self, "independent_role_hash", independent_role)
        normalized: dict[str, tuple[str, ...]] = {}
        for name in (
            "qmt_source_artifact_hashes",
            "independent_source_artifact_hashes",
        ):
            values = tuple(digest(item, name) for item in getattr(self, name))
            if not values or values != tuple(sorted(set(values))):
                raise ValueError("source-artifact hashes must be ordered and unique")
            object.__setattr__(self, name, values)
            normalized[name] = values
        if set(normalized["qmt_source_artifact_hashes"]) & set(
            normalized["independent_source_artifact_hashes"]
        ):
            raise ValueError("cross-source roles share source-artifact lineage")
        if self.quality_state != "DISJOINT_REGISTERED_ARTIFACT_LINEAGE":
            raise ValueError("artifact-independence quality state is immutable")
        if self.operator_review_required is not True or self.source_selected is not False:
            raise ValueError("artifact independence cannot bypass review or select a source")
        object.__setattr__(
            self,
            "proof_hash",
            canonical_sha256(
                {
                    "independent_role_hash": independent_role,
                    "independent_source_artifact_hashes": normalized[
                        "independent_source_artifact_hashes"
                    ],
                    "qmt_role_hash": qmt_role,
                    "qmt_source_artifact_hashes": normalized[
                        "qmt_source_artifact_hashes"
                    ],
                    "quality_state": self.quality_state,
                }
            ),
        )


def build_cross_source_artifact_independence_proof(
    *,
    qmt_role_hash: str,
    independent_role_hash: str,
    qmt_source_artifact_hashes: tuple[str, ...],
    independent_source_artifact_hashes: tuple[str, ...],
) -> CrossSourceArtifactIndependenceProof:
    return CrossSourceArtifactIndependenceProof(
        qmt_role_hash=qmt_role_hash,
        independent_role_hash=independent_role_hash,
        qmt_source_artifact_hashes=qmt_source_artifact_hashes,
        independent_source_artifact_hashes=independent_source_artifact_hashes,
    )
