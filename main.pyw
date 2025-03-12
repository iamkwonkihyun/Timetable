# import library
import logging, os, shutil, threading
from logging.handlers import TimedRotatingFileHandler
from function.programCheck import programCheck
from function.systemTray import systemTray
from function.timetableReminder import timetableReminder

# True = all Test Mode, False = All real Time Mode
isTest = True
# True = 주중, False = 주말( isTest가 False 일땐 wnat 아무 기능 안함)
want = True
# program name
programName = ["pyw.exe", "pythonw.exe"]

# 로그 폴더 경로
log_folder = "logs"

# 로그 폴더가 없으면 생성
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

# 하루마다 새로운 로그 파일 생성, 최대 7개 유지
handler = TimedRotatingFileHandler(
    os.path.join(log_folder, "app.log"), when="D", interval=1, backupCount=7, encoding="utf-8"
)
handler.suffix = "%Y-%m-%d.log"

# 기존 log 파일 삭제 코드 제거 (자동으로 관리됨)
logging.shutdown()

logging.basicConfig(
    filename="logs/app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logging.info("MAEK log folder: GOOD")

# 프로그램 실행 체크 함수(isTest=True: vscode 실행 시, isTest=False: main.pyw 실행 시)
programCheck(programName=programName, isTest=isTest)

logging.info("START PROGRAM")
            
if __name__ == "__main__":
    #timetableReminder만 백그라운드에서 단독 실행
    timetable_reminder = threading.Thread(target=timetableReminder, args=(isTest, want), daemon=True)
    timetable_reminder.start()
    #system tray 설정
    app = systemTray()
    app.run()
