from fcf.contracts.event import FCFEvent, create_event


class Normalizer:
    def normalize(self, raw_event: FCFEvent) -> FCFEvent:
        return create_event(
            event_name="fcf.data.normalized",
            source_module="normalizer",
            correlation_id=raw_event.correlation_id,
            causation_id=raw_event.event_id,
            payload={
                "data_type": raw_event.payload.get("data_type", "unknown"),
                "quality_score": 1.0,
                "normalized_data": raw_event.payload.get("data_body", {}),
            },
        )
