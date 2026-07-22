from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath

from apps.fcp_0017_a_share_trusted_daily_data_substrate_local_calibration_app_1.contracts import (
    canonical_sha256,
    digest,
    identifier,
    utc,
)


GAP_IDS = tuple(f"V2-FR-GAP-{number:03d}" for number in range(87, 94))
CAPABILITY_IDS = (
    "ADJUSTMENT_FACTOR_LINEAGE",
    "CANONICAL_TYPED_OBSERVATION",
    "CORPORATE_ACTION_LINEAGE",
    "CROSS_SOURCE_CONFLICT_QUARANTINE",
    "CROSS_SOURCE_COVERAGE",
    "CROSS_SOURCE_DUPLICATE_OUTLIER",
    "CROSS_SOURCE_UNIT_CLOCK_RECONCILIATION",
    "EXPECTED_CALENDAR_LINEAGE",
    "FIRST_TRADABLE_CLOCK",
    "INGEST_CLOCK",
    "MISSING_BAR_SUSPENSION_POLICY",
    "POINT_IN_TIME_AVAILABILITY",
    "PROVIDER_EDGE_CONVERSION",
    "PROVIDER_PROFILE_AKSHARE",
    "PROVIDER_PROFILE_BAOSTOCK",
    "PROVIDER_PROFILE_MINIQMT",
    "PROVIDER_PROFILE_RQDATA",
    "PROVIDER_PROFILE_TUSHARE",
    "PUBLICATION_CLOCK",
    "QUERY_POLICY_LINEAGE",
    "RAW_NORMALIZED_RESEARCH_LAYERS",
    "RAW_PRICE_LINEAGE",
    "REVISION_CLOCK",
    "RIGHTS_RETENTION_MANIFEST",
    "TRADING_STATUS_SCHEMA",
)
COVERAGE_STATES = (
    "NO_FOUNDATION_EVIDENCE_GAP_OPEN",
    "FOUNDATION_PARTIAL_GAP_OPEN",
    "FOUNDATION_COVERED_GAP_OPEN",
)
_ALLOWED_ROOTS = {"apps", "docs", "scripts", "tests"}


def _closed_capabilities(values: object, name: str, *, allow_empty: bool) -> tuple[str, ...]:
    if not isinstance(values, tuple) or not all(isinstance(item, str) for item in values):
        raise TypeError(f"{name} must be a tuple of capability identifiers")
    result = tuple(sorted(set(values)))
    if result != values:
        raise ValueError(f"{name} must be unique and sorted")
    if not allow_empty and not result:
        raise ValueError(f"{name} must not be empty")
    if any(item not in CAPABILITY_IDS for item in result):
        raise ValueError(f"{name} contains an unregistered capability")
    return result


def repository_path(value: object) -> str:
    if not isinstance(value, str) or not value or not value.isascii() or "\\" in value:
        raise ValueError("repository_path must be nonempty ASCII POSIX text")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError("repository_path must remain repository-relative")
    if path.parts[0] not in _ALLOWED_ROOTS or path.suffix not in {".py", ".md", ".json"}:
        raise ValueError("repository_path is outside the registered source scope")
    return path.as_posix()


@dataclass(frozen=True)
class GapCoverageRequirement:
    gap_id: str
    required_capabilities: tuple[str, ...]
    external_evidence_required: bool
    operator_review_required: bool = True

    def __post_init__(self) -> None:
        if self.gap_id not in GAP_IDS:
            raise ValueError("gap_id is outside the FCP-0077 range")
        object.__setattr__(
            self,
            "required_capabilities",
            _closed_capabilities(
                self.required_capabilities,
                "required_capabilities",
                allow_empty=False,
            ),
        )
        if type(self.external_evidence_required) is not bool:
            raise TypeError("external_evidence_required must be bool")
        if self.operator_review_required is not True:
            raise ValueError("Operator review must remain required")


@dataclass(frozen=True)
class RegisteredImplementationEvidence:
    component_id: str
    gap_id: str
    repository_path: str
    artifact_sha256: str
    capabilities: tuple[str, ...]
    observed_at_utc: str
    operator_registered: bool = True
    claims_data_authority: bool = False
    closes_gap: bool = False
    evidence_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "component_id", identifier(self.component_id, "component_id"))
        if self.gap_id not in GAP_IDS:
            raise ValueError("gap_id is outside the FCP-0077 range")
        object.__setattr__(self, "repository_path", repository_path(self.repository_path))
        object.__setattr__(self, "artifact_sha256", digest(self.artifact_sha256, "artifact_sha256"))
        object.__setattr__(
            self,
            "capabilities",
            _closed_capabilities(self.capabilities, "capabilities", allow_empty=False),
        )
        object.__setattr__(self, "observed_at_utc", utc(self.observed_at_utc, "observed_at_utc"))
        if self.operator_registered is not True:
            raise ValueError("implementation evidence requires Operator registration")
        if self.claims_data_authority is not False or self.closes_gap is not False:
            raise ValueError("implementation evidence cannot establish authority or close gaps")
        object.__setattr__(
            self,
            "evidence_hash",
            canonical_sha256(
                {
                    "artifact_sha256": self.artifact_sha256,
                    "capabilities": self.capabilities,
                    "claims_data_authority": False,
                    "closes_gap": False,
                    "component_id": self.component_id,
                    "gap_id": self.gap_id,
                    "observed_at_utc": self.observed_at_utc,
                    "operator_registered": True,
                    "repository_path": self.repository_path,
                }
            ),
        )


@dataclass(frozen=True)
class GapCoverageRow:
    requirement: GapCoverageRequirement
    evidence: tuple[RegisteredImplementationEvidence, ...]
    observed_capabilities: tuple[str, ...]
    missing_capabilities: tuple[str, ...]
    coverage_state: str
    gap_open: bool = True
    authority_established: bool = False
    provider_selected: bool = False
    row_hash: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.requirement, GapCoverageRequirement):
            raise TypeError("requirement must be GapCoverageRequirement")
        evidence = tuple(self.evidence)
        if not all(isinstance(item, RegisteredImplementationEvidence) for item in evidence):
            raise TypeError("evidence must contain RegisteredImplementationEvidence")
        if tuple(sorted(evidence, key=lambda item: item.component_id)) != evidence:
            raise ValueError("evidence must use deterministic component order")
        if len({item.component_id for item in evidence}) != len(evidence):
            raise ValueError("component evidence must be unique within a gap")
        if any(item.gap_id != self.requirement.gap_id for item in evidence):
            raise ValueError("evidence gap identity disagrees with requirement")
        observed = tuple(sorted({cap for item in evidence for cap in item.capabilities}))
        missing = tuple(
            capability
            for capability in self.requirement.required_capabilities
            if capability not in observed
        )
        if self.observed_capabilities != observed or self.missing_capabilities != missing:
            raise ValueError("coverage capabilities disagree with registered evidence")
        expected_state = (
            "NO_FOUNDATION_EVIDENCE_GAP_OPEN"
            if not evidence
            else "FOUNDATION_PARTIAL_GAP_OPEN"
            if missing
            else "FOUNDATION_COVERED_GAP_OPEN"
        )
        if self.coverage_state != expected_state or self.coverage_state not in COVERAGE_STATES:
            raise ValueError("coverage_state disagrees with capability evidence")
        if self.gap_open is not True or self.authority_established is not False:
            raise ValueError("coverage rows cannot close gaps or establish authority")
        if self.provider_selected is not False:
            raise ValueError("coverage rows cannot select a provider")
        object.__setattr__(self, "evidence", evidence)
        object.__setattr__(
            self,
            "row_hash",
            canonical_sha256(
                {
                    "authority_established": False,
                    "coverage_state": self.coverage_state,
                    "evidence_hashes": tuple(item.evidence_hash for item in evidence),
                    "external_evidence_required": self.requirement.external_evidence_required,
                    "gap_id": self.requirement.gap_id,
                    "gap_open": True,
                    "missing_capabilities": missing,
                    "observed_capabilities": observed,
                    "operator_review_required": True,
                    "provider_selected": False,
                    "required_capabilities": self.requirement.required_capabilities,
                }
            ),
        )


@dataclass(frozen=True)
class TrustedDataSupplyChainCoverageMatrix:
    rows: tuple[GapCoverageRow, ...]
    evaluated_at_utc: str
    status: str = "FOUNDATION_EVIDENCE_ONLY_GAPS_REMAIN_OPEN"
    operator_review_mandatory: bool = True
    changes_gap_status: bool = False
    promotes_candidate_data: bool = False
    provider_selected: bool = False
    matrix_hash: str = field(init=False)

    def __post_init__(self) -> None:
        rows = tuple(self.rows)
        if not all(isinstance(row, GapCoverageRow) for row in rows):
            raise TypeError("rows must contain GapCoverageRow")
        if tuple(row.requirement.gap_id for row in rows) != GAP_IDS:
            raise ValueError("matrix rows must cover the exact ordered gap range")
        object.__setattr__(self, "evaluated_at_utc", utc(self.evaluated_at_utc, "evaluated_at_utc"))
        if self.status != "FOUNDATION_EVIDENCE_ONLY_GAPS_REMAIN_OPEN":
            raise ValueError("matrix status is not registered")
        if self.operator_review_mandatory is not True:
            raise ValueError("Operator review must remain mandatory")
        if self.changes_gap_status is not False or self.promotes_candidate_data is not False:
            raise ValueError("matrix cannot change gaps or promote candidate data")
        if self.provider_selected is not False:
            raise ValueError("matrix cannot select a provider")
        object.__setattr__(self, "rows", rows)
        object.__setattr__(
            self,
            "matrix_hash",
            canonical_sha256(
                {
                    "changes_gap_status": False,
                    "evaluated_at_utc": self.evaluated_at_utc,
                    "operator_review_mandatory": True,
                    "promotes_candidate_data": False,
                    "provider_selected": False,
                    "row_hashes": tuple(row.row_hash for row in rows),
                    "status": self.status,
                }
            ),
        )
