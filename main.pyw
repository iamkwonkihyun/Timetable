# import library, package
import logging, os, threading
from logging.handlers import TimedRotatingFileHandler
from function.mainTray import mainTray
from function.notificationFunc import notificationFunc
from function.mainFunctions import loggingFunc, programCheck

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

loggingFunc(title="makeLogFolder", comment="GOOD :)")

# 프로그램 실행 체크 함수(isTest=True: vscode 실행 시, isTest=False: main.pyw 실행 시)

if __name__ == "__main__":
    programCheck(programName=programName)
    #timetableReminderFunc 백그라운드에서 단독 실행
    timetableReminderFunc = threading.Thread(target=notificationFunc, args=(), daemon=True)
    timetableReminderFunc.start()
    #system tray 설정
    app = mainTray()
    app.run()
