from dataclasses import dataclass

from apps.v2_r2_historical_factor_baseline_app_1.contracts import identifier


FACTOR_FAMILIES = (
    "FLOW",
    "MACRO",
    "MICROSTRUCTURE",
    "QUALITY",
    "RISK",
    "TECHNICAL",
    "VOLUME",
)
FACTOR_LIFECYCLES = ("CHALLENGER", "DRAFT", "RESEARCH", "RETIRED")
SOURCE_TYPES = ("DETERMINISTIC_CODE", "REGISTERED_DERIVATION")
MAX_LOOKBACK = 1_000_000


def sha256_text(value: object, name: str) -> str:
    normalized = str(value).strip()
    if len(normalized) != 64 or any(
        character not in "0123456789abcdef" for character in normalized
    ):
        raise ValueError(f"{name} must be lowercase SHA-256")
    return normalized


def factor_ref(value: object, name: str) -> str:
    normalized = str(value).strip()
    if normalized.count("@") != 1:
        raise ValueError(f"{name} must use factor-id@version")
    factor_id, version = normalized.split("@")
    return f"{identifier(factor_id, name)}@{identifier(version, name)}"


@dataclass(frozen=True)
class FactorDefinition:
    factor_id: str
    version: str
    family: str
    lifecycle: str
    source_type: str
    calculation_spec_hash: str
    output_unit: str
    asset_scopes: tuple[str, ...]
    input_field_ids: tuple[str, ...]
    dependency_factor_refs: tuple[str, ...] = ()
    minimum_lookback: int = 1
    maximum_lookback: int = 1
    operator_registered: bool = True
    calculation_activation_allowed: bool = False
    scoring_allowed: bool = False

    def __post_init__(self) -> None:
        for name in ("factor_id", "version", "output_unit"):
            object.__setattr__(self, name, identifier(getattr(self, name), name))
        family = str(self.family).strip().upper()
        lifecycle = str(self.lifecycle).strip().upper()
        source_type = str(self.source_type).strip().upper()
        if family not in FACTOR_FAMILIES:
            raise ValueError("unsupported factor family")
        if lifecycle not in FACTOR_LIFECYCLES:
            raise ValueError("unsupported factor lifecycle")
        if source_type not in SOURCE_TYPES:
            raise ValueError("unsupported factor source type")
        object.__setattr__(self, "family", family)
        object.__setattr__(self, "lifecycle", lifecycle)
        object.__setattr__(self, "source_type", source_type)
        object.__setattr__(
            self,
            "calculation_spec_hash",
            sha256_text(self.calculation_spec_hash, "calculation_spec_hash"),
        )
        scopes = tuple(identifier(value, "asset_scope") for value in self.asset_scopes)
        fields = tuple(identifier(value, "input_field_id") for value in self.input_field_ids)
        dependencies = tuple(
            factor_ref(value, "dependency_factor_ref")
            for value in self.dependency_factor_refs
        )
        for values, name in ((scopes, "asset scopes"), (fields, "input fields")):
            if not values or tuple(sorted(set(values))) != values:
                raise ValueError(f"{name} must be nonempty, unique, and sorted")
        if tuple(sorted(set(dependencies))) != dependencies:
            raise ValueError("factor dependencies must be unique and sorted")
        object.__setattr__(self, "asset_scopes", scopes)
        object.__setattr__(self, "input_field_ids", fields)
        object.__setattr__(self, "dependency_factor_refs", dependencies)
        if (
            isinstance(self.minimum_lookback, bool)
            or isinstance(self.maximum_lookback, bool)
            or not 1 <= self.minimum_lookback <= self.maximum_lookback <= MAX_LOOKBACK
        ):
            raise ValueError("factor lookback bounds are invalid")
        if self.operator_registered is not True:
            raise ValueError("factor definition must be Operator-registered")
        if self.calculation_activation_allowed or self.scoring_allowed:
            raise ValueError("factor definition exceeds registry-only scope")

    @property
    def natural_key(self) -> str:
        return f"{self.factor_id}@{self.version}"


@dataclass(frozen=True)
class FactorRegistryPolicy:
    registry_id: str
    registry_version: str
    allowed_families: tuple[str, ...] = FACTOR_FAMILIES
    allowed_lifecycles: tuple[str, ...] = FACTOR_LIFECYCLES
    maximum_definitions: int = 1000
    dependencies_allowed: bool = True
    operator_registered: bool = True
    calculation_activation_allowed: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "registry_id", identifier(self.registry_id, "registry_id"))
        object.__setattr__(self, "registry_version", identifier(self.registry_version, "registry_version"))
        families = tuple(str(value).strip().upper() for value in self.allowed_families)
        lifecycles = tuple(str(value).strip().upper() for value in self.allowed_lifecycles)
        if not families or tuple(sorted(set(families))) != families or any(value not in FACTOR_FAMILIES for value in families):
            raise ValueError("allowed factor families are invalid")
        if not lifecycles or tuple(sorted(set(lifecycles))) != lifecycles or any(value not in FACTOR_LIFECYCLES for value in lifecycles):
            raise ValueError("allowed factor lifecycles are invalid")
        object.__setattr__(self, "allowed_families", families)
        object.__setattr__(self, "allowed_lifecycles", lifecycles)
        if isinstance(self.maximum_definitions, bool) or not 1 <= self.maximum_definitions <= 10000:
            raise ValueError("maximum_definitions is invalid")
        if self.operator_registered is not True:
            raise ValueError("factor registry policy must be Operator-registered")
        if self.calculation_activation_allowed:
            raise ValueError("factor registry policy cannot activate calculations")
