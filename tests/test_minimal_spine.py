from main import run_minimal_spine
from fcf.replay.replay_engine import ReplayEngine


EXPECTED_EVENT_NAMES = [
    "fcf.data.raw_received",
    "fcf.data.normalized",
    "fcf.regime.detected",
    "fcf.decision.proposed",
    "fcf.policy.reviewed",
    "fcf.order.approved",
    "fcf.order.executed",
    "fcf.shadow.simulated",
]


def test_minimal_spine_event_count():
    store = run_minimal_spine()

    assert store.count() == 8


def test_minimal_spine_event_order():
    store = run_minimal_spine()
    events = store.all_events()

    assert [event.event_name for event in events] == EXPECTED_EVENT_NAMES


def test_minimal_spine_sequence_ids_are_increasing():
    store = run_minimal_spine()
    events = store.all_events()
    sequence_ids = [event.sequence_id for event in events]

    assert sequence_ids == sorted(sequence_ids)


def test_minimal_spine_correlation_id_is_consistent():
    store = run_minimal_spine()
    events = store.all_events()
    correlation_ids = {event.correlation_id for event in events}

    assert len(correlation_ids) == 1


def test_replay_engine_reads_events():
    store = run_minimal_spine()
    replay_engine = ReplayEngine()

    result = replay_engine.replay(store.all_events())

    assert result["status"] == "completed"
    assert result["event_count"] == 8
    assert result["event_names"] == EXPECTED_EVENT_NAMES


def test_d9_policy_and_execution_events_exist():
    store = run_minimal_spine()
    event_names = [event.event_name for event in store.all_events()]

    assert "fcf.policy.reviewed" in event_names
    assert "fcf.order.approved" in event_names
    assert "fcf.order.executed" in event_names
    assert "fcf.shadow.simulated" in event_names


def test_event_store_save_and_load_jsonl(tmp_path):
    store = run_minimal_spine()
    file_path = tmp_path / "events.jsonl"

    store.save_jsonl(str(file_path))
    loaded_store = type(store).load_jsonl(str(file_path))

    assert loaded_store.count() == 8
    assert [event.event_name for event in loaded_store.all_events()] == EXPECTED_EVENT_NAMES


def test_replay_engine_replays_loaded_jsonl_events(tmp_path):
    store = run_minimal_spine()
    file_path = tmp_path / "events.jsonl"

    store.save_jsonl(str(file_path))
    loaded_store = type(store).load_jsonl(str(file_path))

    replay_engine = ReplayEngine()
    result = replay_engine.replay(loaded_store.all_events())

    assert result["status"] == "completed"
    assert result["event_count"] == 8
    assert result["event_names"] == EXPECTED_EVENT_NAMES
    assert result["is_sequence_ordered"] is True
    assert result["mismatch_count"] == 0
