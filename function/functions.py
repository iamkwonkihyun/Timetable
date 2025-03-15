import datetime, logging, json, os
from pathlib import Path
from win10toast import ToastNotifier

# 토스터 객체 생성
toaster = ToastNotifier()
oneNotification = set()

# global 변수
yesterday = None
isActivated = False

# 상대경로
FUNCTION_DIR = Path(__file__).resolve().parent
BASE_DIR = FUNCTION_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

def todayVariable(isTest):
    """오늘 요일, 시간 정보를 알려주는 함수

    Args:
        isTest (bool): 테스트 할 때

    Returns:
        all_returns(str): 오늘 요일, 날짜, 끝나는 시간 등 반환
        
        || num_today = "MM-DD" || txt_today = "Monday" || now_time  = "HH:MM" || end_time  = "HH:MM" + 10 minutes ||
    """
    
    today = datetime.datetime.today()
    if isTest:
        logging.debug("todayVariable MODE: TEST")
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
        boolean: 어제와 요일이 같으면 False를, 어제와 요일이 다르면 True를 반환
    """
    global yesterday
    
    if yesterday == None:
        yesterday = today
    
    if yesterday != today:
        yesterday = today
        return True
    else:
        return False
    


def isWeekday(today:str, isTest:bool, want:bool):
    """오늘이 주말인지 주중인지 확인하는 함수

    Args:
        today (str): 오늘 요일을 받음
        isTest (bool): 테스트 할 때
        want (bool): 주중, 주말을 설정할 수 있음( isTest=True 일 때 )

    Returns:
        bool: 오늘이 주말이면 False를 주중이면 True를 반환
    """
    if isTest:
        logging.debug("isWeekday Function: TEST MODE")
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
    """단축 수업 인지 확인하는 함수

    Returns:
        bool: systemTray에서 클릭할 때 마다 isActivated가 바뀜
    """
    global isActivated
    
    # if isActivated == True:
    #     isActivated = False
    #     return True
    # elif isActivated == False:
    #     isActivated = True
    #     return False
    return False
    
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
    



def isBirthday(today:str):
    """오늘이 생일이면 축하해주는 함수

    Args:
        today (str): 오늘 요일(num_today(ex. 01-01))을 받아옴 
    """
    
    BITRHDAY_PATH = data_dir_func("userData.json")

    os.path.exists(BITRHDAY_PATH)

    with open(BITRHDAY_PATH, "r", encoding='utf-8') as f:
        BIRTHDAY = json.load(f)
    
    if today == BIRTHDAY and today not in oneNotification:
        logging.info("HAPPY BIRTHDAY TO YOU!!!")
        toaster.show_toast(
            "HAPPY BIRTHDAY TO YOU!!!",
            "Today is your birthday!!🎂",
            duration=None,
            threaded=True
        )
        oneNotification.add(today)
        

def assets_dir_func(fileName=""):
    return str(ASSETS_DIR / fileName)

def data_dir_func(fileName=""):
    return str(DATA_DIR / fileName)