import datetime, logging, json, requests, win32com.client, sys
from pathlib import Path
from win10toast import ToastNotifier

# 토스터 객체 생성
toaster = ToastNotifier()

# global 변수
yesterday = None
isActivated = False
isTest = False
isWeek = True

# 상대경로
FUNCTION_DIR = Path(__file__).resolve().parent
BASE_DIR = FUNCTION_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

# 프로그램 실행 검사
def programCheck(programName ,isTest=isTest):
    """프로그램 실행 검사 함수

    Args:
        programName (str): 실행되는 프로그램 이름
        isTest (bool): 테스트 할 때
    """
    
    checkTime = 0
    
    if isTest == True:
        toasterFunc(
            title="Test Mode",
            comments="This is Test Mode",
            duration=3,
            threaded=False
        )
        pushNotification("This is Test Mode")
        loggingFunc(title="programCheck", comment="TEST MODE")
        pass
    else:
        for program in programName:
            loggingFunc(title="programCheck", comment="···")
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            service = wmi.ConnectServer(".", "root\\cimv2")
            process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{program}'")
            if len(process_list) > 0:
                toasterFunc(
                    title="Hello!",
                    comments="Timetable.pyw is Running!\nNice to meet you :)",
                    duration=3,
                )
                pushNotification(message="Hello!\nTimetable is Running! Nice to meet you")
                loggingFunc(title="programCheck", comment="GOOD :)") 
                loggingFunc(title="programCheck", comment="PROGRAM START")
                break
            else:
                checkTime += 1
                if checkTime == 2:
                    toasterFunc(
                        title="WHAT?!",
                        comments="oh.. bad news..\nsomething went wrong.. :(",
                        duration=3,
                    )
                    loggingFunc(title="programCheck", comment="BAD :(")
                    loggingFunc(title="programCheck", comment="PROGRAM OFF")
                    exitProgramFunc()

def todayVariable(isTest=isTest):
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
        num_today = "03-11"
        txt_today = "Monday"
        now_time = "12:30"
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
        return False
    
    if yesterday != today:
        yesterday = today
        return True
    else:
        return False

def isWeekday(today:str, isTest=isTest, isWeek=isWeek):
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
        if isWeek:
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
            duration=10,
            threaded=True
        )
        pushNotification(title="HAPPY BIRTHDAY TO YOU!!!", message="Today is your birthday!!🎂")
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

def getAllTimetable(choice:str=False):
    """allTimetable.json 데이터를 주는 함수

    Args:
        choice (str, optional): 키 값(없으면 allTimetable.json의 모든 data를 반환). Defaults to None.

    Returns:
        str, dict: allTimetable.json의 경로를 str로 data를 dict로 반환
    """
    
    ALLTIMETABLE_PATH = data_dir_func("allTimetable.json")
    
    with open(ALLTIMETABLE_PATH, "r", encoding="utf-8") as f:
        allTimetable = json.load(f)
    
    if choice == False:
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
        logging.info("{:<25}: {}".format(title, comment))
    elif level == "debug":
        logging.debug("{:<25}: {}".format(title, comment))

def pushNotification(message):
    """폰으로 알림 보내는 함수
    """

    requests.post(f"https://ntfy.sh/Timetable", data=message.encode("utf-8"))
    loggingFunc(title="pushNotification", comment="SUCCESE :)")
    
def convert_timetable(timetable):
    """시간표 데이터를 '1교시, 2교시' 형태로 변환"""
    converted = {}
    
    for day, schedule in timetable.items():
        sorted_times = sorted(schedule.keys())  # 시간을 순서대로 정렬
        converted_schedule = {f"{i+1}교시": schedule[time] for i, time in enumerate(sorted_times)}
        converted[day] = converted_schedule
    
    return converted

def exitProgramFunc():
    """프로그램 종료 함수
    """
    sys.exit()
