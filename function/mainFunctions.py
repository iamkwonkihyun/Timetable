import datetime, logging, json
from pathlib import Path
from win10toast import ToastNotifier

# 토스터 객체 생성
toaster = ToastNotifier()

# global 변수
yesterday = None
isActivated = False

# 상대경로
FUNCTION_DIR = Path(__file__).resolve().parent
BASE_DIR = FUNCTION_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

def todayVariable(isTest:bool=False):
    """오늘 요일, 시간 정보를 주는 함수
    
    Args:
        isTest (bool): 테스트 할 때
    
    Returns:
        all_returns(str): 오늘 요일, 날짜, 끝나는 시간 등 반환
        
        num_today = "MM-DD", txt_today = "Monday", now_time  = "HH:MM", end_time  = "HH:MM" + 10 minutes
    """
    
    today = datetime.datetime.today()
    
    if isTest:
        loggingFunc(title="todayVariable", comment="TEST MODE")
        logging.info("todayVariable  : TEST MODE")
        num_today = "03-11"
        txt_today = "Monday"
        now_time = "12:2"
        end_time = "08:40"
        return num_today, txt_today, now_time, end_time
    else:
        num_today = today.strftime("%m-%d")
        txt_today = today.strftime("%A")
        now_time = today.strftime("%H:%M")
        end_time = (today + datetime.timedelta(minutes=10)).strftime("%H:%M")
        return num_today, txt_today, now_time, end_time

def resetVariable(today:str):
    """하루가 지나면 특정 변수를 초기화 시키는 함수

    Args:
        today (str): 오늘 요일의 값을 받고 어제와 요일이 다르면 변수를 초기화 시킴 

    Returns:
        bool: 어제와 요일이 같으면 False를, 어제와 요일이 다르면 True를 반환
    """

    global yesterday

    if yesterday == None:
        yesterday = today

    if yesterday != today:
        yesterday = today
        return True
    else:
        return False

def isWeekday(today:str, isTest:bool=False, want:bool=False):
    """오늘이 주말인지 주중인지 확인하는 함수

    Args:
        today (str): 오늘 요일을 받음
        isTest (bool): 테스트 할 때
        want (bool): 주중, 주말을 설정할 수 있음( isTest=True 일 때 )

    Returns:
        bool: 오늘이 주말이면 False를 주중이면 True를 반환
    """
    
    if isTest:
        loggingFunc(title="isWeekday", comment="TEST MODE")
        if want:
            return True
        else:
            return False
    else:
        if today not in ["Saturday", "Sunday"]:
            return True
        else:
            return False

def isShortened(): 
    """단축 수업 함수

    Returns:
        bool: !return
    """
    global isActivated
    isActivated = not isActivated
    return isActivated

def isMWF(today:str):
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
    

def isBirthday(today:str, oneNotified):
    """오늘이 생일이면 축하해주는 함수

    Args:
        today (str): 오늘 요일(num_today(ex. 01-01))을 받아옴 
    """
    
    allUserDataPath = data_dir_func("userData.json")

    with open(allUserDataPath, "r", encoding='utf-8') as f:
        allUserData = json.load(f)
    
    if today == allUserData["USERDATA"]["BIRTHDAY"] and today not in oneNotified:
        loggingFunc(title="isBirthday",comment="HAPPY BIRTHDAY TO YOU!!!")
        toaster.show_toast(
            "HAPPY BIRTHDAY TO YOU!!!",
            "Today is your birthday!!🎂",
            duration=None,
            threaded=True
        )
        oneNotified.add(today)
        

def assets_dir_func(fileName:str=""):
    """assets 상대경로 함수

    Args:
        fileName (str, optional): 파일 이름. Defaults to "".

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    return str(ASSETS_DIR / fileName)

def data_dir_func(fileName:str=""):
    """data 상대경로 함수

    Args:
        fileName (str, optional): 파일 이름. Defaults to "".

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    return str(DATA_DIR / fileName)

def getAllTimetable(choice:str=None):
    """allTimetable.json 데이터를 주는 함수

    Args:
        choice (str, optional): 키 값(없으면 allTimetable.json의 모든 data를 반환). Defaults to None.

    Returns:
        str, dict: allTimetable.json의 경로를 str로 data를 dict로 반환
    """
    ALLTIMETABLE_PATH = data_dir_func("allTimetable.json")
    
    with open(ALLTIMETABLE_PATH, "r", encoding="utf-8") as f:
        allTimetable = json.load(f)
    
    if choice == None:
        return ALLTIMETABLE_PATH, allTimetable
    else:
        return ALLTIMETABLE_PATH, allTimetable[choice]

def toasterFunc(title:str, comments:str, duration:int=None, threaded:bool=True):
    """toaster 함수

    Args:
        title (str): 제목
        comments (str): 내용용
        duration (int, optional): 지속시간. Defaults to None.
        threaded (bool, optional): 스레드. Defaults to True.
    """
    toaster.show_toast(
            f"{title}",
            f"{comments}",
            duration=duration,
            threaded=threaded
        )
    
def loggingFunc(level:str="info", title="", comment:str=""):
    """logging 함수

    Args:
        level (str, optional): 로그 레벨. Defaults to "info".
        title (str, optional): 제목. Defaults to "".
        comment (str, optional): 내용. Defaults to "".
    """
    if level == "info":
        logging.info("{:<15}: {}".format(title, comment))
    elif level == "debug":
        logging.debug("{:<15}: {}".format(title, comment))