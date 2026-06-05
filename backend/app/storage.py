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

    def all(self, name: str) -> list[dict]:
        return self._read(name)

    def stats(self) -> dict:
        chat_logs = self._read("chat_logs")
        feedback = self._read("feedback")
        unanswered = self._read("unanswered_questions")
        visits = self._read("visits")
        visitor_counts: dict[str, int] = {}
        for visit in visits:
            visitor_id = visit.get("visitor_id") or "unknown"
            visitor_counts[visitor_id] = visitor_counts.get(visitor_id, 0) + 1

        helpful_count = sum(1 for item in feedback if item.get("helpful") is True)
        not_helpful_count = sum(1 for item in feedback if item.get("helpful") is False)
        total_feedback = len(feedback)
        cag_count = sum(1 for item in chat_logs if item.get("answer_mode") == "CAG")
        rag_count = sum(1 for item in chat_logs if item.get("answer_mode") in {"RAG", "RAG+LLM"})
        memory_count = sum(1 for item in chat_logs if item.get("memory_used") is True)
        llm_count = sum(1 for item in chat_logs if item.get("llm_used") is True)
        return {
            "chat_count": len(chat_logs),
            "visit_count": len(visits),
            "unique_visitor_count": len(visitor_counts),
            "repeat_visit_count": sum(max(count - 1, 0) for count in visitor_counts.values()),
            "repeat_visitor_count": sum(1 for count in visitor_counts.values() if count > 1),
            "feedback_count": total_feedback,
            "unanswered_count": len(unanswered),
            "helpful_count": helpful_count,
            "not_helpful_count": not_helpful_count,
            "helpful_rate": round((helpful_count / total_feedback) * 100, 1) if total_feedback else 0,
            "cag_count": cag_count,
            "rag_count": rag_count,
            "memory_count": memory_count,
            "llm_count": llm_count,
        }

    def visitor_visit_count(self, visitor_id: str) -> int:
        visits = self._read("visits")
        return sum(1 for visit in visits if visit.get("visitor_id") == visitor_id)
