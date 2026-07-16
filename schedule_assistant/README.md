# 일정 관리 비서 (Schedule Assistant)

Windows 시스템 트레이에 상주하면서, 등록한 일정의 예정 시간이 다가오면
화면에 말풍선(풍선 도움말 스타일) 알림을 띄워주는 데스크톱 프로그램입니다.

## 주요 기능

- 일정 등록 / 조회 / 수정 / 삭제
- 예정 시간 N분 전 말풍선 알림 (알림 시간은 일정별로 설정 가능)
- 반복 일정: 매일 / 매주 / 매월
- Windows 로그인 시 자동 실행 (트레이 메뉴에서 켜고 끄기)
- 트레이 아이콘 상주, 창을 닫아도 백그라운드에서 계속 동작

## 실행 방법

```bash
pip install -r requirements.txt
python main.py
```

macOS/Linux에서도 PySide6가 설치되어 있으면 동작하지만,
"시작 시 자동 실행" 기능은 Windows에서만 지원됩니다.

## 배포용 실행 파일 만들기 (선택)

PyInstaller로 단일 실행 파일(exe)을 만들 수 있습니다.

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name ScheduleAssistant main.py
```

`--noconsole` 옵션을 주면 콘솔 창 없이 트레이 아이콘만 뜹니다.

## 데이터 저장 위치

일정 데이터는 `%APPDATA%\ScheduleAssistant\schedules.json` (Windows 기준)에
저장됩니다.

## 폴더 구조

```
schedule_assistant/
  main.py              실행 진입점
  app/
    models.py           일정 데이터 모델, 반복 발생 계산
    storage.py           JSON 파일 저장소
    scheduler.py         주기적으로 일정을 확인해 알림 신호 발생
    notification.py      말풍선 알림 위젯
    tray.py               시스템 트레이 아이콘/메뉴
    main_window.py       일정 목록 창
    schedule_dialog.py   일정 추가/수정 다이얼로그
    autostart.py         Windows 시작프로그램 등록/해제
```
