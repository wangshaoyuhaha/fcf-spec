from main import run_minimal_spine
from fcf.replay.replay_engine import ReplayEngine


def test_minimal_spine_event_count():
    store = run_minimal_spine()

    assert store.count() == 4


def test_minimal_spine_event_order():
    store = run_minimal_spine()
    events = store.all_events()

    assert [event.event_name for event in events] == [
        "fcf.data.raw_received",
        "fcf.data.normalized",
        "fcf.regime.detected",
        "fcf.decision.proposed",
    ]


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
    assert result["event_count"] == 4
    assert result["event_names"] == [
        "fcf.data.raw_received",
        "fcf.data.normalized",
        "fcf.regime.detected",
        "fcf.decision.proposed",
    ]
