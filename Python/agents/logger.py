# Python/agents/logger.py

import sqlite3
from datetime import datetime
from pathlib import Path


class LoggingAgent:
    def __init__(self, db_path: str = "db/logs.db"):
        """
        SQLite-based logging agent for observability.
        Creates DB and tables automatically on first run.
        """
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """Create database and logs table if not exists."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                agent_name TEXT,
                input_data TEXT,
                output_data TEXT
            )
            """
        )

        conn.commit()
        conn.close()

    def log_step(self, agent_name: str, input_data: str, output_data: str):
        """
        Log a single agent step.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO agent_logs (timestamp, agent_name, input_data, output_data)
            VALUES (?, ?, ?, ?)
            """,
            (
                datetime.utcnow().isoformat(),
                agent_name,
                input_data,
                output_data,
            ),
        )

        conn.commit()
        conn.close()
