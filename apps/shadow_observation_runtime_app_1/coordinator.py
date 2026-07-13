from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Tuple

from .domain import (
    SHADOW_OBSERVATION_RUNTIME_BOUNDARY,
    ShadowObservationRequest,
)
from .input_loader import (
    LoadedObservationDataset,
    load_registered_observation_dataset,
)
from .observation_engine import (
    ShadowObservationPacket,
    evaluate_shadow_observation,
)
from .packet_builder import (
    ContradictionRecord,
    OperatorReviewPacket,
    RiskFlag,
    ShadowObservationResultPacket,
    build_operator_review_packet,
    build_shadow_observation_result_packet,
)


_ALLOWED_FINAL_STATES = {
    "BLOCKED_REVIEW_REQUIRED",
    "DEGRADED_REVIEW_REQUIRED",
    "REVIEW_PACKET_READY",
}
_SAFE_RUN_ID = re.compile(r"^[A-Za-z0-9._-]+$")


@dataclass(frozen=True)
class LifecycleEvent:
    sequence: int
    from_state: str
    to_state: str
    reason: str

    def __post_init__(self) -> None:
        if self.sequence < 1:
            raise ValueError(
                "lifecycle event sequence must be positive"
            )
        if not self.from_state.strip():
            raise ValueError("from_state is required")
        if not self.to_state.strip():
            raise ValueError("to_state is required")
        if not self.reason.strip():
            raise ValueError("reason is required")

    def as_dict(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class LifecycleTrace:
    run_id: str
    correlation_id: str
    state: str
    events: Tuple[LifecycleEvent, ...]
    fail_closed: bool = True
    operator_review_required: bool = True
    automatic_transition_to_approval_allowed: bool = False
    automatic_transition_to_promotion_allowed: bool = False
    automatic_transition_to_archive_allowed: bool = False

    def __post_init__(self) -> None:
        if self.state not in _ALLOWED_FINAL_STATES:
            raise ValueError("invalid final lifecycle state")
        if not self.events:
            raise ValueError(
                "lifecycle trace must contain events"
            )
        if not self.fail_closed:
            raise ValueError(
                "lifecycle must remain fail-closed"
            )
        if not self.operator_review_required:
            raise ValueError(
                "operator review must remain required"
            )

        prohibited = (
            self.automatic_transition_to_approval_allowed,
            self.automatic_transition_to_promotion_allowed,
            self.automatic_transition_to_archive_allowed,
        )
        if any(prohibited):
            raise ValueError(
                "automatic governance transition is prohibited"
            )

        expected = tuple(
            range(1, len(self.events) + 1)
        )
        actual = tuple(
            event.sequence
            for event in self.events
        )
        if actual != expected:
            raise ValueError(
                "lifecycle event sequence is invalid"
            )
        if self.events[-1].to_state != self.state:
            raise ValueError(
                "final lifecycle event does not match state"
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "state": self.state,
            "events": [
                event.as_dict()
                for event in self.events
            ],
            "fail_closed": self.fail_closed,
            "operator_review_required": (
                self.operator_review_required
            ),
            "automatic_transition_to_approval_allowed": (
                self.automatic_transition_to_approval_allowed
            ),
            "automatic_transition_to_promotion_allowed": (
                self.automatic_transition_to_promotion_allowed
            ),
            "automatic_transition_to_archive_allowed": (
                self.automatic_transition_to_archive_allowed
            ),
        }


@dataclass(frozen=True)
class ShadowRuntimeOutcome:
    request: ShadowObservationRequest
    dataset: LoadedObservationDataset
    observation: ShadowObservationPacket
    result_packet: ShadowObservationResultPacket
    operator_review_packet: OperatorReviewPacket
    lifecycle: LifecycleTrace
    operator_triggered: bool = True
    local_only: bool = True
    paper_only: bool = True
    passive_observation_only: bool = True
    network_access_used: bool = False
    external_data_fetch_used: bool = False
    broker_or_exchange_access_used: bool = False
    credential_access_used: bool = False
    account_or_wallet_access_used: bool = False
    order_path_used: bool = False
    real_execution_used: bool = False
    automatic_approval_used: bool = False
    automatic_promotion_used: bool = False
    automatic_baseline_replacement_used: bool = False
    automatic_learning_activation_used: bool = False
    automatic_archive_used: bool = False

    def __post_init__(self) -> None:
        if not self.operator_triggered:
            raise ValueError(
                "runtime must be Operator-triggered"
            )
        if not (
            self.local_only
            and self.paper_only
            and self.passive_observation_only
        ):
            raise ValueError(
                "runtime must remain local, paper-only, and passive"
            )

        prohibited = (
            self.network_access_used,
            self.external_data_fetch_used,
            self.broker_or_exchange_access_used,
            self.credential_access_used,
            self.account_or_wallet_access_used,
            self.order_path_used,
            self.real_execution_used,
            self.automatic_approval_used,
            self.automatic_promotion_used,
            self.automatic_baseline_replacement_used,
            self.automatic_learning_activation_used,
            self.automatic_archive_used,
        )
        if any(prohibited):
            raise ValueError(
                "prohibited runtime behavior was enabled"
            )

        if self.request != self.dataset.request:
            raise ValueError("runtime dataset request mismatch")
        if self.request.run_id != self.result_packet.run_id:
            raise ValueError("runtime result run_id mismatch")
        if (
            self.request.correlation_id
            != self.result_packet.correlation_id
        ):
            raise ValueError(
                "runtime result correlation_id mismatch"
            )
        if (
            self.operator_review_packet.result_packet
            != self.result_packet
        ):
            raise ValueError(
                "operator review result mismatch"
            )
        if self.lifecycle.run_id != self.request.run_id:
            raise ValueError("lifecycle run_id mismatch")
        if (
            self.lifecycle.correlation_id
            != self.request.correlation_id
        ):
            raise ValueError(
                "lifecycle correlation_id mismatch"
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.request.run_id,
            "correlation_id": (
                self.request.correlation_id
            ),
            "artifact_id": (
                self.request.artifact.artifact_id
            ),
            "artifact_version": (
                self.request.artifact.artifact_version
            ),
            "operator_trigger_id": (
                self.request.operator_trigger_id
            ),
            "source_path": self.dataset.source_path,
            "source_sha256": self.dataset.source_sha256,
            "observation": self.result_packet.observation,
            "result_packet": (
                self.result_packet.as_dict()
            ),
            "operator_review_packet": (
                self.operator_review_packet.as_dict()
            ),
            "lifecycle": self.lifecycle.as_dict(),
            "operator_triggered": self.operator_triggered,
            "local_only": self.local_only,
            "paper_only": self.paper_only,
            "passive_observation_only": (
                self.passive_observation_only
            ),
            "network_access_used": (
                self.network_access_used
            ),
            "external_data_fetch_used": (
                self.external_data_fetch_used
            ),
            "broker_or_exchange_access_used": (
                self.broker_or_exchange_access_used
            ),
            "credential_access_used": (
                self.credential_access_used
            ),
            "account_or_wallet_access_used": (
                self.account_or_wallet_access_used
            ),
            "order_path_used": self.order_path_used,
            "real_execution_used": (
                self.real_execution_used
            ),
            "automatic_approval_used": (
                self.automatic_approval_used
            ),
            "automatic_promotion_used": (
                self.automatic_promotion_used
            ),
            "automatic_baseline_replacement_used": (
                self.automatic_baseline_replacement_used
            ),
            "automatic_learning_activation_used": (
                self.automatic_learning_activation_used
            ),
            "automatic_archive_used": (
                self.automatic_archive_used
            ),
        }


@dataclass(frozen=True)
class WrittenShadowBundle:
    run_id: str
    correlation_id: str
    output_directory: str
    observation_result_file: str
    operator_review_file: str
    lifecycle_file: str
    manifest_file: str
    observation_result_sha256: str
    operator_review_sha256: str
    lifecycle_sha256: str
    reused_existing_bundle: bool
    operator_review_required: bool = True
    paper_only: bool = True
    passive_observation_only: bool = True
    archive_status: str = "NOT_ARCHIVED"

    def __post_init__(self) -> None:
        if not (
            self.operator_review_required
            and self.paper_only
            and self.passive_observation_only
        ):
            raise ValueError(
                "bundle must remain passive and review-gated"
            )
        if self.archive_status != "NOT_ARCHIVED":
            raise ValueError(
                "runtime output must not be automatically archived"
            )

    def as_dict(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "correlation_id": self.correlation_id,
            "output_directory": self.output_directory,
            "observation_result_file": (
                self.observation_result_file
            ),
            "operator_review_file": (
                self.operator_review_file
            ),
            "lifecycle_file": self.lifecycle_file,
            "manifest_file": self.manifest_file,
            "observation_result_sha256": (
                self.observation_result_sha256
            ),
            "operator_review_sha256": (
                self.operator_review_sha256
            ),
            "lifecycle_sha256": (
                self.lifecycle_sha256
            ),
            "reused_existing_bundle": (
                self.reused_existing_bundle
            ),
            "operator_review_required": (
                self.operator_review_required
            ),
            "paper_only": self.paper_only,
            "passive_observation_only": (
                self.passive_observation_only
            ),
            "archive_status": self.archive_status,
        }


def _event(
    events: list[LifecycleEvent],
    from_state: str,
    to_state: str,
    reason: str,
) -> None:
    events.append(
        LifecycleEvent(
            sequence=len(events) + 1,
            from_state=from_state,
            to_state=to_state,
            reason=reason,
        )
    )


def run_shadow_observation(
    *,
    request: ShadowObservationRequest,
    allowed_root: Path,
    risk_flags: Iterable[RiskFlag] = (),
    contradictions: Iterable[ContradictionRecord] = (),
) -> ShadowRuntimeOutcome:
    if (
        SHADOW_OBSERVATION_RUNTIME_BOUNDARY.mode
        != "shadow_observation"
    ):
        raise RuntimeError(
            "shadow observation runtime boundary is unavailable"
        )
    if not request.operator_trigger_id.strip():
        raise ValueError("operator_trigger_id is required")

    events: list[LifecycleEvent] = []
    _event(
        events,
        "CREATED",
        "INPUT_LOADING",
        "Operator-triggered passive observation started",
    )

    dataset = load_registered_observation_dataset(
        request=request,
        allowed_root=allowed_root,
    )
    _event(
        events,
        "INPUT_LOADING",
        "INPUT_VALIDATED",
        (
            "Registered artifact identity, hash, correlation, "
            "and observation window validated"
        ),
    )

    observation = evaluate_shadow_observation(dataset)
    _event(
        events,
        "INPUT_VALIDATED",
        "OBSERVATION_EVALUATED",
        (
            "Deterministic baseline and candidate observation "
            "comparison completed"
        ),
    )

    result_packet = (
        build_shadow_observation_result_packet(
            request=request,
            dataset=dataset,
            observation=observation,
            risk_flags=risk_flags,
            contradictions=contradictions,
        )
    )
    _event(
        events,
        "OBSERVATION_EVALUATED",
        "RESULT_PACKET_BUILT",
        (
            "Risk and contradiction evidence preserved "
            "without authority escalation"
        ),
    )

    operator_review_packet = (
        build_operator_review_packet(result_packet)
    )

    final_state = {
        "BLOCKED": "BLOCKED_REVIEW_REQUIRED",
        "DEGRADED": "DEGRADED_REVIEW_REQUIRED",
        "READY_FOR_OPERATOR_REVIEW": (
            "REVIEW_PACKET_READY"
        ),
    }[result_packet.status]

    _event(
        events,
        "RESULT_PACKET_BUILT",
        final_state,
        (
            "Operator review packet created without "
            "automatic approval, promotion, or archive"
        ),
    )

    lifecycle = LifecycleTrace(
        run_id=request.run_id,
        correlation_id=request.correlation_id,
        state=final_state,
        events=tuple(events),
    )

    return ShadowRuntimeOutcome(
        request=request,
        dataset=dataset,
        observation=observation,
        result_packet=result_packet,
        operator_review_packet=operator_review_packet,
        lifecycle=lifecycle,
    )


def _json_bytes(
    payload: dict[str, object],
) -> bytes:
    return (
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            ensure_ascii=True,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _write_new_file(
    path: Path,
    payload: bytes,
) -> None:
    with path.open("xb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())


def _verify_existing_file(
    path: Path,
    expected: bytes,
) -> None:
    if not path.is_file():
        raise ValueError(
            f"existing shadow bundle is incomplete: {path.name}"
        )
    if path.read_bytes() != expected:
        raise ValueError(
            f"existing shadow bundle content mismatch: {path.name}"
        )


def write_shadow_runtime_bundle(
    *,
    outcome: ShadowRuntimeOutcome,
    output_root: Path,
) -> WrittenShadowBundle:
    run_id = outcome.request.run_id
    if not _SAFE_RUN_ID.fullmatch(run_id):
        raise ValueError(
            "run_id is unsafe for local output"
        )

    if output_root.exists() and output_root.is_symlink():
        raise ValueError(
            "symbolic output roots are not allowed"
        )

    root = output_root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    run_directory = root / run_id
    if run_directory.exists() and run_directory.is_symlink():
        raise ValueError(
            "symbolic run directories are not allowed"
        )

    result_payload = _json_bytes(
        outcome.result_packet.as_dict()
    )
    review_payload = _json_bytes(
        outcome.operator_review_packet.as_dict()
    )
    lifecycle_payload = _json_bytes(
        outcome.lifecycle.as_dict()
    )

    result_sha256 = _sha256_bytes(result_payload)
    review_sha256 = _sha256_bytes(review_payload)
    lifecycle_sha256 = _sha256_bytes(
        lifecycle_payload
    )

    manifest_payload = _json_bytes(
        {
            "schema_version": (
                "shadow_observation_bundle_manifest_v1"
            ),
            "run_id": run_id,
            "correlation_id": (
                outcome.request.correlation_id
            ),
            "artifact_id": (
                outcome.request.artifact.artifact_id
            ),
            "artifact_version": (
                outcome.request.artifact.artifact_version
            ),
            "source_sha256": (
                outcome.dataset.source_sha256
            ),
            "observation_result_sha256": (
                result_sha256
            ),
            "operator_review_sha256": review_sha256,
            "lifecycle_sha256": lifecycle_sha256,
            "status": outcome.result_packet.status,
            "operator_review_required": True,
            "paper_only": True,
            "local_only": True,
            "passive_observation_only": True,
            "archive_status": "NOT_ARCHIVED",
            "automatic_approval_allowed": False,
            "automatic_promotion_allowed": False,
            "automatic_baseline_replacement_allowed": False,
            "automatic_learning_activation_allowed": False,
            "real_execution_allowed": False,
        }
    )

    expected_files = {
        "observation_result.json": result_payload,
        "operator_review.json": review_payload,
        "lifecycle.json": lifecycle_payload,
        "manifest.json": manifest_payload,
    }

    reused = False

    if run_directory.exists():
        if not run_directory.is_dir():
            raise ValueError(
                "existing shadow output path is not a directory"
            )

        actual_names = {
            path.name
            for path in run_directory.iterdir()
        }
        expected_names = set(expected_files)

        if actual_names != expected_names:
            raise ValueError(
                "existing shadow bundle file set mismatch"
            )

        for filename, payload in expected_files.items():
            _verify_existing_file(
                run_directory / filename,
                payload,
            )

        reused = True
    else:
        staging = root / (
            f".{run_id}.{os.getpid()}.tmp"
        )

        if staging.exists():
            if staging.is_symlink():
                raise ValueError(
                    "symbolic staging paths are not allowed"
                )
            shutil.rmtree(staging)

        staging.mkdir()

        try:
            for filename, payload in expected_files.items():
                _write_new_file(
                    staging / filename,
                    payload,
                )

            os.replace(staging, run_directory)
        finally:
            if staging.exists():
                shutil.rmtree(staging)

    return WrittenShadowBundle(
        run_id=run_id,
        correlation_id=outcome.request.correlation_id,
        output_directory=str(run_directory),
        observation_result_file=str(
            run_directory / "observation_result.json"
        ),
        operator_review_file=str(
            run_directory / "operator_review.json"
        ),
        lifecycle_file=str(
            run_directory / "lifecycle.json"
        ),
        manifest_file=str(
            run_directory / "manifest.json"
        ),
        observation_result_sha256=result_sha256,
        operator_review_sha256=review_sha256,
        lifecycle_sha256=lifecycle_sha256,
        reused_existing_bundle=reused,
    )
