"""주기적으로 일정을 확인해 알림이 필요한 시점을 판단한다."""

from __future__ import annotations

from datetime import datetime, timedelta

from PySide6.QtCore import QObject, QTimer, Signal

from .storage import ScheduleStore

CHECK_INTERVAL_MS = 20_000


class ScheduleChecker(QObject):
    reminder_due = Signal(str, str, str)  # schedule_id, title, message
    start_due = Signal(str, str, str)

    def __init__(self, store: ScheduleStore, parent=None):
        super().__init__(parent)
        self._store = store
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.check_now)
        self._timer.start(CHECK_INTERVAL_MS)

    def check_now(self) -> None:
        now = datetime.now()
        changed = False
        for sched in self._store.all():
            occ = sched.current_occurrence(now)
            if occ is None:
                continue
            key = sched.occurrence_key(occ)
            remind_at = occ - timedelta(minutes=max(sched.remind_before, 0))

            if remind_at <= now < occ and sched.last_reminded_occurrence != key:
                minutes = max(sched.remind_before, 0)
                when_text = f"{minutes}분 후" if minutes > 0 else "곧"
                self.reminder_due.emit(
                    sched.id,
                    sched.title,
                    f"{when_text} 시작: {occ.strftime('%m/%d %H:%M')}" + (f"\n{sched.memo}" if sched.memo else ""),
                )
                sched.last_reminded_occurrence = key
                changed = True

            if now >= occ and sched.last_started_occurrence != key:
                self.start_due.emit(
                    sched.id,
                    sched.title,
                    "지금 시작하는 일정입니다." + (f"\n{sched.memo}" if sched.memo else ""),
                )
                sched.last_started_occurrence = key
                changed = True

        if changed:
            self._store.save()
