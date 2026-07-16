"""일정 목록을 JSON 파일로 저장/로드한다."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from .models import Schedule


def default_data_dir() -> Path:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "ScheduleAssistant"
    return Path.home() / ".schedule_assistant"


class ScheduleStore:
    def __init__(self, data_dir: Path | None = None):
        self.data_dir = data_dir or default_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / "schedules.json"
        self._schedules: dict[str, Schedule] = {}
        self.load()

    def load(self) -> None:
        self._schedules = {}
        if not self.file_path.exists():
            return
        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        for item in raw:
            try:
                sched = Schedule.from_dict(item)
                self._schedules[sched.id] = sched
            except (KeyError, ValueError):
                continue

    def save(self) -> None:
        payload = [s.to_dict() for s in self._schedules.values()]
        tmp_path = self.file_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(self.file_path)

    def all(self) -> list[Schedule]:
        return sorted(self._schedules.values(), key=lambda s: s.when)

    def get(self, schedule_id: str) -> Schedule | None:
        return self._schedules.get(schedule_id)

    def add(self, schedule: Schedule) -> None:
        self._schedules[schedule.id] = schedule
        self.save()

    def update(self, schedule: Schedule) -> None:
        self._schedules[schedule.id] = schedule
        self.save()

    def delete(self, schedule_id: str) -> None:
        self._schedules.pop(schedule_id, None)
        self.save()
