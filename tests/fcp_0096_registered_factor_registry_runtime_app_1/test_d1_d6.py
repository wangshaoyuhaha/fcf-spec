from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from types import MappingProxyType

import pytest

from apps.fcp_0096_registered_factor_registry_runtime_app_1 import (
    RegisteredFactorArtifact,
    load_registered_factor_registry,
)


SPEC_HASH = "1" * 64
OBSERVED = "2026-07-23T12:00:00Z"


def _definition(
    factor_id: str,
    version: str,
    *,
    lifecycle: str = "RESEARCH",
    dependencies: tuple[str, ...] = (),
    retired_at: str | None = None,
    replacement: str | None = None,
) -> dict[str, object]:
    return {
        "asset_scopes": ["BTC"],
        "calculation_spec_hash": SPEC_HASH,
        "dependency_factor_refs": list(dependencies),
        "effective_at_utc": "2026-01-01T00:00:00Z",
        "factor_id": factor_id,
        "family": "TECHNICAL",
        "input_field_ids": ["close"],
        "lifecycle": lifecycle,
        "maximum_lookback": 20,
        "minimum_lookback": 1,
        "output_unit": "ratio",
        "replacement_factor_ref": replacement,
        "retired_at_utc": retired_at,
        "source_type": "DETERMINISTIC_CODE",
        "version": version,
    }


def _content(definitions: list[dict[str, object]] | None = None) -> bytes:
    payload = {
        "definitions": definitions
        or [
            _definition(
                "legacy-trend",
                "v1",
                lifecycle="RETIRED",
                retired_at="2026-06-01T00:00:00Z",
                replacement="trend-v2@v2",
            ),
            _definition(
                "trend-v2",
                "v2",
                dependencies=("legacy-trend@v1",),
            ),
            _definition(
                "trend-confirmation",
                "v1",
                dependencies=("trend-v2@v2",),
            ),
            _definition("volume-quality", "v1"),
        ],
        "registry_id": "fcf-factor-registry",
        "registry_version": "v1",
        "schema_version": "fcf-registered-factor-registry-runtime-v1",
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")


def _artifact(content: bytes) -> RegisteredFactorArtifact:
    return RegisteredFactorArtifact(
        artifact_id="registered-factor-registry-v1",
        artifact_hash=hashlib.sha256(content).hexdigest(),
        byte_length=len(content),
        rights_id="local-research-rights-v1",
        registered_at_utc="2026-07-23T11:00:00Z",
    )


def test_d1_exact_registered_artifact_is_required() -> None:
    content = _content()
    artifact = _artifact(content)
    with pytest.raises(ValueError, match="byte length"):
        load_registered_factor_registry(content, replace(artifact, byte_length=1), observed_at_utc=OBSERVED)
    with pytest.raises(ValueError, match="hash mismatch"):
        load_registered_factor_registry(
            content,
            replace(artifact, artifact_hash="2" * 64),
            observed_at_utc=OBSERVED,
        )


def test_d2_closed_ascii_schema_is_enforced() -> None:
    content = _content()
    payload = json.loads(content)
    payload["unexpected"] = True
    changed = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    with pytest.raises(ValueError, match="closed registered schema"):
        load_registered_factor_registry(changed, _artifact(changed), observed_at_utc=OBSERVED)
    non_ascii = b'{"name":"\\xff"}'
    with pytest.raises(ValueError, match="ASCII JSON"):
        load_registered_factor_registry(non_ascii, _artifact(non_ascii), observed_at_utc=OBSERVED)


def test_d3_dependency_graph_is_deterministic_and_immutable() -> None:
    content = _content()
    snapshot = load_registered_factor_registry(content, _artifact(content), observed_at_utc=OBSERVED)
    assert snapshot.topological_order == (
        "legacy-trend@v1",
        "volume-quality@v1",
        "trend-v2@v2",
        "trend-confirmation@v1",
    )
    assert snapshot.reverse_dependency_graph["legacy-trend@v1"] == ("trend-v2@v2",)
    assert isinstance(snapshot.record_hashes, MappingProxyType)
    with pytest.raises(TypeError):
        snapshot.record_hashes["x"] = "y"  # type: ignore[index]


def test_d4_retirement_invalidation_propagates_transitively() -> None:
    content = _content()
    snapshot = load_registered_factor_registry(content, _artifact(content), observed_at_utc=OBSERVED)
    assert snapshot.retired_factor_refs == ("legacy-trend@v1",)
    assert snapshot.invalidated_factor_refs == (
        "legacy-trend@v1",
        "trend-confirmation@v1",
        "trend-v2@v2",
    )
    assert dict(snapshot.replacement_map) == {"legacy-trend@v1": "trend-v2@v2"}
    assert "volume-quality@v1" not in snapshot.invalidated_factor_refs


def test_d5_cycles_missing_dependencies_and_replacements_fail_closed() -> None:
    cyclic = [
        _definition("a", "v1", dependencies=("b@v1",)),
        _definition("b", "v1", dependencies=("a@v1",)),
    ]
    content = _content(cyclic)
    with pytest.raises(ValueError, match="foundation rejected|cycle"):
        load_registered_factor_registry(content, _artifact(content), observed_at_utc=OBSERVED)
    missing = _content([_definition("a", "v1", dependencies=("missing@v1",))])
    with pytest.raises(ValueError, match="same artifact"):
        load_registered_factor_registry(missing, _artifact(missing), observed_at_utc=OBSERVED)
    replacement = _content(
        [
            _definition(
                "a",
                "v1",
                lifecycle="RETIRED",
                retired_at="2026-06-01T00:00:00Z",
                replacement="missing@v2",
            )
        ]
    )
    with pytest.raises(ValueError, match="replacement factor"):
        load_registered_factor_registry(
            replacement, _artifact(replacement), observed_at_utc=OBSERVED
        )


def test_d6_snapshot_is_reproducible_and_non_authorizing() -> None:
    content = _content()
    first = load_registered_factor_registry(content, _artifact(content), observed_at_utc=OBSERVED)
    second = load_registered_factor_registry(content, _artifact(content), observed_at_utc=OBSERVED)
    assert first == second
    assert first.snapshot_hash == second.snapshot_hash
    assert first.operator_review_required
    assert first.read_only
    assert not any(
        (
            first.calculation_activation_allowed,
            first.scoring_allowed,
            first.promotion_allowed,
            first.account_authority,
            first.execution_authority,
        )
    )
