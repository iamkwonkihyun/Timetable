import os
import sys
import time
import json
import shutil
import logging
import datetime
import requests
import win32com.client
from dotenv import load_dotenv
from pathlib import Path
from win10toast import ToastNotifier
from logging.handlers import TimedRotatingFileHandler

# .env 불러오기
load_dotenv()

# 키값
API_KEY = os.getenv("NEIS_API_KEY")

# base url
base_url = "https://open.neis.go.kr/hub/hisTimetable"

# 토스터 객체 생성
toaster = ToastNotifier()

# 테스트 변수
is_weak, is_test = True, True

# global 변수
notified_times = set()
yesterday = None
is_activated = False

# 상대경로
FUNCTION_DIR = Path(__file__).resolve().parent
BASE_DIR = FUNCTION_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"


def get_api_func(key = API_KEY):
    ymd, _, _, _ = today_variable()
    
    period_to_time = {
        "1": "08:40",
        "2": "09:40",
        "3": "10:40",
        "4": "11:40",
        "5": "13:20",
        "6": "14:20",
        "7": "15:20"
    }
    
    # 파라미터를 딕셔너리로 정리
    params = {
        "KEY": key,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": "B10",         # 교육청 코드
        "SD_SCHUL_CODE": "7010911",          # 학교 코드
        "DDDEP_NM": "클라우드보안과",         # 학과명
        "GRADE": 3,
        "CLASS_NM": 2,
        "sem": 1,                           # 학기
        "AY": 2025,                         # 학년도
        "ALL_TI_YMD": ymd
    }
    
    # ( try, except로 혹시 모를 문제 예방하기 )
    
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        
        # 시간별 과목 딕셔너리 생성
        timetable = {
            period_to_time[row["PERIO"]]: row["ITRT_CNTNT"]
            for row in data["hisTimetable"][1]["row"]
            if row["PERIO"] in period_to_time
        }

        # 저장
        with open(data_dir_func("api_timetable.json"), "w", encoding="utf-8") as f:
            json.dump(timetable, f, ensure_ascii=False, indent=4)


# 프로그램 실행 검사 함수
def program_running_check(test: bool = is_test):
    """프로그램 실행 검사 및 로그 폴더 생성 함수

    Args:
        test (bool, optional): 테스트 인자.

    Returns:
        bool: 테스트 중이거나 program이 실행중이면 True를 반환
    """
    
    check_time = 0
    log_folder = "logs"
    program_name = get_json_data(json_file_name="etc_data.json", root_key="PROGRAM_DATA", sub_key="PROGRAM_NAME")
    
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
    
    if test:
        alert_func(
            title="isTest is True",
            comment="now, Test Mode",
        )
        
        shutil.rmtree(log_folder, ignore_errors=True)
        
        return True
    
    for program in program_name:
        
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\cimv2")
        process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{program}'")
        
        logging_func(title="programRunningCheck", comment="···")
        
        if len(process_list) > 0:
            alert_func(
                title="😀 Hello!",
                comment="Timetable is Running!\nNice to meet you :)"
            )
            logging_func(title="programRunningCheck", comment="GOOD")
            return True
        else:
            check_time += 1
            if check_time == len(program_name):
                alert_func(
                    title="🤯 What?!",
                    comment="oh No.. bad news..\nsomething went wrong.. :(",
                )
                logging_func(title="programRunningCheck", comment="FAILED")
                exit_program_func()


# 알림 함수
def notify_func(title: str, message: str, time: str, notified_times: set):
    """알림 함수

    Args:
        title (str): 제목
        message (str): 내용
        timeKey (str): 시간
        notified_times (set): notified_times 변수
    """
    
    if time not in notified_times:
        alert_func(title=title, comment=message)
        logging_func(title="notified", comment=f"{title} | {time}")
        notified_times.add(time)


# 오늘 날짜, 요일, 시간을 반환하는 함수
def today_variable(test: bool = is_test):
    """오늘 날짜, 요일, 시간을 반환하는 함수

    Args:
        isTest (bool, optional): 테스트 인자.

    Returns:
        allReturns: numToday(MM-DD), txtToday(Monday), nextTime(HH:MM) 날짜, 요일, 시간을 str로 반환
    """
    
    today = datetime.datetime.today()
    
    if test:
        return "20250531","03-22", "Monday", "09:30"

    ymd_today = today.strftime("%y%m%d")
    num_today = today.strftime("%m-%d")
    txt_today = today.strftime("%A")
    next_time = (today + datetime.timedelta(minutes=10)).strftime("%H:%M")
    
    return ymd_today, num_today, txt_today, next_time


# 하루가 지나면 특정 변수를 초기화 하는 함수
def reset_function(today:str):
    """하루가 지나면 모든 상태를 초기화 하는 함수

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
def is_weekday(today: str, test: bool = is_test, is_week: bool = is_weak):
    """오늘이 주말인지 주중인지 확인하는 함수

    Args:
        today (str): 오늘 날짜
        isTest (bool, optional): 테스트 인자. Defaults to isTest.
        isWeek (bool, optional): 테스트 인자 주말 주중 선택. Defaults to isWeek.

    Returns:
        bool: 주말이면 True를 주말이 아니면 False를 반환
    """

    if test:
        return is_week
    return today not in ["Saturday", "Sunday"]


# 단축 수업 함수
def is_shortened(): 
    """단축 수업 함수

    Returns:
        bool: !is_acticated
    """
    
    global is_activated
    is_activated = not is_activated
    return is_activated


# 월수금 확인 함수
def is_mwf(today: str):
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
def is_birthday(today: str, one_notified: set):
    """오늘이 생일인지 확인해주는 함수

    Args:
        today (str): 오늘 날짜
        one_notified (set): set 변수
    """
    
    all_user_data = get_json_data("etc_data.json")
    
    if today == all_user_data["USER_DATA"]["BIRTHDAY"] and today not in one_notified:
        logging_func(title="isBirthday",comment="HAPPY BIRTHDAY TO YOU!!!")
        alert_func(title="HAPPY BIRTHDAY TO YOU!!!", comment="Today is your birthday!!🎂")
        one_notified.add(today)


# assets 상대경로 반환 함수
def assets_dir_func(file_name:str):
    """assets 상대경로 함수

    Args:
        fileName (str): 파일 이름.

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    
    return str(ASSETS_DIR / file_name)


# data 상대경로 반환 함수
def data_dir_func(file_name:str):
    """data 상대경로 함수

    Args:
        fileName (str): 파일 이름.

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    return str(DATA_DIR / file_name)


# json 데이터 반환 함수
def get_json_data(json_file_name: str, root_key: str = None, sub_key: str = None, need_path: bool = False):
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

    JSON_DATA_PATH = os.path.join(base_path, "data", json_file_name)

    if not os.path.exists(JSON_DATA_PATH):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {JSON_DATA_PATH}")

    with open(JSON_DATA_PATH, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    if root_key is None:
        result = json_data
    elif sub_key is None:
        result = json_data.get(root_key, None)
    else:
        result = json_data.get(root_key, {}).get(sub_key, None)

    return (result, JSON_DATA_PATH) if need_path else result


# alert 함수
def alert_func(title: str, comment: str, duration: int = 3, threaded: bool = True, icon_path: str = None):
    """알림 함수

    Args:
        title (str): 제목
        comment (str): 내용
        duration (int, optional): 지속 시간. Defaults to 3.
        threaded (bool, optional): 스레딩. Defaults to True.
        icon_path (str, optional): 아이콘 경로. Defaults to None.
    """
    
    # 토스터
    toaster.show_toast(
            f"{title}",
            f"{comment}",
            duration=duration,
            threaded=threaded,
            icon_path=icon_path
        )
    
    # ntfy
    comments = f"{title}\n{comment}"
    requests.post(f"https://ntfy.sh/Timetable", data=comments.encode("utf-8"))


# 로깅 함수
def logging_func(title: str, comment: str, level: str = "info"):
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
def exit_program_func():
    """프로그램 종료 함수"""
    logging_func(title="program", comment="OFF")
    logging.shutdown()
    sys.exit()


# 알림 함수
def notification_func():
    today_timetable = get_json_data(json_file_name="api_timetable.json")
    
    all_Timetable = get_json_data(json_file_name="timetable.json")
    breaktime = all_Timetable["BREAKTIME"]
    
    while True:
        # 오늘 날짜, 요일, 시간 불러오기
        _, num_today, txt_today, next_time = today_variable()
        
        # notifiedTime 변수 초기화 ( 하루가 지날때만 )
        if reset_function(txt_today):
            get_api_func()
            notified_times.clear()
            
        # 생일 확인 함수
        is_birthday(num_today, notified_times)
        
        # 주말 주중 확인 함수
        if is_weekday(txt_today):
            if next_time in today_timetable[txt_today]:
                notify_func(title=f"{txt_today} Class Notification",
                    message=f"Next Class: {today_timetable[txt_today][next_time]}",
                    time=next_time,
                    notified_times=notified_times)
            break_key = "MWF" if is_mwf(txt_today) else "TT"
            if next_time in breaktime[break_key]:
                notify_func(title=f"{txt_today} Break Notification",
                    message=f"10 minutes left until the {breaktime[break_key][next_time]}",
                    time=next_time,
                    notified_times=notified_times)
            time.sleep(1)