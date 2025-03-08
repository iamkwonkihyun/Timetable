# import library
import time, datetime, logging, os, sys, win32com.client, shutil
from logging.handlers import TimedRotatingFileHandler
from win10toast import ToastNotifier
from data.data import TIMETABLE
from data.test_data import TEST_TIMETABLE
from function.isBirthday import isBirthday

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
logging.info("PROGRAM CHECKING: ···")
wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
service = wmi.ConnectServer(".", "root\\cimv2")
process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{programName}'")

while True:
    print(len(process_list))
    if len(process_list) > 0:
        toaster.show_toast(
            "Hello!",
            "Timetable.pyw is Running!\nDon't worry, it is not hacking :)",
            duration=3,
            threaded=False,
        )
        logging.info("PROGRAM CHECKING: GOOD :)")
        break
    else:
        toaster.show_toast(
            "Error",
            "fucking Error\nI don't like Error",
            duration=3,
            threaded=False,
        )
        logging.ERROR("PROGRAM CHECKING: BAD :(")
        sys.exit()

# notification 한 번만 보내게 해줄 변수
notified_times = set()

while True:
    # num_today = "01-01"
    num_today = datetime.datetime.today().strftime("%m-%d")
    
    # str_today = "Monday"
    str_today = datetime.datetime.today().strftime("%A")
    
    # now_time = "HH:MM"
    now_time = datetime.datetime.now().strftime("%H:%M")
    
    # end_time = "HH:MM" + 10 minutes
    end_time = (datetime.datetime.strptime(now_time, "%H:%M") + datetime.timedelta(minutes=10)).strftime("%H:%M")
    
    if isBirthday(num_today):
        logging.info("HAPPY BIRTHDAY TO YOU!!!")
    pass

    if str_today not in ["Saturday", "Sunday"]:
        logging.info(f"WEEKDAYS:{str_today} KEEP RUNNING")
        if now_time in TIMETABLE[str_today] and now_time not in notified_times:
            subject = TIMETABLE[str_today][now_time]
            toaster.show_toast(
                f"{str_today} Class Notification",
                f"Next Class: {subject}",
                duration=None,
                threaded=True,
            )
            logging.info(f"{str_today} | {now_time} | {subject}")
            notified_times.add(now_time)
            
        if end_time == "8:30":
            logging.info("endTime 8:30 pass")
            continue
        elif end_time in TIMETABLE[str_today] and end_time not in notified_times:
            toaster.show_toast(
                f"{str_today} Class Notification",
                f"10 minutes before the end of class",
                duration=None,
                threaded=True,
            )
            logging.info(f"{str_today} | {now_time} | {subject}")
            notified_times.add(end_time)
            
        time.sleep(1)
        continue
    else:
        logging.info(f"WEEKEND:{str_today} KEEP RUNNING")
        time.sleep(1)
        continue
            