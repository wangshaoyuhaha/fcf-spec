from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from apps.fcp_0090_a_share_guojin_qmt_local_terminal_liveness_evidence_app_1.contracts import (
    DEFAULT_REGISTRATION,
    REGISTERED_FAMILIES,
    TerminalLivenessRegistration,
    build_evidence,
    build_snapshot,
    render_evidence_json,
)
from apps.fcp_0090_a_share_guojin_qmt_local_terminal_liveness_evidence_app_1.observer import (
    iter_local_process_image_names,
)


OBSERVED_AT = datetime(2026, 7, 23, 0, 50, tzinfo=timezone.utc)


def test_d1_registration_is_closed_and_deterministic():
    assert DEFAULT_REGISTRATION.registered_families == REGISTERED_FAMILIES
    assert DEFAULT_REGISTRATION.max_observed_processes == 4096
    assert DEFAULT_REGISTRATION.contract_sha256 == (
        "c82466c987b415d5d78db0dba161fc1653b651d8caa642860ba5dda6772c097a"
    )


def test_d1_rejects_unregistered_family_contract():
    with pytest.raises(ValueError, match="closed registry"):
        TerminalLivenessRegistration(
            artifact_id="bad-contract",
            source_kind="WINDOWS_LOCAL_PROCESS_NAME_SNAPSHOT",
            registered_families=("ARBITRARY",),
            max_observed_processes=1,
        )


def test_d2_reduces_names_to_registered_families_only():
    snapshot = build_snapshot(
        ["System", "XtMiniQmt.exe", "MINIQUOTE.EXE", "private-secret.exe"],
        OBSERVED_AT,
    )
    assert snapshot.observed_process_count == 4
    assert snapshot.family_counts["XT_MINI_QMT"] == 1
    assert snapshot.family_counts["MINIQUOTE"] == 1
    assert snapshot.readiness_state == "TERMINAL_OBSERVED"
    output = json.dumps(snapshot.payload(), sort_keys=True)
    assert "System" not in output
    assert "private-secret" not in output


def test_d2_count_limit_fails_closed():
    registration = TerminalLivenessRegistration(
        artifact_id="bounded-process-snapshot",
        source_kind="WINDOWS_LOCAL_PROCESS_NAME_SNAPSHOT",
        registered_families=REGISTERED_FAMILIES,
        max_observed_processes=2,
    )
    with pytest.raises(ValueError, match="registered limit"):
        build_snapshot(["a.exe", "b.exe", "c.exe"], OBSERVED_AT, registration)


def test_d3_snapshot_mapping_is_immutable():
    snapshot = build_snapshot(["XtItClient.exe"], OBSERVED_AT)
    with pytest.raises(TypeError):
        snapshot.family_counts["XT_IT_CLIENT"] = 0


def test_d4_missing_terminal_fails_closed():
    snapshot = build_snapshot(["miniquote.exe", "other.exe"], OBSERVED_AT)
    evidence = build_evidence(snapshot)
    assert snapshot.readiness_state == "TERMINAL_NOT_OBSERVED"
    assert "QMT_TERMINAL_NOT_OBSERVED" in evidence.blockers


def test_d4_observed_terminal_keeps_external_blockers():
    snapshot = build_snapshot(["XtMiniQmt.exe"], OBSERVED_AT)
    evidence = build_evidence(snapshot)
    assert snapshot.readiness_state == "TERMINAL_OBSERVED"
    assert evidence.blockers == (
        "MINIQMT_ENTITLEMENT_UNPROVEN",
        "READ_ONLY_MARKET_DATA_PROBE_UNPROVEN",
    )


def test_d5_all_authorities_remain_false_and_gap_open():
    evidence = build_evidence(build_snapshot([], OBSERVED_AT))
    assert evidence.gap_104_status == "RESEARCH_REQUIRED"
    assert evidence.entitlement_authority is False
    assert evidence.market_data_authority is False
    assert evidence.provider_selection_authority is False
    assert evidence.realtime_activation_authority is False
    assert evidence.data_promotion_authority is False
    assert evidence.product_authority is False
    assert evidence.execution_authority is False


def test_d6_canonical_render_is_ascii_and_stable():
    evidence = build_evidence(build_snapshot(["XtMiniQmt.exe"], OBSERVED_AT))
    rendered = render_evidence_json(evidence)
    assert rendered.encode("ascii").decode("ascii") == rendered
    assert rendered == render_evidence_json(evidence)
    assert json.loads(rendered)["evidence_hash"] == evidence.evidence_hash
    assert evidence.snapshot.snapshot_sha256 == (
        "f990651e95449acae4863fd4812ba5569734f95b736b681c2c62e4bfe134c2f8"
    )
    assert evidence.evidence_hash == (
        "73683bffb99cbb428c275ea8e07c85e0edf8e41177c9dcf949e6fca1afd2af17"
    )


def test_windows_observer_returns_names_without_persisting_metadata():
    names = tuple(iter_local_process_image_names())
    assert names
    assert all(isinstance(name, str) and name for name in names)
