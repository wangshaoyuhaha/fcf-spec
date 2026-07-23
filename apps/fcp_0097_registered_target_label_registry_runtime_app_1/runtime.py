from __future__ import annotations

import hashlib
import json

from apps.v2_r1_factor_contract_foundation_app_1 import (
    ForecastTargetDefinition,
    ForecastTargetRegistry,
    ForecastTargetType,
    TargetBasis,
)

from .contracts import (
    RUNTIME_SCHEMA_VERSION,
    RegisteredLabelDefinition,
    RegisteredTargetLabelArtifact,
    RegisteredTargetLabelRuntimeSnapshot,
    canonical_sha256,
    target_ref,
)


TOP_LEVEL_FIELDS = {
    "labels",
    "registry_id",
    "registry_version",
    "schema_version",
    "targets",
}
TARGET_FIELDS = {
    "abstention_behavior",
    "asset_class",
    "basis",
    "benchmark_policy",
    "capacity_treatment",
    "censored_behavior",
    "cost_treatment",
    "decision_time_basis",
    "effective_at_utc",
    "evaluation_metrics",
    "evidence_refs",
    "forecast_horizon",
    "formula",
    "instrument_scope",
    "invalid_behavior",
    "label_availability_rule",
    "market",
    "maturity_rule",
    "minimum_sample",
    "missing_behavior",
    "neutralization_policy",
    "objective",
    "owner",
    "slippage_treatment",
    "target_id",
    "target_type",
    "target_version",
}
LABEL_FIELDS = {
    "available_time_field",
    "censored_behavior",
    "decision_time_field",
    "effective_at_utc",
    "first_tradable_time_field",
    "invalid_behavior",
    "label_id",
    "label_version",
    "maturity_rule",
    "maturity_time_field",
    "missing_behavior",
    "observation_key_rule",
    "published_time_field",
    "revision_policy",
    "source_evidence_rule",
    "target_ref",
    "value_type",
}


def _closed_object(value: object, fields: set[str], name: str) -> dict[str, object]:
    if type(value) is not dict or set(value) != fields:
        raise ValueError(f"{name} must use the closed registered schema")
    return value


def _target_record_hash(definition: ForecastTargetDefinition) -> str:
    return canonical_sha256(
        {
            "abstention_behavior": definition.abstention_behavior,
            "asset_class": definition.asset_class,
            "basis": definition.basis.value,
            "benchmark_policy": definition.benchmark_policy,
            "capacity_treatment": definition.capacity_treatment,
            "censored_behavior": definition.censored_behavior,
            "cost_treatment": definition.cost_treatment,
            "decision_time_basis": definition.decision_time_basis,
            "effective_at_utc": definition.effective_at_utc,
            "evaluation_metrics": definition.evaluation_metrics,
            "evidence_refs": definition.evidence_refs,
            "forecast_horizon": definition.forecast_horizon,
            "formula": definition.formula,
            "instrument_scope": definition.instrument_scope,
            "invalid_behavior": definition.invalid_behavior,
            "label_availability_rule": definition.label_availability_rule,
            "market": definition.market,
            "maturity_rule": definition.maturity_rule,
            "minimum_sample": definition.minimum_sample,
            "missing_behavior": definition.missing_behavior,
            "neutralization_policy": definition.neutralization_policy,
            "objective": definition.objective,
            "owner": definition.owner,
            "slippage_treatment": definition.slippage_treatment,
            "target_id": definition.target_id,
            "target_type": definition.target_type.value,
            "target_version": definition.target_version,
        }
    )


def load_registered_target_label_registry(
    content: bytes,
    artifact: RegisteredTargetLabelArtifact,
    *,
    observed_at_utc: str,
) -> RegisteredTargetLabelRuntimeSnapshot:
    if type(content) is not bytes:
        raise TypeError("content must be exact bytes")
    if len(content) != artifact.byte_length:
        raise ValueError("registered target-label artifact byte length mismatch")
    if hashlib.sha256(content).hexdigest() != artifact.artifact_hash:
        raise ValueError("registered target-label artifact hash mismatch")
    try:
        payload = json.loads(content.decode("ascii"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("registered target-label artifact must be ASCII JSON") from exc
    payload = _closed_object(payload, TOP_LEVEL_FIELDS, "registry")
    if payload["schema_version"] != RUNTIME_SCHEMA_VERSION:
        raise ValueError("registered target-label schema version mismatch")
    raw_targets = payload["targets"]
    raw_labels = payload["labels"]
    if type(raw_targets) is not list or not raw_targets:
        raise ValueError("registry targets must be a nonempty list")
    if type(raw_labels) is not list or not raw_labels:
        raise ValueError("registry labels must be a nonempty list")

    targets: list[ForecastTargetDefinition] = []
    registry = ForecastTargetRegistry()
    for raw in raw_targets:
        item = _closed_object(raw, TARGET_FIELDS, "target definition")
        definition = ForecastTargetDefinition(
            target_id=item["target_id"],
            target_version=item["target_version"],
            asset_class=item["asset_class"],
            market=item["market"],
            instrument_scope=item["instrument_scope"],
            decision_time_basis=item["decision_time_basis"],
            forecast_horizon=item["forecast_horizon"],
            maturity_rule=item["maturity_rule"],
            target_type=ForecastTargetType(item["target_type"]),
            formula=item["formula"],
            basis=TargetBasis(item["basis"]),
            objective=item["objective"],
            cost_treatment=item["cost_treatment"],
            slippage_treatment=item["slippage_treatment"],
            capacity_treatment=item["capacity_treatment"],
            label_availability_rule=item["label_availability_rule"],
            benchmark_policy=item["benchmark_policy"],
            neutralization_policy=item["neutralization_policy"],
            missing_behavior=item["missing_behavior"],
            invalid_behavior=item["invalid_behavior"],
            censored_behavior=item["censored_behavior"],
            abstention_behavior=item["abstention_behavior"],
            evaluation_metrics=tuple(item["evaluation_metrics"]),
            minimum_sample=item["minimum_sample"],
            evidence_refs=tuple(item["evidence_refs"]),
            owner=item["owner"],
            effective_at_utc=item["effective_at_utc"],
        )
        registry = registry.register(definition)
        targets.append(definition)

    labels = tuple(
        RegisteredLabelDefinition(
            **_closed_object(raw, LABEL_FIELDS, "label definition")
        )
        for raw in raw_labels
    )
    target_keys = tuple(target_ref(definition) for definition in targets)
    label_keys = tuple(definition.natural_key for definition in labels)
    if len(set(target_keys)) != len(target_keys):
        raise ValueError("registered target references must be unique")
    if len(set(label_keys)) != len(label_keys):
        raise ValueError("registered label references must be unique")
    target_key_set = set(target_keys)
    if any(label.target_ref not in target_key_set for label in labels):
        raise ValueError("labels must reference a target in the same artifact")

    target_to_labels = {
        key: tuple(
            sorted(
                label.natural_key for label in labels if label.target_ref == key
            )
        )
        for key in sorted(target_keys)
    }
    if any(not values for values in target_to_labels.values()):
        raise ValueError("each registered target must have at least one label definition")
    ordered_targets = tuple(sorted(targets, key=target_ref))
    ordered_labels = tuple(sorted(labels, key=lambda label: label.natural_key))
    return RegisteredTargetLabelRuntimeSnapshot(
        artifact_id=artifact.artifact_id,
        artifact_hash=artifact.artifact_hash,
        registry_id=payload["registry_id"],
        registry_version=payload["registry_version"],
        target_record_hashes={
            target_ref(definition): _target_record_hash(definition)
            for definition in ordered_targets
        },
        label_record_hashes={
            definition.natural_key: definition.record_hash
            for definition in ordered_labels
        },
        target_to_label_refs=target_to_labels,
        label_to_target_ref={
            definition.natural_key: definition.target_ref
            for definition in ordered_labels
        },
        observed_at_utc=observed_at_utc,
    )
