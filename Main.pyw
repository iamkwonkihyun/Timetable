import time
import datetime
import logging
import os
import win32com.client
import sys
import shutil
from win10toast import ToastNotifier
from data.data import TIMETABLE, KOR_DAYS, BREAK_TIME

#DEBUG: 디버깅 정보
#INFO: 프로그램 시작
#WARNING: 메모리 부족
#ERROR: 파일을 찾을 수 없음
#CRITICAL: 시스템 장애!

programName = "pyw.exe"


if os.path.exists("logs"):
    shutil.rmtree("logs")
if not os.path.exists("logs"):
    os.makedirs("logs")

    
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logging.info("start program")

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

# 오늘 날짜 영어로 불러오기 ex) Monday
today = datetime.datetime.today().strftime("%A")

today_kor = KOR_DAYS[today]

notified_times = set()

# timetable에 today_kor이 포함되어 있으면 코드 실행
if today_kor in TIMETABLE:
    while True:
        logging.info("KEEP RUNNING")
        now = datetime.datetime.now().strftime("%H:%M") # 현재 시간 구해서 변수로
        if now in TIMETABLE[today_kor] and now not in notified_times: # 현재 시간에 timetable[today_kor]에 있으면 아래 코드 실행
            subject = TIMETABLE[today_kor][now] # 현재 시간의 과목 가져오기
            toaster.show_toast(
                f"{today_kor} class notification",
                f"next class: {subject}",
                duration=None,
                threaded=True,
            )
            logging.info(f"{today} | {now} | {subject}")
            notified_times.add(now)
            
        strp_now = datetime.datetime.strptime(now, "%H:%M") + datetime.timedelta(minutes=10)
        endTime = strp_now.strftime("%H:%M")
        if endTime == "8:30":
            logging.info("endTime 8:30 pass")
            continue
        elif endTime in TIMETABLE[today_kor] and endTime not in notified_times:
            toaster.show_toast(
                f"{today_kor} class notification",
                f"10 minutes before the end of class",
                duration=None,
                threaded=True,
            )
            logging.info(f"{today} | {now} | {subject}")
            notified_times.add(endTime)
            
        time.sleep(1) # 1초마다 확인
elif today_kor not in TIMETABLE:
    while True:
        logging.info(f"weekend: {today}")
        time.sleep(86400)
