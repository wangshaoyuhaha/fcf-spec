from typing import Any, Dict
from uuid import uuid4

from fcf.contracts.event import FCFEvent, create_event


class DataIngestor:
    def ingest_demo_data(self) -> FCFEvent:
        correlation_id = str(uuid4())

        return create_event(
            event_name="fcf.data.raw_received",
            source_module="data_ingestor",
            correlation_id=correlation_id,
            payload={
                "data_type": "demo",
                "source": "manual_demo",
                "data_body": {"message": "hello FCF"},
            },
        )
