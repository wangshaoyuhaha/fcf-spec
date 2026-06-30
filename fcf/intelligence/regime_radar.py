from fcf.contracts.event import FCFEvent, create_event


class RegimeRadar:
    def detect(self, normalized_event: FCFEvent) -> FCFEvent:
        return create_event(
            event_name="fcf.regime.detected",
            source_module="regime_radar",
            correlation_id=normalized_event.correlation_id,
            causation_id=normalized_event.event_id,
            payload={
                "target_id": "demo_target",
                "regime": "demo_ready",
                "confidence": 1.0,
            },
        )
