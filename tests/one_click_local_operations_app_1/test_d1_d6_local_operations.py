import json
import shutil
import socket
import tempfile
import time
import zipfile
from pathlib import Path

import pytest

from apps.one_click_local_operations_app_1 import cli as local_operations_cli
from apps.one_click_local_operations_app_1 import (
    ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY,
    LocalLifecycleState,
    LocalOperationsProfile,
    LocalOperationsStateStore,
    LocalRuntimeState,
    OneClickLocalOperationsController,
    OperationalSnapshotService,
    build_one_click_local_operations_acceptance,
    run_local_operations_preflight,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STARTER_ROOT = PROJECT_ROOT / "examples" / "browser_product_console_starter"


def _reserve_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", 0))
        return int(handle.getsockname()[1])


def _unlink_generated_log_with_retry(path, timeout_seconds=3.0):
    deadline = time.monotonic() + timeout_seconds
    while True:
        try:
            path.unlink(missing_ok=True)
            return
        except PermissionError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(0.05)


@pytest.fixture
def profile(tmp_path):
    project = tmp_path / "project"
    registered = project / "registered"
    shutil.copytree(STARTER_ROOT, registered)
    return LocalOperationsProfile(
        project_root=project,
        allowed_root=registered,
        index_path=registered / "index.json",
        state_root=project / "runtime" / "operations",
        backup_root=project / "runtime" / "operations" / "backups",
        port=_reserve_port(),
        open_browser=False,
    )


def _state(profile, state=LocalLifecycleState.READY, pid=4321):
    return LocalRuntimeState(
        instance_id="a" * 32,
        pid=pid,
        lifecycle_state=state,
        port=profile.port,
        url=profile.url,
        started_at_utc="2026-07-16T00:00:00+00:00",
        updated_at_utc="2026-07-16T00:00:01+00:00",
        correlation_id="corr-one-click",
        artifact_count=14,
    )


def test_d1_boundary_is_fail_closed():
    assert ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY.paper_only is True
    assert ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY.exact_loopback_only is True
    assert ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY.graceful_stop_required is True
    assert (
        ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY.unrelated_process_termination_allowed
        is False
    )
    assert ONE_CLICK_LOCAL_OPERATIONS_BOUNDARY.financial_execution_allowed is False


def test_d1_profile_rejects_paths_outside_project(tmp_path):
    with pytest.raises(ValueError, match="inside project_root"):
        LocalOperationsProfile(
            project_root=tmp_path / "project",
            allowed_root=STARTER_ROOT,
            index_path=STARTER_ROOT / "index.json",
            state_root=tmp_path / "project" / "state",
            backup_root=tmp_path / "project" / "backup",
        )


def test_d1_state_store_round_trips_atomic_owned_state(profile):
    store = LocalOperationsStateStore(profile.state_root)
    state = _state(profile)
    store.write_state(state)
    assert store.read_state() == state
    assert not store.state_path.with_suffix(".json.tmp").exists()


def test_d1_state_rejects_non_loopback_url(profile):
    with pytest.raises(ValueError, match="exact loopback"):
        LocalRuntimeState(
            **{
                **_state(profile).__dict__,
                "url": "http://localhost:8775/",
            }
        )


def test_d2_preflight_validates_registered_artifacts_and_migration(profile):
    report = run_local_operations_preflight(profile)
    assert report.status == "READY"
    assert report.artifact_count == 16
    assert report.checks["registered_artifacts_valid"] is True
    assert report.checks["migration_compatible"] is True
    assert "MODELS_NOT_REQUIRED" in report.notifications[0]


def test_d2_cli_check_serializes_immutable_preflight_checks(
    profile,
    monkeypatch,
    capsys,
):
    monkeypatch.setattr(local_operations_cli, "default_profile", lambda: profile)

    assert local_operations_cli.main(["check"]) == 0
    payload = json.loads(capsys.readouterr().out)

    assert payload["status"] == "READY"
    assert payload["checks"]["registered_artifacts_valid"] is True
    assert payload["artifact_count"] == 16


def test_d2_preflight_reports_missing_model(profile):
    profile = LocalOperationsProfile(
        **{
            **profile.__dict__,
            "required_model_ids": ("registered-model-1",),
        }
    )
    report = run_local_operations_preflight(profile)
    assert report.status == "BLOCKED"
    assert report.missing_model_ids == ("registered-model-1",)
    assert any("MISSING_MODELS" in item for item in report.notifications)


def test_d2_preflight_reports_port_collision(profile):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as handle:
        handle.bind(("127.0.0.1", profile.port))
        report = run_local_operations_preflight(profile)
    assert report.status == "BLOCKED"
    assert report.checks["port_available"] is False
    assert any("PORT_UNAVAILABLE" in item for item in report.notifications)


def test_d2_preflight_reports_missing_database_target(profile):
    profile = LocalOperationsProfile(
        **{
            **profile.__dict__,
            "database_paths": (profile.project_root / "missing.db",),
        }
    )
    report = run_local_operations_preflight(profile)
    assert report.status == "BLOCKED"
    assert any("DATABASE_TARGET_MISSING" in item for item in report.notifications)


def test_d3_start_waits_for_health_then_opens_browser(profile):
    opened = []
    controller = OneClickLocalOperationsController(
        LocalOperationsProfile(**{**profile.__dict__, "open_browser": True}),
        process_launcher=lambda _profile, _instance: 4321,
        alive_probe=lambda _pid: True,
        health_probe=lambda _url: True,
        browser_opener=lambda url: opened.append(url) or True,
        clock=lambda: "2026-07-16T00:00:00+00:00",
        sleeper=lambda _seconds: None,
    )
    receipt = controller.start()
    assert receipt.status == "READY"
    assert opened == [profile.url]
    assert controller.store.read_state().lifecycle_state is LocalLifecycleState.READY


def test_d3_start_is_single_instance(profile):
    controller = OneClickLocalOperationsController(
        profile,
        process_launcher=lambda _profile, _instance: 4321,
        alive_probe=lambda _pid: True,
        health_probe=lambda _url: True,
        clock=lambda: "2026-07-16T00:00:00+00:00",
        sleeper=lambda _seconds: None,
    )
    assert controller.start().status == "READY"
    assert controller.start().status == "ALREADY_RUNNING"


def test_d3_failed_health_requests_owned_cleanup_without_force_kill(profile):
    controller = OneClickLocalOperationsController(
        profile,
        process_launcher=lambda _profile, _instance: 4321,
        alive_probe=lambda _pid: True,
        health_probe=lambda _url: False,
        clock=lambda: "2026-07-16T00:00:00+00:00",
        sleeper=lambda _seconds: None,
    )
    receipt = controller.start(health_timeout_seconds=0)
    state = controller.store.read_state()
    assert receipt.status == "BLOCKED"
    assert state.lifecycle_state is LocalLifecycleState.FAILED
    assert controller.store.stop_request_path(state.instance_id).is_file()
    assert receipt.unrelated_process_terminated is False


def test_d3_graceful_stop_uses_owned_instance_request(profile):
    store = LocalOperationsStateStore(profile.state_root)
    store.write_state(_state(profile))
    alive_results = iter((True, False))
    controller = OneClickLocalOperationsController(
        profile,
        alive_probe=lambda _pid: next(alive_results, False),
        clock=lambda: "2026-07-16T00:00:02+00:00",
        sleeper=lambda _seconds: None,
    )
    receipt = controller.stop()
    assert receipt.status == "STOPPED"
    request = json.loads(
        store.stop_request_path("a" * 32).read_text(encoding="ascii")
    )
    assert request["instance_id"] == "a" * 32
    assert request["pid"] == 4321
    assert receipt.unrelated_process_terminated is False


def test_d3_graceful_stop_accepts_owned_service_stopped_state(profile):
    store = LocalOperationsStateStore(profile.state_root)
    ready = _state(profile)
    store.write_state(ready)

    def observe_alive(_pid):
        current = store.read_state()
        if current.lifecycle_state is LocalLifecycleState.STOP_REQUESTED:
            store.write_state(
                LocalRuntimeState(
                    **{
                        **current.__dict__,
                        "lifecycle_state": LocalLifecycleState.STOPPED,
                    }
                )
            )
            return True
        return current.lifecycle_state is not LocalLifecycleState.STOPPED

    controller = OneClickLocalOperationsController(
        profile,
        alive_probe=observe_alive,
        clock=lambda: "2026-07-16T00:00:02+00:00",
        sleeper=lambda _seconds: None,
    )
    receipt = controller.stop()
    assert receipt.status == "STOPPED"
    assert controller.status().status == "STOPPED"


def test_d3_stop_timeout_never_force_terminates(profile):
    store = LocalOperationsStateStore(profile.state_root)
    store.write_state(_state(profile))
    controller = OneClickLocalOperationsController(
        profile,
        alive_probe=lambda _pid: True,
        clock=lambda: "2026-07-16T00:00:02+00:00",
        sleeper=lambda _seconds: None,
    )
    receipt = controller.stop(stop_timeout_seconds=0)
    assert receipt.status == "BLOCKED"
    assert "No process was force-terminated" in receipt.message
    assert receipt.unrelated_process_terminated is False


@pytest.mark.parametrize(
    ("alive", "healthy", "expected"),
    (
        (True, True, "READY"),
        (True, False, "DEGRADED"),
        (False, False, "STOPPED"),
    ),
)
def test_d4_status_exposes_health_and_degradation(profile, alive, healthy, expected):
    LocalOperationsStateStore(profile.state_root).write_state(_state(profile))
    controller = OneClickLocalOperationsController(
        profile,
        alive_probe=lambda _pid: alive,
        health_probe=lambda _url: healthy,
    )
    assert controller.status().status == expected


def test_d5_snapshot_contains_registered_data_state_and_manifest(profile):
    LocalOperationsStateStore(profile.state_root).write_state(_state(profile))
    destination = profile.backup_root / "backup.zip"
    receipt = OperationalSnapshotService().create_snapshot(profile, destination)
    assert receipt.status == "CREATED"
    assert receipt.automatic_activation_allowed is False
    with zipfile.ZipFile(destination, "r") as archive:
        names = archive.namelist()
        manifest = json.loads(archive.read("manifest.json"))
    assert "registered/index.json" in names
    assert "operations/runtime_state.json" in names
    assert manifest["database_backup_status"] == "NOT_CONFIGURED"
    assert manifest["automatic_activation_allowed"] is False


def test_d5_snapshot_includes_configured_database_target(profile):
    database = profile.project_root / "runtime" / "paper.db"
    database.parent.mkdir(parents=True)
    database.write_bytes(b"paper-database")
    profile = LocalOperationsProfile(
        **{**profile.__dict__, "database_paths": (database,)}
    )
    destination = profile.backup_root / "database-backup.zip"
    OperationalSnapshotService().create_snapshot(profile, destination)
    with zipfile.ZipFile(destination, "r") as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert archive.read("database/paper.db") == b"paper-database"
    assert manifest["database_backup_status"] == "INCLUDED"


def test_d5_recovery_is_staged_without_automatic_activation(profile):
    destination = profile.backup_root / "upgrade.zip"
    snapshots = OperationalSnapshotService()
    snapshots.create_snapshot(
        profile,
        destination,
        snapshot_kind="PRE_UPGRADE_SNAPSHOT",
    )
    recovery = profile.project_root / "recovery" / "candidate"
    receipt = snapshots.stage_recovery(destination, recovery)
    assert receipt.status == "RESTORED_TO_RECOVERY_STAGING"
    assert receipt.automatic_activation_allowed is False
    assert (recovery / "manifest.json").is_file()
    assert not (profile.project_root / "ACTIVE_BASELINE_REPLACED").exists()


def test_d5_recovery_rejects_nonempty_destination(profile):
    destination = profile.backup_root / "backup.zip"
    snapshots = OperationalSnapshotService()
    snapshots.create_snapshot(profile, destination)
    recovery = profile.project_root / "recovery"
    recovery.mkdir(parents=True)
    (recovery / "existing.txt").write_text("operator-owned", encoding="ascii")
    with pytest.raises(ValueError, match="absent or empty"):
        snapshots.stage_recovery(destination, recovery)


def test_d5_state_export_is_deterministic_copy(profile):
    store = LocalOperationsStateStore(profile.state_root)
    store.write_state(_state(profile))
    destination = profile.backup_root / "state.json"
    receipt = OperationalSnapshotService().export_state(profile, destination)
    assert receipt.status == "EXPORTED"
    assert json.loads(destination.read_text(encoding="ascii"))["instance_id"] == (
        "a" * 32
    )


def test_d5_windows_double_click_entries_do_not_require_powershell():
    windows_root = PROJECT_ROOT / "operations" / "windows"
    for name, command in (
        ("FCF Start.cmd", " start"),
        ("FCF Stop.cmd", " stop"),
        ("FCF Status.cmd", " status"),
        ("FCF Backup.cmd", " backup"),
    ):
        content = (windows_root / name).read_text(encoding="ascii")
        assert "powershell" not in content.lower()
        assert "one_click_local_operations_app_1.cli" in content
        assert command in content


def test_d6_acceptance_closes_stage_9_without_starting_next_phase():
    acceptance = build_one_click_local_operations_acceptance()
    assert acceptance.status == "D1_D6_ACCEPTED"
    assert all(acceptance.checks.values())
    assert acceptance.next_phase == "MULTI_MARKET_PAPER_SHADOW_VALIDATION"


def test_d6_real_background_start_health_and_graceful_stop():
    runtime_parent = PROJECT_ROOT / "runtime"
    runtime_parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix="one_click_stage_9_test_",
        dir=runtime_parent,
    ) as temporary:
        state_root = Path(temporary)
        profile = LocalOperationsProfile(
            project_root=PROJECT_ROOT,
            allowed_root=STARTER_ROOT,
            index_path=STARTER_ROOT / "index.json",
            state_root=state_root,
            backup_root=state_root / "backups",
            port=_reserve_port(),
            open_browser=False,
        )
        controller = OneClickLocalOperationsController(profile)
        started = controller.start(health_timeout_seconds=8)
        try:
            assert started.status == "READY"
            assert controller.status().status == "READY"
        finally:
            stopped = controller.stop(stop_timeout_seconds=8)
            _unlink_generated_log_with_retry(controller.store.log_path)
        assert stopped.status in {"STOPPED", "ALREADY_STOPPED"}
        deadline = time.monotonic() + 3
        while controller.status().status != "STOPPED" and time.monotonic() < deadline:
            time.sleep(0.05)
        assert controller.status().status == "STOPPED"
