"""시스템 트레이 아이콘과 메뉴."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from . import autostart


def _build_icon() -> QIcon:
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor(76, 141, 255))
    painter.drawEllipse(4, 4, 56, 56)
    painter.setPen(QColor(255, 255, 255))
    pen = painter.pen()
    pen.setWidth(4)
    pen.setCapStyle(Qt.RoundCap)
    painter.setPen(pen)
    painter.drawLine(32, 32, 32, 16)
    painter.drawLine(32, 32, 44, 36)
    painter.end()
    return QIcon(pixmap)


class Tray(QSystemTrayIcon):
    def __init__(self, main_window, add_schedule_callback):
        super().__init__(_build_icon())
        self._main_window = main_window
        self.setToolTip("일정 관리 비서")

        menu = QMenu()
        open_action = QAction("일정 관리 열기", menu)
        open_action.triggered.connect(self._show_main_window)
        menu.addAction(open_action)

        add_action = QAction("새 일정 추가", menu)
        add_action.triggered.connect(add_schedule_callback)
        menu.addAction(add_action)

        menu.addSeparator()

        self.autostart_action = QAction("시작 시 자동 실행", menu)
        self.autostart_action.setCheckable(True)
        self.autostart_action.setEnabled(autostart.is_supported())
        self.autostart_action.setChecked(autostart.is_enabled())
        self.autostart_action.toggled.connect(autostart.set_enabled)
        menu.addAction(self.autostart_action)

        menu.addSeparator()

        quit_action = QAction("종료", menu)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.activated.connect(self._on_activated)

    def _on_activated(self, reason) -> None:
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self._show_main_window()

    def _show_main_window(self) -> None:
        self._main_window.showNormal()
        self._main_window.raise_()
        self._main_window.activateWindow()
