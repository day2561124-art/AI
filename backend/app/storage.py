from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4
import json


class JsonStore:
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()

    def _path(self, name: str) -> Path:
        return self.data_dir / f"{name}.json"

    def _read(self, name: str) -> list[dict]:
        path = self._path(name)
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _write(self, name: str, rows: list[dict]) -> None:
        path = self._path(name)
        path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    def append(self, name: str, row: dict) -> dict:
        with self._lock:
            rows = self._read(name)
            saved = {
                "id": str(uuid4()),
                "created_at": datetime.now(timezone.utc).isoformat(),
                **row,
            }
            rows.append(saved)
            self._write(name, rows)
            return saved

    def list(self, name: str, limit: int = 50) -> list[dict]:
        rows = self._read(name)
        return list(reversed(rows))[:limit]

    def stats(self) -> dict:
        chat_logs = self._read("chat_logs")
        feedback = self._read("feedback")
        unanswered = self._read("unanswered_questions")
        return {
            "chat_count": len(chat_logs),
            "feedback_count": len(feedback),
            "unanswered_count": len(unanswered),
            "helpful_count": sum(1 for item in feedback if item.get("helpful") is True),
            "not_helpful_count": sum(1 for item in feedback if item.get("helpful") is False),
        }

