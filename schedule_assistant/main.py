"""일정 관리 비서 진입점.

시스템 트레이에 상주하며 등록된 일정의 예정 시간 전에 화면에 말풍선
알림을 띄운다. `python main.py` 로 실행한다 (Windows 권장).
"""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from app.main_window import MainWindow
from app.notification import NotificationManager
from app.scheduler import ScheduleChecker
from app.storage import ScheduleStore
from app.tray import Tray


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("이 시스템에서는 트레이 아이콘을 사용할 수 없습니다.", file=sys.stderr)

    store = ScheduleStore()
    main_window = MainWindow(store)

    notifications = NotificationManager(on_bubble_clicked=main_window.select_schedule)

    tray = Tray(main_window, add_schedule_callback=lambda: (main_window.showNormal(), main_window.add_schedule()))
    tray.show()

    checker = ScheduleChecker(store)

    def handle_reminder(schedule_id: str, title: str, message: str) -> None:
        notifications.show(title, message, schedule_id)
        main_window.refresh()

    checker.reminder_due.connect(handle_reminder)
    checker.start_due.connect(handle_reminder)
    checker.check_now()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
