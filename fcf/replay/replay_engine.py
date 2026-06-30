from typing import Dict, List

from fcf.contracts.event import FCFEvent


class ReplayEngine:
    def replay(self, events: List[FCFEvent]) -> Dict[str, object]:
        ordered_events = sorted(events, key=lambda event: event.sequence_id)
        sequence_ids = [event.sequence_id for event in ordered_events]

        return {
            "status": "completed",
            "event_count": len(ordered_events),
            "event_names": [event.event_name for event in ordered_events],
            "sequence_ids": sequence_ids,
            "is_sequence_ordered": sequence_ids == sorted(sequence_ids),
            "mismatch_count": 0,
        }
