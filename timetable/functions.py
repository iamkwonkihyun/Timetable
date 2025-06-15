import os
import sys
import time
import json
import shutil
import logging
import datetime
import requests
import win32com.client
from pathlib import Path
from dotenv import load_dotenv
from win10toast import ToastNotifier
from logging.handlers import TimedRotatingFileHandler

# env 불러오기
load_dotenv()

# 키 변수
API_KEY = os.getenv("NEIS_API_KEY")

# base url 변수
TIMETABLE_URL = "https://open.neis.go.kr/hub/hisTimetable"
MEAL_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo"

# 토스터 객체 생성
toaster = ToastNotifier()

# 테스트 변수
is_test = False

# 상대경로 변수
timetable_dir = Path(__file__).resolve().parent
base_dir = timetable_dir.parent
assets_dir = base_dir / "assets"
data_dir = base_dir / "data"


# 오늘 날짜, 요일, 시간을 반환하는 함수
def today_variable(test: bool = is_test, api: bool = False) -> str:
    """오늘 날짜, 요일, 시간을 반환하는 함수

    Args:
        isTest (bool, optional): 테스트 인자.

    Returns:
        allReturns: numToday(MM-DD), txtToday(Monday), nextTime(HH:MM) 날짜, 요일, 시간을 str로 반환
    """
    
    today = datetime.datetime.today()
    
    if test:
        return "20250613","03-22", "Monday", "09:30"

    ymd = today.strftime("%y%m%d") if api else today.strftime("%Y년 %m월 %d일")
    num = today.strftime("%m-%d")
    txt = today.strftime("%A")
    next_time = (today + datetime.timedelta(minutes=10)).strftime("%H:%M")
    
    return ymd, num, txt, next_time


def get_meal_api_func(key: str = API_KEY) -> bool:
    ymd, _, _, _ = today_variable(api=True)
    
    params = {
        "KEY": key,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": "B10",     # 서울시교육청
        "SD_SCHUL_CODE": "7010911",       # 한세사이버보안고등학교
        "MLSV_YMD" : ymd
    }

    try:
        response = requests.get(MEAL_URL, params=params)
        if response.status_code != 200:
            logging_func("get_meal_api_func", "HTTP failed")
            return False

        data = response.json()

        # 응답 결과 코드 확인
        try:
            result_code = data["mealServiceDietInfo"][0]["head"][1]["RESULT"]["CODE"]
        except (KeyError, IndexError):
            logging_func("get_meal_api_func", "wrong_value")
            return False

        if result_code == "INFO-000":
            rows = data["mealServiceDietInfo"][1]["row"]
            meal_info = {}

            for row in rows:
                date = row.get("MLSV_YMD")
                meal_type = row.get("MMEAL_SC_NM")  # 조식, 중식, 석식 중 선택
                menu = row.get("DDISH_NM", "").replace("<br/>", ",")
                
                if date not in meal_info:
                    meal_info[date] = {}

                meal_info[date][meal_type] = menu

            # JSON 파일로 저장
            with open(data_dir_func("meal.json"), "w", encoding="utf-8") as f:
                json.dump(meal_info, f, ensure_ascii=False, indent=4)

            logging_func("get_meal_api_func", "succeeded")
            return True
        else:
            logging_func("get_meal_api_func", f"failed: {result_code}")
            return False

    except Exception as e:
        logging_func("get_meal_api_func", f"exception: {str(e)}")
        return False


def get_timetable_api_func(key: str = API_KEY) -> bool:
    """시간표 api 받아오는 함수

    Args:
        key (str, optional): api 키값. Defaults to API_KEY.
    """
    
    ymd, _, _, _ = today_variable(api=True)
    
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
    
    response = requests.get(TIMETABLE_URL, params=params)
    
    if response.status_code == 200:
        data = response.json()

        # 응답의 RESULT 코드 확인
        try:
            result_code = data["hisTimetable"][0]["head"][1]["RESULT"]["CODE"]
        except (KeyError, IndexError):
            logging_func(title="get_api_func", comment="wrong_value")
            return False

        if result_code == "INFO-000":
            timetable = {
            period_to_time[row["PERIO"]]: row["ITRT_CNTNT"]
            for row in data["hisTimetable"][1]["row"]
            if row["PERIO"] in period_to_time
            }
            with open(data_dir_func("api_timetable.json"), "w", encoding="utf-8") as f:
                json.dump(timetable, f, ensure_ascii=False, indent=4)
            logging_func(title="get_api_func", comment="succesed")
            return True
        elif result_code == "INFO-200":
            logging_func(title="get_api_func", comment="failed")
            return False
        else:
            logging_func(title="get_api_func", comment="failed")
            return False
    else:
        logging_func(title="get_api_func", comment="failed")
        return False


# 프로그램 실행 검사 함수
def program_running_check(test: bool = is_test) -> None:
    """프로그램 실행 확인 함수

    Args:
        test (bool, optional): 테스트 인자. Defaults to is_test.

    Returns:
        bool: 실행중이면 True, 아니면 프로그램 강제 종료 
    """
    check_time = 0
    log_folder_path = "logs"
    data_folder_path = "data"
    program_name = get_json_data(json_file_name="etc_data.json", root_key="PROGRAM_DATA", sub_key="PROGRAM_NAME")
    
    if not os.path.exists(log_folder_path):
        os.makedirs(log_folder_path, exist_ok=True)
    
    if not os.path.exists(data_folder_path):
        os.makedirs(data_folder_path, exist_ok=True)
        
    log_file = os.path.join(log_folder_path, "app.log")
    
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
        get_meal_api_func()
        get_timetable_api_func()
        
        alert_func(title="isTest is True", comment="now, Test Mode")
        
        shutil.rmtree(log_folder_path, ignore_errors=True)
        
        return True
    
    logging_func(title="programRunningCheck", comment="···")
    
    for program in program_name:
        
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\cimv2")
        process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{program}'")
        
        if len(process_list) > 0:
            alert_func(
                title="😀 Hello!",
                comment="Timetable is Running!\nNice to meet you :)"
            )
            logging_func(title="programRunningCheck", comment="GOOD")
            return True if get_timetable_api_func() and get_meal_api_func() else False
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
def notify_func(title: str, message: str, time: str) -> None:
    """알림 함수

    Args:
        title (str): 제목
        message (str): 내용
        time (str): 시간
    """
    alert_func(title=title, comment=message)
    logging_func(title="notified", comment=f"{title} | {time}")


# 하루가 지나면 특정 변수를 초기화 하는 함수
def is_yesterday(today: str, yesterday: str | None) -> bool:
    """하루가 지나면 상태 초기화 여부를 반환"""
    
    if yesterday is None:
        logging_func(title="is_yesterday", comment=f"{yesterday} | {today}")
        return False
    
    if yesterday != today and yesterday is not None:
        logging_func(title="is_yesterday", comment=f"{yesterday} | {today}")
        return True
    
    return False


# 월수금 확인 함수
def is_mwf(today: str) -> bool:
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
def is_birthday(today: str, notified_times: set[str]) -> None:
    """오늘이 생일인지 확인해주는 함수

    Args:
        today (str): 오늘 날짜
    """
    
    all_user_data = get_json_data("etc_data.json")
    
    if today == all_user_data["USER_DATA"]["BIRTHDAY"] and today not in notified_times:
        alert_func(title="HAPPY BIRTHDAY TO YOU!!!", comment="Today is your birthday!!🎂")


# assets 상대경로 반환 함수
def assets_dir_func(file_name: str) -> str:
    """assets 상대경로 함수

    Args:
        fileName (str): 파일 이름.

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    
    return str(assets_dir / file_name)


# data 상대경로 반환 함수
def data_dir_func(file_name: str) -> str:
    """data 상대경로 함수

    Args:
        fileName (str): 파일 이름.

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    return str(data_dir / file_name)


# json 데이터 반환 함수
def get_json_data(json_file_name: str,
    root_key: str | None = None,
    sub_key: str | None = None,
    need_path: bool = False
    ) -> tuple[str, dict[str, str]] | dict[str, str]:
    
    """
    JSON 파일에서 데이터를 가져옵니다.

    Args:
        json_file_name (str): 읽을 JSON 파일 이름
        root_key (str, optional): 루트 키
        sub_key (str, optional): 서브 키
        need_path (bool): 경로를 결과에 포함할지 여부

    Raises:
        FileNotFoundError: JSON 파일이 존재하지 않을 때 발생

    Returns:
        dict[str, str]: 파싱된 데이터
        또는 tuple[str, dict[str, str]]: need_path가 True일 경우 (파일 경로, 데이터)
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
def alert_func(
    title: str,
    comment: str,
    duration: int = 3,
    threaded: bool = True,
    icon_path: str | None = None,
    only_toast: bool = is_test
    ) -> None:
    
    """알림 함수

    Args:
        title (str): 제목
        comment (str): 내용
        duration (int, optional): 지속 시간. Defaults to 3.
        threaded (bool, optional): 스레딩. Defaults to True.
        icon_path (str, optional): 아이콘 경로. Defaults to None.
        only_toast (bool, optional): 토스터만 필요한지
    """
    toaster.show_toast(
            f"{title}",
            f"{comment}",
            duration=duration,
            threaded=threaded,
            icon_path=icon_path
        )
    if not only_toast:
        comments = f"{title}\n{comment}"
        requests.post(f"https://ntfy.sh/Timetable", data=comments.encode("utf-8"))


# 로깅 함수
def logging_func(title: str, comment: str, level: str = "info") -> None:
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


# 프로그램 종료 함수
def exit_program_func() -> None:
    """프로그램 종료 함수"""
    logging_func(title="program", comment="OFF")
    logging.shutdown()
    sys.exit()


# 시간표 시간을 교시로 반환하는 함수    
def convert_timetable(timetable: dict[str, str]) -> dict[str, str]:
    """시간표 시간을 교시로 변환해주는 함수

    Args:
        timetable (dict): 시간표

    Returns:
        시간표: 교시로 변환된 시간표
    """
    
    converted_schedule = {f"{i+1}교시": schedule for i, (_, schedule) in enumerate(timetable.items())}
    
    return converted_schedule


def timetable_func():
    today_timetable = get_json_data(json_file_name="api_timetable.json")
    all_Timetable = get_json_data(json_file_name="hard_timetable.json")
    breaktime = all_Timetable["BREAKTIME"]
    notified_times = set()
    yesterday = None
    
    while True:
        # 오늘 날짜, 요일, 시간 불러오기
        _, num_today, txt_today, next_time = today_variable()
        
        # notifiedTime 변수 초기화 ( 하루가 지날때만 )
        if is_yesterday(txt_today, yesterday):
            yesterday = txt_today
            
            # notified_times 변수 초기화
            notified_times.clear()
            
            # 시간표 갱신
            get_timetable_api_func()
            
            # 생일 확인 함수
            if is_birthday(num_today, notified_times):
                notified_times.add(num_today)

        # 주말 주중 확인 함수
        if txt_today not in ["Saturday", "Sunday"]:
            
            # 다음 교시 과목 알려주는 로직
            if next_time in today_timetable and next_time not in notified_times:
                notify_func(title=f"{txt_today} Class Notification",
                    message=f"Next Class: {today_timetable[next_time]}",
                    time=next_time)
                notified_times.add(next_time)
            
            # 쉬는 시간 10분 전 알림 보내는 로직
            break_key = "MWF" if is_mwf(txt_today) else "TT"
            if next_time in breaktime[break_key] and next_time not in notified_times:
                notify_func(title=f"{txt_today} Break Notification",
                    message=f"10 minutes left until the {breaktime[break_key][next_time]}",
                    time=next_time)
                notified_times.add(next_time)
            
            time.sleep(1)


# # 단축 수업 함수
# def is_shortened(): 
#     """단축 수업 함수

#     Returns:
#         bool: !is_acticated
#     """
    
#     global is_activated
#     is_activated = not is_activated
#     return is_activated


# # 주말인지 주중인지 확인하는 함수
# def is_weekday(today: str):
#     """오늘이 주말인지 주중인지 확인하는 함수

#     Args:
#         today (str): 오늘 날짜
#         isTest (bool, optional): 테스트 인자. Defaults to isTest.
#         isWeek (bool, optional): 테스트 인자 주말 주중 선택. Defaults to isWeek.

#     Returns:
#         bool: 주말이면 True를 주말이 아니면 False를 반환
#     """

#     return today not in ["Saturday", "Sunday"]