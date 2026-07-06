"""FINAL-COMPLETION-REVIEW-D5 completion review packet."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from apps.final_completion_review_app_1.contract import APP_ID
from apps.final_completion_review_app_1.completion_model import (
    build_final_completion_review,
    validate_final_completion_review,
)
from apps.final_completion_review_app_1.source_loader import (
    build_final_completion_source_manifest,
    validate_final_completion_source_manifest,
)


STAGE_ID = "FINAL-COMPLETION-REVIEW-D5"
PACKET_VERSION = "1.0.0"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_final_completion_packet(
    packet_id: str,
    source_manifest: Optional[Dict[str, Any]] = None,
    generated_at_utc: Optional[str] = None,
) -> Dict[str, Any]:
    manifest = deepcopy(source_manifest) if source_manifest is not None else build_final_completion_source_manifest()
    manifest_validation = validate_final_completion_source_manifest(manifest)
    review = build_final_completion_review(source_manifest=manifest)
    review_validation = validate_final_completion_review(review)

    return {
        "app_id": APP_ID,
        "stage_id": STAGE_ID,
        "packet_version": PACKET_VERSION,
        "packet_id": packet_id,
        "generated_at_utc": generated_at_utc or _utc_now(),
        "source_manifest": manifest,
        "source_manifest_valid": manifest_validation["valid"],
        "source_manifest_issues": manifest_validation["issues"],
        "final_completion_review": review,
        "final_completion_review_valid": review_validation["valid"],
        "final_completion_review_issues": review_validation["issues"],
        "completion_item_count": review["completion_item_count"],
        "completion_state_counts": deepcopy(review["completion_state_counts"]),
        "operator_review_required": True,
        "operator_review_bypass_allowed": False,
        "auto_completion_approval_allowed": False,
        "workflow_execution_allowed": False,
        "trade_action_allowed": False,
        "real_execution_allowed": False,
        "tag_allowed": False,
        "release_allowed": False,
        "deploy_allowed": False,
        "archive_ready": manifest_validation["valid"] and review_validation["valid"],
    }


def validate_final_completion_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    candidate = deepcopy(packet)
    issues = []

    if candidate.get("app_id") != APP_ID:
        issues.append("app_id mismatch")

    if candidate.get("stage_id") != STAGE_ID:
        issues.append("stage_id mismatch")

    if not candidate.get("packet_id"):
        issues.append("packet_id must not be empty")

    if candidate.get("source_manifest_valid") is not True:
        issues.append("source_manifest_valid must be true")

    if candidate.get("final_completion_review_valid") is not True:
        issues.append("final_completion_review_valid must be true")

    if candidate.get("operator_review_required") is not True:
        issues.append("operator_review_required must be true")

    for false_key in [
        "operator_review_bypass_allowed",
        "auto_completion_approval_allowed",
        "workflow_execution_allowed",
        "trade_action_allowed",
        "real_execution_allowed",
        "tag_allowed",
        "release_allowed",
        "deploy_allowed",
    ]:
        if candidate.get(false_key) is not False:
            issues.append(false_key + " must be false")

    return {
        "valid": not issues,
        "issues": issues,
        "app_id": candidate.get("app_id"),
        "stage_id": candidate.get("stage_id"),
        "packet_id": candidate.get("packet_id"),
        "archive_ready": candidate.get("archive_ready"),
    }
