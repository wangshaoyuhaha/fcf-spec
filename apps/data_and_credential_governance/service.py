from __future__ import annotations

from dataclasses import dataclass

from apps.read_only_data_gateway_app_1 import RegisteredArtifactRegistry, RegisteredArtifactSource

from .contracts import GovernanceAuditRecord, GovernanceRequest
from .credential_reference import CredentialReferenceRegistry, evaluate_credential_reference
from .freshness import FreshnessBand, FreshnessPolicyRegistry, evaluate_data_freshness
from .licensing import LicensePolicyRegistry, evaluate_source_license


@dataclass(frozen=True)
class GovernanceEvaluationOutcome:
    request: GovernanceRequest
    source: RegisteredArtifactSource
    audit_record: GovernanceAuditRecord
    freshness_band: FreshnessBand
    license_registry_sha256: str
    freshness_registry_sha256: str
    credential_reference_registry_sha256: str
    operator_review_required: bool = True
    automatic_activation_allowed: bool = False

    def __post_init__(self) -> None:
        if self.request.source_id != self.source.source_id:
            raise ValueError("governance outcome source linkage mismatch")
        if self.audit_record.request != self.request:
            raise ValueError("governance outcome request linkage mismatch")
        if self.operator_review_required is not True:
            raise ValueError("operator_review_required must be true")
        if self.automatic_activation_allowed is not False:
            raise ValueError("automatic_activation_allowed must be false")


class UnifiedGovernanceService:
    def __init__(
        self,
        source_registry: RegisteredArtifactRegistry,
        license_registry: LicensePolicyRegistry,
        freshness_registry: FreshnessPolicyRegistry,
        credential_reference_registry: CredentialReferenceRegistry,
    ) -> None:
        if not isinstance(source_registry, RegisteredArtifactRegistry):
            raise TypeError("source_registry must be a RegisteredArtifactRegistry")
        if not isinstance(license_registry, LicensePolicyRegistry):
            raise TypeError("license_registry must be a LicensePolicyRegistry")
        if not isinstance(freshness_registry, FreshnessPolicyRegistry):
            raise TypeError("freshness_registry must be a FreshnessPolicyRegistry")
        if not isinstance(credential_reference_registry, CredentialReferenceRegistry):
            raise TypeError("credential_reference_registry must be a CredentialReferenceRegistry")
        self._source_registry = source_registry
        self._license_registry = license_registry
        self._freshness_registry = freshness_registry
        self._credential_reference_registry = credential_reference_registry

    def evaluate(
        self,
        request: GovernanceRequest,
        *,
        credential_reference_required: bool,
    ) -> GovernanceEvaluationOutcome:
        if not isinstance(request, GovernanceRequest):
            raise TypeError("request must be a GovernanceRequest")
        source = self._source_registry.require(request.source_id)
        license_decision = evaluate_source_license(request, self._license_registry)
        freshness_band, freshness_decision = evaluate_data_freshness(
            request, source.published_at_utc, self._freshness_registry
        )
        credential_decision = evaluate_credential_reference(
            request,
            self._credential_reference_registry,
            credential_reference_required=credential_reference_required,
        )
        audit = GovernanceAuditRecord(
            request,
            (license_decision, freshness_decision, credential_decision),
        )
        return GovernanceEvaluationOutcome(
            request=request,
            source=source,
            audit_record=audit,
            freshness_band=freshness_band,
            license_registry_sha256=self._license_registry.registry_sha256,
            freshness_registry_sha256=self._freshness_registry.registry_sha256,
            credential_reference_registry_sha256=self._credential_reference_registry.registry_sha256,
        )
