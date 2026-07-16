"""일정 추가/수정 다이얼로그."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QDate, QTime
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QTextEdit,
    QTimeEdit,
)

from .models import (
    REPEAT_DAILY,
    REPEAT_LABELS,
    REPEAT_MONTHLY,
    REPEAT_NONE,
    REPEAT_WEEKLY,
    Schedule,
)

REPEAT_ORDER = [REPEAT_NONE, REPEAT_DAILY, REPEAT_WEEKLY, REPEAT_MONTHLY]


class ScheduleDialog(QDialog):
    def __init__(self, parent=None, schedule: Schedule | None = None):
        super().__init__(parent)
        self._editing = schedule
        self.setWindowTitle("일정 수정" if schedule else "새 일정")
        self.setMinimumWidth(360)

        self.title_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.repeat_combo = QComboBox()
        for key in REPEAT_ORDER:
            self.repeat_combo.addItem(REPEAT_LABELS[key], key)
        self.remind_spin = QSpinBox()
        self.remind_spin.setRange(0, 1440)
        self.remind_spin.setSuffix(" 분 전")
        self.remind_spin.setValue(10)
        self.memo_edit = QTextEdit()
        self.memo_edit.setFixedHeight(70)

        now = datetime.now()
        self.date_edit.setDate(QDate(now.year, now.month, now.day))
        self.time_edit.setTime(QTime(now.hour, now.minute))

        if schedule:
            self.title_edit.setText(schedule.title)
            self.date_edit.setDate(QDate(schedule.when.year, schedule.when.month, schedule.when.day))
            self.time_edit.setTime(QTime(schedule.when.hour, schedule.when.minute))
            idx = REPEAT_ORDER.index(schedule.repeat) if schedule.repeat in REPEAT_ORDER else 0
            self.repeat_combo.setCurrentIndex(idx)
            self.remind_spin.setValue(schedule.remind_before)
            self.memo_edit.setPlainText(schedule.memo)

        form = QFormLayout(self)
        form.addRow("제목", self.title_edit)
        form.addRow("날짜", self.date_edit)
        form.addRow("시간", self.time_edit)
        form.addRow("반복", self.repeat_combo)
        form.addRow("알림", self.remind_spin)
        form.addRow("메모", self.memo_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

        self._result_schedule: Schedule | None = None

    def _on_accept(self) -> None:
        if not self.title_edit.text().strip():
            self.title_edit.setFocus()
            return
        d = self.date_edit.date()
        t = self.time_edit.time()
        when = datetime(d.year(), d.month(), d.day(), t.hour(), t.minute())
        repeat = self.repeat_combo.currentData()
        remind_before = self.remind_spin.value()
        memo = self.memo_edit.toPlainText().strip()
        title = self.title_edit.text().strip()

        if self._editing:
            self._editing.title = title
            self._editing.when = when
            self._editing.repeat = repeat
            self._editing.remind_before = remind_before
            self._editing.memo = memo
            self._editing.last_reminded_occurrence = None
            self._editing.last_started_occurrence = None
            self._result_schedule = self._editing
        else:
            self._result_schedule = Schedule(
                title=title,
                when=when,
                repeat=repeat,
                remind_before=remind_before,
                memo=memo,
            )
        self.accept()

    def result_schedule(self) -> Schedule | None:
        return self._result_schedule
