import json
import sqlite3
from pathlib import Path
from typing import Optional
from fcf.core.event_model import Event


class AuditStore:
    def __init__(self, db_path: str = "fcf_events.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT UNIQUE NOT NULL,
            event_type TEXT NOT NULL,
            event_version TEXT NOT NULL,
            producer TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            correlation_id TEXT NOT NULL,
            payload_json TEXT NOT NULL
        )
        """)
        self.conn.commit()

    async def log_event(self, event: Event) -> None:
        self.conn.execute(
            """
            INSERT OR IGNORE INTO events
            (event_id, event_type, event_version, producer, timestamp, correlation_id, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.event_id,
                event.event_type,
                event.event_version,
                event.producer,
                event.timestamp,
                event.correlation_id,
                json.dumps(event.payload, ensure_ascii=False),
            ),
        )
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
