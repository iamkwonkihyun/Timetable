# import library
import time, datetime, logging, os, sys, win32com.client, shutil
from logging.handlers import TimedRotatingFileHandler
from win10toast import ToastNotifier
from data.data import TIMETABLE
from data.test_data import TEST_TIMETABLE

programName = "pyw.exe"

# log 생성
if os.path.exists("logs"):
    shutil.rmtree("logs")
if not os.path.exists("logs"):
    os.makedirs("logs")

# 하루마다 새로운 로그 파일 생성, 최대 7개 유지
handler = TimedRotatingFileHandler("logs/app.log", when="D", interval=1, backupCount=7)
handler.suffix = "%Y-%m-%d.log"
logging.basicConfig(
    filename="logs/app.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logging.info("START PROGRAM")

# toaster 객체 생성
toaster = ToastNotifier()

# 프로그램 실행 검사
wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
service = wmi.ConnectServer(".", "root\\cimv2")
process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{programName}'")

# while True:
#     print(len(process_list))
#     if len(process_list) > 0:
#         toaster.show_toast(
#             "Hello!",
#             "Timetable.pyw is Running!\nDon't worry, it is not hacking :)",
#             duration=None,
#             threaded=True,
#         )
#         logging.info("program running check: GOOD")
#         break
#     else:
#         toaster.show_toast(
#             "Error",
#             "fucking Error\nI don't like Error",
#             duration=None,
#             threaded=True,
#         )
#         logging.ERROR("program running check: BAD")
#         sys.exit()

# notification 한 번만 보내게 해줄 변수
notified_times = set()

while True:
    
    # today = "Monday"
    today = datetime.datetime.today().strftime("%A")
    
    # now = HH:MM
    now = datetime.datetime.now().strftime("%H:%M")
    strp_now = datetime.datetime.strptime(now, "%H:%M") + datetime.timedelta(minutes=10)
    endTime = strp_now.strftime("%H:%M")

    if today not in ["Saturday", "Sunday"]:
        logging.info(f"WEEKDAYS:{today} KEEP RUNNING")
        if now in TIMETABLE[today] and now not in notified_times:
            subject = TIMETABLE[today][now]
            toaster.show_toast(
                f"{today} Class Notification",
                f"Next Class: {subject}",
                duration=None,
                threaded=True,
            )
            logging.info(f"{today} | {now} | {subject}")
            notified_times.add(now)
            
        if endTime == "8:30":
            logging.info("endTime 8:30 pass")
            continue
        elif endTime in TIMETABLE[today] and endTime not in notified_times:
            toaster.show_toast(
                f"{today} Class Notification",
                f"10 minutes before the end of class",
                duration=None,
                threaded=True,
            )
            logging.info(f"{today} | {now} | {subject}")
            notified_times.add(endTime)
            
        time.sleep(1)
        continue
    else:
        logging.info(f"WEEKEND:{today} KEEP RUNNING")
        time.sleep(1)
        continue
            