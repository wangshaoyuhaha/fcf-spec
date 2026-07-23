from __future__ import annotations

from dataclasses import dataclass, field
import json
import re

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
)
from apps.fcp_0035_guojin_qmt_registered_local_daily_export_profile_app_1 import (
    QmtFrontAdjustmentReference,
)
from apps.fcp_0084_a_share_guojin_qmt_local_export_batch_coverage_evidence_app_1 import (
    QmtLocalExportCoverageEvidence,
)
from apps.v2_r3_local_event_ingress_foundation_app_1.contracts import utc


STATUS = "BLOCKED_PENDING_ENTITLEMENT_EXPECTED_DATES_AND_SUPPLEMENTS"
OUTCOME = "LOCAL_COMPATIBILITY_OBSERVED_NON_AUTHORIZING"
SCHEMA_VERSION = "a-share-guojin-qmt-dual-export-offline-sdk-compatibility-v1"
NATIVE_MODULE_NAME = "xtpythonclient.cp311-win_amd64.pyd"
_PYTHON_311 = re.compile(r"^3\.11\.[0-9]+$")


def _positive(value: int, field_name: str) -> int:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{field_name} must be a positive integer")
    return value


@dataclass(frozen=True)
class OfflineSdkAbiObservation:
    observation_id: str
    observed_at_utc: str
    python_version: str
    architecture_bits: int
    native_module_name: str
    native_module_sha256: str
    native_module_byte_length: int
    native_loaded: bool
    rpc_client_present: bool
    connection_attempted: bool = False
    network_used: bool = False
    credentials_used: bool = False
    account_data_read: bool = False
    market_data_function_called: bool = False
    observation_hash: str = field(init=False)

    def __post_init__(self) -> None:
        observation_id = identifier(self.observation_id, "observation_id")
        observed_at = utc(self.observed_at_utc, "observed_at_utc")
        version = str(self.python_version).strip()
        if _PYTHON_311.fullmatch(version) is None:
            raise ValueError("python_version must use the supported CPython 3.11 ABI")
        if self.architecture_bits != 64:
            raise ValueError("architecture_bits must be 64")
        if self.native_module_name != NATIVE_MODULE_NAME:
            raise ValueError("native_module_name must use the registered CPython 3.11 module")
        module_hash = digest(self.native_module_sha256, "native_module_sha256")
        module_length = _positive(
            self.native_module_byte_length, "native_module_byte_length"
        )
        if self.native_loaded is not True or self.rpc_client_present is not True:
            raise ValueError("offline SDK ABI capability was not observed")
        prohibited = (
            self.connection_attempted,
            self.network_used,
            self.credentials_used,
            self.account_data_read,
            self.market_data_function_called,
        )
        if any(prohibited):
            raise ValueError("offline SDK observation cannot connect, call data, or use authority")
        object.__setattr__(self, "observation_id", observation_id)
        object.__setattr__(self, "observed_at_utc", observed_at)
        object.__setattr__(self, "python_version", version)
        object.__setattr__(self, "native_module_sha256", module_hash)
        object.__setattr__(
            self,
            "observation_hash",
            canonical_sha256(
                {
                    "account_data_read": False,
                    "architecture_bits": 64,
                    "connection_attempted": False,
                    "credentials_used": False,
                    "market_data_function_called": False,
                    "native_loaded": True,
                    "native_module_byte_length": module_length,
                    "native_module_name": self.native_module_name,
                    "native_module_sha256": module_hash,
                    "network_used": False,
                    "observation_id": observation_id,
                    "observed_at_utc": observed_at,
                    "python_version": version,
                    "rpc_client_present": True,
                }
            ),
        )


@dataclass(frozen=True)
class QmtDualExportOfflineCompatibilityEvidence:
    evidence_id: str
    observed_at_utc: str
    coverage_evidence: QmtLocalExportCoverageEvidence
    adjustment_reference: QmtFrontAdjustmentReference
    sdk_observation: OfflineSdkAbiObservation
    status: str = STATUS
    outcome: str = OUTCOME
    raw_rows_embedded: bool = False
    normalized_rows_embedded: bool = False
    market_values_embedded: bool = False
    local_paths_embedded: bool = False
    entitlement_proven: bool = False
    rights_proven: bool = False
    retention_proven: bool = False
    expected_dates_registered: bool = False
    pagination_proven: bool = False
    adjustment_factor_authority: bool = False
    trading_status_proven: bool = False
    point_in_time_supplements_proven: bool = False
    provider_selected: bool = False
    realtime_activation_allowed: bool = False
    registered_evidence_promotion_allowed: bool = False
    factor_calculation_allowed: bool = False
    product_authority_allowed: bool = False
    account_access_allowed: bool = False
    order_allowed: bool = False
    execution_allowed: bool = False
    gap_closed: bool = False
    operator_review_required: bool = True
    schema_version: str = SCHEMA_VERSION
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        evidence_id = identifier(self.evidence_id, "evidence_id")
        observed_at = utc(self.observed_at_utc, "observed_at_utc")
        coverage = self.coverage_evidence
        adjustment = self.adjustment_reference
        sdk = self.sdk_observation
        if type(coverage) is not QmtLocalExportCoverageEvidence:
            raise ValueError("coverage_evidence must be exact FCP-0084 evidence")
        if type(adjustment) is not QmtFrontAdjustmentReference:
            raise ValueError("adjustment_reference must be exact FCP-0035 evidence")
        if type(sdk) is not OfflineSdkAbiObservation:
            raise ValueError("sdk_observation must be exact offline ABI evidence")
        if len(coverage.observations) != 1:
            raise ValueError("dual-export compatibility requires one exact raw batch")
        raw_observation = coverage.observations[0]
        if (
            adjustment.raw_artifact_sha256
            != raw_observation.source_artifact_sha256
            or adjustment.profile_hash != coverage.profile_hash
            or adjustment.row_count != raw_observation.row_count
        ):
            raise ValueError("dual-export lineage does not match exact coverage evidence")
        mandatory_findings = {
            "EXPECTED_DATE_ARTIFACT_MISSING",
            "FCP36_RECONCILIATION_NOT_RUN",
            "PAGINATION_NOT_PROVEN",
        }
        if not mandatory_findings.issubset(coverage.finding_codes):
            raise ValueError("coverage evidence omitted mandatory blockers")
        fixed_false = (
            self.raw_rows_embedded,
            self.normalized_rows_embedded,
            self.market_values_embedded,
            self.local_paths_embedded,
            self.entitlement_proven,
            self.rights_proven,
            self.retention_proven,
            self.expected_dates_registered,
            self.pagination_proven,
            self.adjustment_factor_authority,
            self.trading_status_proven,
            self.point_in_time_supplements_proven,
            self.provider_selected,
            self.realtime_activation_allowed,
            self.registered_evidence_promotion_allowed,
            self.factor_calculation_allowed,
            self.product_authority_allowed,
            self.account_access_allowed,
            self.order_allowed,
            self.execution_allowed,
            self.gap_closed,
        )
        if (
            self.status != STATUS
            or self.outcome != OUTCOME
            or self.schema_version != SCHEMA_VERSION
            or self.operator_review_required is not True
            or any(fixed_false)
        ):
            raise ValueError("compatibility evidence cannot become authoritative")
        object.__setattr__(self, "evidence_id", evidence_id)
        object.__setattr__(self, "observed_at_utc", observed_at)
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(
                {
                    "adjustment_reference_hash": adjustment.reference_hash,
                    "coverage_evidence_hash": coverage.evidence_hash,
                    "evidence_id": evidence_id,
                    "observed_at_utc": observed_at,
                    "outcome": self.outcome,
                    "schema_version": self.schema_version,
                    "sdk_observation_hash": sdk.observation_hash,
                    "status": self.status,
                }
            ),
        )

    def to_record(self) -> dict[str, object]:
        raw_observation = self.coverage_evidence.observations[0]
        return {
            "authority": {
                "account_access_allowed": False,
                "adjustment_factor_authority": False,
                "entitlement_proven": False,
                "execution_allowed": False,
                "factor_calculation_allowed": False,
                "gap_closed": False,
                "operator_review_required": True,
                "order_allowed": False,
                "product_authority_allowed": False,
                "provider_selected": False,
                "realtime_activation_allowed": False,
                "registered_evidence_promotion_allowed": False,
                "rights_proven": False,
                "retention_proven": False,
            },
            "coverage": {
                "actual_end_date": raw_observation.actual_end_date,
                "actual_start_date": raw_observation.actual_start_date,
                "finding_codes": list(self.coverage_evidence.finding_codes),
                "front_adjustment_boundary_count": len(
                    self.adjustment_reference.boundary_dates
                ),
                "row_count": raw_observation.row_count,
            },
            "evidence_hash": self.evidence_hash,
            "evidence_id": self.evidence_id,
            "lineage": {
                "adjustment_reference_hash": self.adjustment_reference.reference_hash,
                "coverage_evidence_hash": self.coverage_evidence.evidence_hash,
                "front_artifact_sha256": self.adjustment_reference.front_artifact_sha256,
                "profile_hash": self.coverage_evidence.profile_hash,
                "raw_artifact_sha256": self.adjustment_reference.raw_artifact_sha256,
                "sdk_observation_hash": self.sdk_observation.observation_hash,
            },
            "observed_at_utc": self.observed_at_utc,
            "outcome": self.outcome,
            "schema_version": self.schema_version,
            "sdk": {
                "architecture_bits": self.sdk_observation.architecture_bits,
                "connection_attempted": False,
                "native_loaded": True,
                "native_module_byte_length": (
                    self.sdk_observation.native_module_byte_length
                ),
                "native_module_name": self.sdk_observation.native_module_name,
                "native_module_sha256": self.sdk_observation.native_module_sha256,
                "network_used": False,
                "python_version": self.sdk_observation.python_version,
                "rpc_client_present": True,
            },
            "status": self.status,
        }


def render_compatibility_evidence_json(
    evidence: QmtDualExportOfflineCompatibilityEvidence,
) -> str:
    if type(evidence) is not QmtDualExportOfflineCompatibilityEvidence:
        raise TypeError("evidence must be exact compatibility evidence")
    return json.dumps(
        evidence.to_record(), ensure_ascii=True, separators=(",", ":"), sort_keys=True
    ) + "\n"
