import os
import sys
import time
import json
import shutil
import logging
import datetime
import requests
import threading
import subprocess
import win32com.client
from pathlib import Path
from win10toast import ToastNotifier
from logging.handlers import TimedRotatingFileHandler

# 토스터 객체 생성
toaster = ToastNotifier()

# 테스트 변수
is_weak, is_test = True, False

# global 변수
notified_times = set()
yesterday = None
is_activated = False

# 상대경로
FUNCTION_DIR = Path(__file__).resolve().parent
BASE_DIR = FUNCTION_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"


# 프로그램 실행 검사 함수
def program_running_check(isTest:bool=is_test):
    """프로그램 실행 검사 함수

    Args:
        isTest (bool, optional): 테스트 인자. Defaults to isTest.
    """
    check_time = 0
    program_name = get_json_data(jsonFileName="etcData.json", rootKey="PROGRAM_DATA", subKey="PROGRAM_NAME")
    
    make_log_folder() # 로그 생성 함수
    
    if isTest == True:
        toaster_func(
            title="isTest is True",
            comment="now, Test Mode",
        )
        push_notification(title="This is Test Mode", comment="test mode")
        logging_func(title="programRunningCheck", comment="TEST MODE")
        
        log_thread = threading.Thread(target=watchLogFunc, args=(True), daemon=True)
        log_thread.start()
        
        return True
    
    for program in program_name:
        logging_func(title="programRunningCheck", comment="···")
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\cimv2")
        process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{program}'")
        if len(process_list) > 0:
            toaster_func(
                title="😀 Hello!",
                comment="Timetable is Running!\nNice to meet you :)",
            )
            push_notification(title="😀 Hello", comment="Timetable is Running! Nice to meet you")
            logging_func(title="programRunningCheck", comment="GOOD")
            break
        else:
            check_time += 1
            if check_time == len(program_name):
                toaster_func(
                    title="🤯 What?!",
                    comment="oh No.. bad news..\nsomething went wrong.. :(",
                )
                push_notification(title="🤯 What?!", comment="oh No.. bad news..\nsomething went wrong.. :(")
                logging_func(title="programRunningCheck", comment="FAILED")
                exitProgramFunc()


# 로그 생성 함수
def make_log_folder(isTest=is_test):
    """로그 생성 함수

    Args:
        isTest (bool, optional): 테스트 인자. Defaults to isTest.
    """
    
    log_folder = "logs"
    
    if isTest:
        shutil.rmtree(log_folder, ignore_errors=True)
        logging_func(title="makeLogFolder", comment="TEST MODE")
    
    os.makedirs(log_folder, exist_ok=True)
    
    log_file = os.path.join(log_folder, "app.log")
    
    logger = logging.getLogger()
    logger.handlers.clear()
    
    handler = TimedRotatingFileHandler(
        log_file, when="D", interval=1, backupCount=7, encoding="utf-8"
    )

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[handler]
    )
    
    logging_func(title="makeLogFolder", comment="SUCCESS")


# 알림 함수
def notify_func(title:str, message:str, time:str, notifiedTimes:set):
    """알림 함수

    Args:
        title (str): 제목
        message (str): 내용
        timeKey (str): 시간
        notifiedTimes (set): notifiedTimes 변수
    """
    
    if time not in notifiedTimes:
        toaster_func(title=title, comment=message)
        push_notification(title=title, comment=message)
        logging_func(title="notified", comment=f"{title} | {time}")
        notifiedTimes.add(time)


# 오늘 날짜, 요일, 시간을 반환하는 함수
def today_variable(isTest:bool=is_test):
    """오늘 날짜, 요일, 시간을 반환하는 함수

    Args:
        isTest (bool, optional): 테스트 인자.

    Returns:
        allReturns: numToday(MM-DD), txtToday(Monday), nextTime(HH:MM) 날짜, 요일, 시간을 str로 반환
    """
    
    today = datetime.datetime.today()
    
    if isTest:
        return "03-22", "Monday", "09:30"

    num_today = today.strftime("%m-%d")
    txt_today = today.strftime("%A")
    next_time = (today + datetime.timedelta(minutes=10)).strftime("%H:%M")
    
    return num_today, txt_today, next_time


# 하루가 지나면 특정 변수를 초기화 하는 함수
def reset_variable(today:str):
    """하루가 지나면 특정 변수를 초기화 하는 함수

    Args:
        today (str): 오늘 날짜

    Returns:
        bool: 다른 날이면 True를 같은 날이면 False를 반환
    """
    
    global yesterday
    
    if yesterday == None:
        yesterday = today
        return False
    
    if yesterday != today:
        yesterday = today
        return True
    else:
        return False


# 주말인지 주중인지 확인하는 함수
def is_weekday(today:str, isTest:bool=is_test, isWeek:bool=is_weak):
    """오늘이 주말인지 주중인지 확인하는 함수

    Args:
        today (str): 오늘 날짜
        isTest (bool, optional): 테스트 인자. Defaults to isTest.
        isWeek (bool, optional): 테스트 인자 주말 주중 선택. Defaults to isWeek.

    Returns:
        bool: 주말이면 True를 주말이면 False를 반환
    """

    if isTest:
        return isWeek
    return today not in ["Saturday", "Sunday"]


# 단축 수업 함수
def is_shortened(): 
    """단축 수업 함수

    Returns:
        bool: !isActicated
    """
    
    global is_activated
    is_activated = not is_activated
    return is_activated


# 월수금 확인 함수
def is_mwf(today:str):
    """오늘이 월수금 인지 확인해주는 함수

    Args:
        today (str): 오늘 요일을 받아옴

    Returns:
        bool: 오늘이 월수금이면 True를 아니면 False를 반환
    """
    if today in ["Monday", "Wednesday", "Friday"]:
        return True
    else:
        return False


# 생일 확인 함수
def is_birthday(today:str, oneNotified:set):
    """오늘이 생일인지 확인해주는 함수

    Args:
        today (str): 오늘 날짜
        oneNotified (set): set 변수
    """
    
    all_user_data = get_json_data("etcData.json")
    
    if today == all_user_data["USER_DATA"]["BIRTHDAY"] and today not in oneNotified:
        logging_func(title="isBirthday",comment="HAPPY BIRTHDAY TO YOU!!!")
        toaster_func(title="HAPPY BIRTHDAY TO YOU!!!", comment="Today is your birthday!!🎂")
        push_notification(message="HAPPY BIRTHDAY TO YOU!!!\nToday is your birthday!!🎂")
        oneNotified.add(today)


# assets 상대경로 반환 함수
def assets_dir_func(fileName:str):
    """assets 상대경로 함수

    Args:
        fileName (str): 파일 이름.

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    
    return str(ASSETS_DIR / fileName)


# data 상대경로 반환 함수
def data_dir_func(fileName:str):
    """data 상대경로 함수

    Args:
        fileName (str): 파일 이름.

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    return str(DATA_DIR / fileName)


# json 데이터 반환 함수
def get_json_data(jsonFileName: str, rootKey: str = None, subKey: str = None, needPath: bool = False):
    """JSON 데이터를 반환하는 함수

    Args:
        jsonFileName (str): JSON 파일 이름
        rootKey (str, optional): 루트 키. Defaults to None.
        subKey (str, optional): 서브 키. Defaults to None.
        needPath (bool, optional): 파일 경로 필요 여부. Defaults to False.

    Returns:
        result or (result, JSONDATA_PATH): 요청된 JSON 데이터 또는 파일 경로 포함한 튜플
    """

    if getattr(sys, 'frozen', False):  
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")

    JSONDATA_PATH = os.path.join(base_path, "data", jsonFileName)

    if not os.path.exists(JSONDATA_PATH):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {JSONDATA_PATH}")

    with open(JSONDATA_PATH, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    if rootKey is None:
        result = json_data
    elif subKey is None:
        result = json_data.get(rootKey, None)
    else:
        result = json_data.get(rootKey, {}).get(subKey, None)

    return (result, JSONDATA_PATH) if needPath else result


# toaster 함수
def toaster_func(title:str="", comment:str="", duration:int=3, threaded:bool=True, iconPath:str=None):
    """toaster 함수

    Args:
        title (str): 제목
        comments (str): 내용용
        duration (int, optional): 지속시간. Defaults to None.
        threaded (bool, optional): 스레드. Defaults to True.
    """
    
    toaster.show_toast(
            f"{title}",
            f"{comment}",
            duration=duration,
            threaded=threaded,
            icon_path=iconPath
        )


# 로깅 함수
def logging_func(title:str, comment:str, level:str="info"):
    """logging 함수

    Args:
        level (str, optional): 로그 레벨. Defaults to "info".
        title (str): 제목
        comment (str): 내용
    """
    
    if level == "info":
        logging.info("{:<25}: {}".format(title, comment))
    elif level == "debug":
        logging.debug("{:<25}: {}".format(title, comment))


# 폰으로 알림 보내는 함수
def push_notification(title:str, comment:str):
    """폰으로 알림 보내는 함수

    Args:
        message (str): 폰으로 보낼 메세지
    """
    comments = f"{title}\n{comment}"
    requests.post(f"https://ntfy.sh/Timetable", data=comments.encode("utf-8"))
    logging_func(title="pushNotification", comment="SUCCESE")


# 시간표 시간을 교시로 반환하는 함수
def convert_timetable(timetable):
    """시간표 시간을 교시로 변환해주는 함수

    Args:
        timetable (dict): 시간표

    Returns:
        시간표: 교시로 변환된 시간표
    """
    converted = {}
    
    for day, schedule in timetable.items():
        sorted_times = sorted(schedule.keys())  # 시간을 순서대로 정렬
        converted_schedule = {f"{i+1}교시": schedule[time] for i, time in enumerate(sorted_times)}
        converted[day] = converted_schedule
    
    return converted


# 프로그램 종료 함수
def exitProgramFunc():
    """프로그램 종료 함수"""
    logging_func(title="program", comment="OFF")
    logging.shutdown()
    sys.exit()


# 실시간 로그 확인 함수
def watchLogFunc(isTest:bool=is_test):
    """실시간 로그 확인 함수

    Args:
        isTest (bool, optional): 테스트 인자. Defaults to isTest.
    """
    if isTest:
        logging_func(title="isWeekday", comment="TEST MODE")
        logging_func(title="todayVariable", comment="TEST MODE")
        cmd = ["powershell", "-Command", "Get-Content logs/app.log -Wait"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            for line in process.stdout:
                print(line, end="")
        except KeyboardInterrupt:
                process.terminate()


# 알림 함수
def notificationFunc():
    all_Timetable = get_json_data(jsonFileName="mainData.json")
    basic_timetable, breaktime = all_Timetable["BASIC_TIMETABLE"], all_Timetable["BREAKTIME"]
    while True:
        # 오늘 날짜, 요일, 시간 불러오기
        num_today, txt_today, next_time = today_variable()
        
        # notifiedTime 변수 초기화 ( 하루가 지날때만 )
        if reset_variable(txt_today):
            notified_times.clear()
        
        # 생일 확인 함수
        is_birthday(num_today, notified_times)
        
        # 주말 주중 확인 함수
        if is_weekday(txt_today):
            if next_time in basic_timetable[txt_today]:
                notify_func(title=f"{txt_today} Class Notification",
                    message=f"Next Class: {basic_timetable[txt_today][next_time]}",
                    time=next_time,
                    notifiedTimes=notified_times)
            breakKey = "MWF" if is_mwf(txt_today) else "TT"
            if next_time in breaktime[breakKey]:
                notify_func(title=f"{txt_today} Break Notification",
                    message=f"10 minutes left until the {breaktime[breakKey][next_time]}",
                    time=next_time,
                    notifiedTimes=notified_times)
            logging_func(title="weekdays", comment=f"{txt_today} KEEP RUNNING")
        else:
            logging_func(title="weekends", comment=f"{txt_today} KEEP RUNNING")
        
        time.sleep(1)