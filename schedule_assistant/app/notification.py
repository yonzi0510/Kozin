"""말풍선 스타일의 데스크톱 알림 위젯."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer, QRectF, Signal
from PySide6.QtGui import QPainter, QPainterPath, QColor, QFont
from PySide6.QtWidgets import QWidget, QApplication

BUBBLE_WIDTH = 300
BUBBLE_HEIGHT = 96
TAIL_SIZE = 14
MARGIN = 16
SPACING = 10
DISPLAY_MS = 7000


class BubbleNotification(QWidget):
    """화면 우측 하단에 떠오르는 말풍선 알림 한 개."""

    clicked = Signal(str)  # schedule_id

    def __init__(self, title: str, message: str, schedule_id: str = ""):
        super().__init__(
            None,
            Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool,
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._title = title
        self._message = message
        self._schedule_id = schedule_id

        self.resize(BUBBLE_WIDTH, BUBBLE_HEIGHT + TAIL_SIZE)

        self._close_timer = QTimer(self)
        self._close_timer.setSingleShot(True)
        self._close_timer.timeout.connect(self.close)
        self._close_timer.start(DISPLAY_MS)

    def mousePressEvent(self, event):  # noqa: N802 (Qt override)
        if self._schedule_id:
            self.clicked.emit(self._schedule_id)
        self.close()

    def enterEvent(self, event):  # noqa: N802
        self._close_timer.stop()
        super().enterEvent(event)

    def leaveEvent(self, event):  # noqa: N802
        self._close_timer.start(DISPLAY_MS)
        super().leaveEvent(event)

    def paintEvent(self, event):  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        body_rect = QRectF(0, 0, BUBBLE_WIDTH, BUBBLE_HEIGHT)
        path = QPainterPath()
        path.addRoundedRect(body_rect, 14, 14)

        tail_x = BUBBLE_WIDTH - 34
        path.moveTo(tail_x, BUBBLE_HEIGHT)
        path.lineTo(tail_x + TAIL_SIZE, BUBBLE_HEIGHT + TAIL_SIZE)
        path.lineTo(tail_x + TAIL_SIZE * 2, BUBBLE_HEIGHT)
        path.closeSubpath()

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(45, 45, 55, 235))
        painter.drawPath(path)

        painter.setPen(QColor(255, 255, 255))
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        painter.setFont(title_font)
        painter.drawText(QRectF(18, 12, BUBBLE_WIDTH - 36, 24), Qt.AlignLeft | Qt.AlignVCenter, self._title)

        msg_font = QFont()
        msg_font.setPointSize(10)
        painter.setFont(msg_font)
        painter.setPen(QColor(220, 220, 225))
        painter.drawText(
            QRectF(18, 38, BUBBLE_WIDTH - 36, BUBBLE_HEIGHT - 46),
            Qt.AlignLeft | Qt.TextWordWrap,
            self._message,
        )


class NotificationManager:
    """화면에 떠 있는 말풍선들을 우측 하단에 스택으로 배치한다."""

    def __init__(self, on_bubble_clicked=None):
        self._active: list[BubbleNotification] = []
        self._on_bubble_clicked = on_bubble_clicked

    def show(self, title: str, message: str, schedule_id: str = "") -> None:
        bubble = BubbleNotification(title, message, schedule_id)
        bubble.destroyed.connect(lambda: self._on_destroyed(bubble))
        if self._on_bubble_clicked:
            bubble.clicked.connect(self._on_bubble_clicked)
        self._active.append(bubble)
        self._reposition()
        bubble.show()

    def _on_destroyed(self, bubble) -> None:
        if bubble in self._active:
            self._active.remove(bubble)
        self._reposition()

    def _reposition(self) -> None:
        screen = QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        y = geo.bottom() - MARGIN
        for bubble in reversed(self._active):
            y -= bubble.height()
            x = geo.right() - MARGIN - bubble.width()
            bubble.move(x, y)
            y -= SPACING
