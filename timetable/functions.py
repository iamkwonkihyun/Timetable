import datetime
import requests
import json
import locale
import logging
import os
import shutil
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from requests.exceptions import RequestException

import requests
import win32com.client
from dotenv import load_dotenv
from win10toast import ToastNotifier

# env 불러오기
load_dotenv()

# 한글화
locale.setlocale(locale.LC_TIME, "Korean_Korea.utf8")

# env값 불러오기
API_KEY = os.getenv("NEIS_API_KEY")
ATPT_OFCDC_SC_CODE = os.getenv("ATPT_OFCDC_SC_CODE")
SD_SCHUL_CODE = os.getenv("SD_SCHUL_CODE")

# api url
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

# etc
BIRTHDAY = "03-09"
PROGRAM_NAME_LIST = ["pyw.exe", "pythonw.exe", "py.exe", "python.exe"]

# 재시도 함수
def get_with_retry(url, params, retries=3, delay=2):
    """네트워크 오류 발생 시 재시도 요청 함수"""
    for i in range(retries):
        try:
            return requests.get(url, params=params, timeout=5)
        except RequestException as e:
            logging_func("get_with_retry", f"retry {i+1}/{retries} failed: {e}")
            time.sleep(delay)
    raise Exception(f"Failed to connect to {url} after {retries} retries.")


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
        return "20250623" if api else "2025년 06월 23일","03-22", "Monday", "09:30"

    ymd = today.strftime("%Y%m%d") if api else today.strftime("%Y년 %m월 %d일")
    num = today.strftime("%m-%d")
    txt = today.strftime("%A")
    next_time = (today + datetime.timedelta(minutes=10)).strftime("%H:%M")
    
    return ymd, num, txt, next_time


# 시간표 api 받아오는 함수
def get_api_func(key: str = API_KEY) -> bool:
    """시간표, 급식 API 받아오는 함수"""
    
    ymd, _, _, _ = today_variable(api=True)
    
    meal_list = {}
    
    meal_api_params = {
        "KEY": key,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,
        "MLSV_YMD": ymd
    }
    
    timetable_api_params = {
        "KEY": key,
        "Type": "json",
        "pIndex": 1,
        "pSize": 100,
        "ATPT_OFCDC_SC_CODE": ATPT_OFCDC_SC_CODE,
        "SD_SCHUL_CODE": SD_SCHUL_CODE,
        "DDDEP_NM": "클라우드보안과",
        "GRADE": 3,
        "CLASS_NM": 2,
        "sem": 1,
        "AY": 2025,
        "ALL_TI_YMD": ymd
    }
    
    period_to_time = {
        "1": "08:40",
        "2": "09:40",
        "3": "10:40",
        "4": "11:40",
        "5": "13:20",
        "6": "14:20",
        "7": "15:20"
    }
    
    try:
        meal_api_response = get_with_retry(MEAL_URL, meal_api_params)
        
        if meal_api_response.status_code != 200:
            logging_func("get_api_func", "meal HTTP failed")
            return False
        
        meal_api_data = meal_api_response.json()
        
        try:
            meal_api_result_code = meal_api_data["mealServiceDietInfo"][0]["head"][1]["RESULT"]["CODE"]
        except (KeyError, IndexError):
            logging_func("get_meal_api_func", "wrong_value")
            return False
        
        if meal_api_result_code == "INFO-000":
            rows = meal_api_data["mealServiceDietInfo"][1]["row"]
            for row in rows:
                menu = row.get("DDISH_NM", "").replace("<br/>", ",")
                meal_list["중식"] = menu

            with open(data_dir_func("api_meal.json"), "w", encoding="utf-8") as f:
                json.dump(meal_list, f, ensure_ascii=False, indent=4)

            logging_func("get_meal_api_func", "success")
        else:
            logging_func("get_meal_api_func", f"API returned result code: {meal_api_result_code}")
            return False
    except Exception as e:
        # DNS 관련 에러 메시지를 구분해서 로깅
        if "getaddrinfo failed" in str(e):
            logging_func("get_api_func", "DNS 해석 실패: open.neis.go.kr")
        else:
            logging_func("get_api_func", f"exception: {str(e)}")
        return False
    
    try:
        timetable_api_response = get_with_retry(TIMETABLE_URL, timetable_api_params)
        
        if timetable_api_response.status_code != 200:
            logging_func("get_api_func", "timetable HTTP failed")
            return False
        
        timetable_api_data = timetable_api_response.json()
        
        try:
            timetable_api_result_code = timetable_api_data["hisTimetable"][0]["head"][1]["RESULT"]["CODE"]
        except (KeyError, IndexError):
            logging_func("get_api_func", "wrong_value")
            return False
        
        if timetable_api_result_code == "INFO-000":
            timetable = {
                period_to_time[row["PERIO"]]: row["ITRT_CNTNT"]
                for row in timetable_api_data["hisTimetable"][1]["row"]
                if row["PERIO"] in period_to_time
            }
            with open(data_dir_func("api_timetable.json"), "w", encoding="utf-8") as f:
                json.dump(timetable, f, ensure_ascii=False, indent=4)

            logging_func("get_api_func", "success")
            return True
        else:
            logging_func("get_api_func", f"timetable failed with result code: {timetable_api_result_code}")
            return False
    except Exception as e:
        if "getaddrinfo failed" in str(e):
            logging_func("get_api_func", "DNS 해석 실패: open.neis.go.kr")
        else:
            logging_func("get_api_func", f"exception: {str(e)}")
        return False

# 프로그램 실행 검사 함수
def program_running_check(test: bool = is_test) -> bool | None:
    """프로그램 실행 확인 함수

    Args:
        test (bool, optional): 테스트 인자. Defaults to is_test.

    Returns:
        bool: 실행중이면 True, 아니면 프로그램 강제 종료 
    """
    check_time = 0
    log_folder_path = "logs"
    data_folder_path = "data"
    
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
        get_api_func()
        
        shutil.rmtree(log_folder_path, ignore_errors=True)
        
        alert_func(title="테스트 모드 알림", comment="테스트 모드입니다")
        
        return True
    
    logging_func(title="programRunningCheck", comment="···")
    
    for program in PROGRAM_NAME_LIST:
        
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\cimv2")
        process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{program}'")
        
        if len(process_list) > 0:
            alert_func(
                title="😀 안녕하세요!",
                comment="Timetable이 실행중입니다!\n만나서 반가워요!"
            )
            logging_func(title="programRunningCheck", comment="GOOD")
            return True
        else:
            check_time += 1
            if check_time == len(PROGRAM_NAME_LIST):
                alert_func(
                    title="🤯 음??!!",
                    comment="이런.. 안 좋은 소식이 있어요..\n프로그램에 무슨 문제가 있나봐요..",
                )
                logging_func(title="programRunningCheck", comment="FAILED")
                exit_program_func()


# 알림 함수
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
        duration (int, optional): 지속 시간.
        threaded (bool, optional): 스레딩.
        icon_path (str, optional): 아이콘 경로.
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


# 쉬는 시간, 다음 교시 과목 알림 함수 (alert 함수랑 다름)
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
    
    if yesterday == None:
        logging_func(title="is_yesterday", comment=f"{yesterday} | {today}")
        return True
    
    if yesterday != None and yesterday != today:
        logging_func(title="is_yesterday", comment=f"{yesterday} | {today}")
        return True
    
    return False


# 생일 확인 함수
def is_birthday(today: str, notified_times: set[str]) -> None:
    """오늘이 생일인지 확인해주는 함수

    Args:
        today (str): 오늘 날짜
    """
    
    if today == BIRTHDAY and today not in notified_times:
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
def get_json_data(json_file_name: str) -> dict[str, str]:
    
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
    
    return json_data


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


# 실질적 main 함수
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
        if is_yesterday(today=txt_today, yesterday=yesterday):
            yesterday = txt_today
            
            # notified_times 변수 초기화
            notified_times.clear()
            
            # 시간표 갱신
            get_api_func()
            
            # 생일 확인 함수
            if is_birthday(num_today, notified_times):
                notified_times.add(num_today)

        # 주말 주중 확인 함수
        if txt_today not in ["토요일", "일요일"]:
            
            # 다음 교시 과목 알려주는 로직
            if next_time in today_timetable and next_time not in notified_times:
                notify_func(title=f"{txt_today} 과목 알림",
                    message=f"다음 교시 과목: {today_timetable[next_time]}",
                    time=next_time)
                notified_times.add(next_time)
            
            # 쉬는 시간 10분 전 알림 보내는 로직
            break_key = "MWF" if txt_today in ["Monday", "Wednesday", "Friday"] else "TT"
            if next_time in breaktime[break_key] and next_time not in notified_times:
                notify_func(title=f"{txt_today} 쉬는 시간 알림",
                    message=f"{breaktime[break_key][next_time]} 쉬는 시간까지 10분 남았습니다",
                    time=next_time)
                notified_times.add(next_time)
            
            time.sleep(1)


# - - - - - - 소멸된 함수들 - - - - - - -

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


# # 월수금 확인 함수
# def is_mwf(today: str) -> bool:
#     """오늘이 월수금 인지 확인해주는 함수

#     Args:
#         today (str): 오늘 요일을 받아옴

#     Returns:
#         bool: 오늘이 월수금이면 True를 아니면 False를 반환
#     """
#     if today in ["Monday", "Wednesday", "Friday"]:
#         return True
#     else:
#         return False