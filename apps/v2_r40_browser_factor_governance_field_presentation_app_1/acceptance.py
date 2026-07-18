from dataclasses import dataclass

from .contracts import BrowserFactorGovernanceFieldPresentation


@dataclass(frozen=True)
class V2R40FieldPresentationAcceptance:
    status: str
    field_count: int
    origins_explicit: bool
    read_only: bool = True
    operator_review_required: bool = True
    factor_activated: bool = False
    action_created: bool = False


def build_field_presentation_acceptance(
    presentation: BrowserFactorGovernanceFieldPresentation,
) -> V2R40FieldPresentationAcceptance:
    origins_explicit = all(
        field.origin in {"OBSERVED", "INFERRED"}
        for field in presentation.fields
    )
    return V2R40FieldPresentationAcceptance(
        status=(
            "PASSED_READ_ONLY_FIELD_PRESENTATION"
            if origins_explicit
            else "FAILED_FIELD_ORIGIN_PRESENTATION"
        ),
        field_count=len(presentation.fields),
        origins_explicit=origins_explicit,
    )
