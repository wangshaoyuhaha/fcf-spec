from collections.abc import Iterable

from apps.v2_r40_browser_factor_governance_field_presentation_app_1 import (
    BrowserFactorGovernanceFieldPresentation,
)

from .contracts import (
    BrowserGovernanceReviewEvidenceTrace,
    BrowserGovernanceReviewEvidenceTraceItem,
)


def build_governance_review_evidence_trace(
    presentations: Iterable[BrowserFactorGovernanceFieldPresentation],
) -> BrowserGovernanceReviewEvidenceTrace:
    source = tuple(presentations)
    if any(not isinstance(item, BrowserFactorGovernanceFieldPresentation) for item in source):
        raise ValueError("validated governance presentations are required")
    items = tuple(
        sorted(
            (
                BrowserGovernanceReviewEvidenceTraceItem(
                    artifact_id=presentation.artifact_id,
                    projection_id=presentation.projection_id,
                    observed_field_count=sum(field.origin == "OBSERVED" for field in presentation.fields),
                    inferred_field_count=sum(field.origin == "INFERRED" for field in presentation.fields),
                    source_snapshot_hashes=tuple(
                        sorted(
                            {
                                snapshot_hash
                                for field in presentation.fields
                                for snapshot_hash in field.source_snapshot_hashes
                            }
                        )
                    ),
                )
                for presentation in source
            ),
            key=lambda item: (item.projection_id, item.artifact_id),
        )
    )
    return BrowserGovernanceReviewEvidenceTrace(
        status=("REGISTERED_EVIDENCE_TRACE_AVAILABLE" if items else "NO_REGISTERED_EVIDENCE_TRACE"),
        items=items,
    )
