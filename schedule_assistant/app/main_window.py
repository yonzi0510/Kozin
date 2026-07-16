"""일정 목록을 보여주고 추가/수정/삭제하는 메인 창."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .models import REPEAT_LABELS
from .schedule_dialog import ScheduleDialog
from .storage import ScheduleStore

COLUMNS = ["제목", "날짜/시간", "반복", "알림", "메모"]


class MainWindow(QWidget):
    def __init__(self, store: ScheduleStore):
        super().__init__()
        self._store = store
        self.setWindowTitle("일정 관리 비서")
        self.resize(640, 420)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.doubleClicked.connect(self._edit_selected)

        add_btn = QPushButton("추가")
        edit_btn = QPushButton("수정")
        delete_btn = QPushButton("삭제")
        add_btn.clicked.connect(self.add_schedule)
        edit_btn.clicked.connect(self._edit_selected)
        delete_btn.clicked.connect(self._delete_selected)

        btn_row = QHBoxLayout()
        btn_row.addWidget(add_btn)
        btn_row.addWidget(edit_btn)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addLayout(btn_row)
        layout.addWidget(self.table)

        self.refresh()

    def refresh(self) -> None:
        schedules = self._store.all()
        self.table.setRowCount(len(schedules))
        for row, sched in enumerate(schedules):
            values = [
                sched.title,
                sched.when.strftime("%Y-%m-%d %H:%M"),
                REPEAT_LABELS.get(sched.repeat, sched.repeat),
                f"{sched.remind_before}분 전",
                sched.memo,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.UserRole, sched.id)
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

    def add_schedule(self) -> None:
        dialog = ScheduleDialog(self)
        if dialog.exec() == ScheduleDialog.Accepted:
            sched = dialog.result_schedule()
            if sched:
                self._store.add(sched)
                self.refresh()

    def _selected_schedule_id(self) -> str | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        return item.data(Qt.UserRole) if item else None

    def _edit_selected(self) -> None:
        schedule_id = self._selected_schedule_id()
        if not schedule_id:
            return
        sched = self._store.get(schedule_id)
        if not sched:
            return
        dialog = ScheduleDialog(self, schedule=sched)
        if dialog.exec() == ScheduleDialog.Accepted:
            self._store.update(sched)
            self.refresh()

    def _delete_selected(self) -> None:
        schedule_id = self._selected_schedule_id()
        if not schedule_id:
            return
        reply = QMessageBox.question(self, "삭제 확인", "선택한 일정을 삭제할까요?")
        if reply == QMessageBox.Yes:
            self._store.delete(schedule_id)
            self.refresh()

    def select_schedule(self, schedule_id: str) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.data(Qt.UserRole) == schedule_id:
                self.table.selectRow(row)
                break
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def closeEvent(self, event) -> None:  # noqa: N802
        event.ignore()
        self.hide()
