"""일정(Schedule) 데이터 모델 및 다음 발생 시각 계산 로직."""

from __future__ import annotations

import calendar
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta

REPEAT_NONE = "none"
REPEAT_DAILY = "daily"
REPEAT_WEEKLY = "weekly"
REPEAT_MONTHLY = "monthly"

REPEAT_LABELS = {
    REPEAT_NONE: "반복 없음",
    REPEAT_DAILY: "매일",
    REPEAT_WEEKLY: "매주",
    REPEAT_MONTHLY: "매월",
}

DATETIME_FMT = "%Y-%m-%dT%H:%M:%S"


def _add_month(dt: datetime) -> datetime:
    """dt에서 한 달을 더한 시각을 반환한다. 말일 초과분은 그 달의 마지막 날로 보정한다."""
    year = dt.year + (dt.month // 12)
    month = dt.month % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(dt.day, last_day)
    return dt.replace(year=year, month=month, day=day)


@dataclass
class Schedule:
    title: str
    when: datetime
    repeat: str = REPEAT_NONE
    remind_before: int = 10  # 분 단위
    memo: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    last_reminded_occurrence: str | None = None
    last_started_occurrence: str | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        d["when"] = self.when.strftime(DATETIME_FMT)
        return d

    @classmethod
    def from_dict(cls, d: dict) -> "Schedule":
        data = dict(d)
        data["when"] = datetime.strptime(data["when"], DATETIME_FMT)
        return cls(**data)

    def current_occurrence(self, now: datetime) -> datetime | None:
        """알림 판단에 사용할 '현재 관련된' 발생 시각을 반환한다.

        반복 일정은 알림 대상 창(occurrence + remind_before분)이 이미 지났으면
        다음 발생 시각으로 넘어간다. 단발성 일정은 그 시각이 알림 창을 완전히
        지났다면 None을 반환한다(더 이상 알릴 것이 없음).
        """
        occ = self.when
        window_end = timedelta(minutes=max(self.remind_before, 0)) + timedelta(minutes=1)

        if self.repeat == REPEAT_NONE:
            return occ if occ + window_end >= now else None

        step = None
        if self.repeat == REPEAT_DAILY:
            step = timedelta(days=1)
        elif self.repeat == REPEAT_WEEKLY:
            step = timedelta(weeks=1)

        guard = 0
        while occ + window_end < now and guard < 10000:
            occ = _add_month(occ) if self.repeat == REPEAT_MONTHLY else occ + step
            guard += 1
        return occ

    def occurrence_key(self, occurrence: datetime) -> str:
        return occurrence.strftime(DATETIME_FMT)
