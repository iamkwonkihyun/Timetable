import datetime, logging, json, requests, win32com.client, sys, os
from logging.handlers import TimedRotatingFileHandler
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
def programCheck(isTest=isTest):
    """프로그램 실행 검사 함수

    Args:
        programName (str): 실행되는 프로그램 이름
        isTest (bool): 테스트 할 때
    """
    
    checkTime = 0
    programName = getJsonData(jsonFileName="etcData.json", rootKey="PROGRAM_DATA", subKey="PROGRAM_NAME")
    if isTest == True:
        toasterFunc(
            title="Test Mode",
            comments="This is Test Mode",
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
                    )
                    loggingFunc(title="programCheck", comment="BAD :(")
                    loggingFunc(title="programCheck", comment="PROGRAM OFF")
                    exitProgramFunc()

def todayVariable(isTest:bool=isTest):
    """오늘 요일, 시간 정보를 주는 함수
    
    Args:
        isTest (bool): 테스트 할 때
    
    Returns:
        all_returns(str): 오늘 요일, 날짜, 끝나는 시간 등 반환
        
        num_today = "MM-DD", txt_today = "Monday", now_time  = "HH:MM" + 10 minutes
    """
    
    today = datetime.datetime.today()
    
    if isTest:
        loggingFunc(title="todayVariable", comment="TEST MODE")
        num_today = "03-22"
        txt_today = "Monday"
        next_time = "08:40"
        return num_today, txt_today, next_time
    else:
        num_today = today.strftime("%m-%d")
        txt_today = today.strftime("%A")
        next_time = (today + datetime.timedelta(minutes=10)).strftime("%H:%M")
        return num_today, txt_today, next_time

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

def isWeekday(today:str, isTest:bool=isTest, isWeek:bool=isWeek):
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

def isBirthday(today:str, oneNotified:set):
    """오늘이 생일이면 축하해주는 함수

    Args:
        today (str): 오늘 요일(num_today(ex. 01-01))을 받아옴 
    """
    
    allUserData = getJsonData("etcData.json")
    
    if today == allUserData["USER_DATA"]["BIRTHDAY"] and today not in oneNotified:
        loggingFunc(title="isBirthday",comment="HAPPY BIRTHDAY TO YOU!!!")
        toaster.show_toast(
            "HAPPY BIRTHDAY TO YOU!!!",
            "Today is your birthday!!🎂",
            duration=10,
            threaded=True
        )
        pushNotification(title="HAPPY BIRTHDAY TO YOU!!!", message="Today is your birthday!!🎂")
        oneNotified.add(today)

def assets_dir_func(fileName:str):
    """assets 상대경로 함수

    Args:
        fileName (str, optional): 파일 이름. Defaults to "".

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    return str(ASSETS_DIR / fileName)

def data_dir_func(fileName:str):
    """data 상대경로 함수

    Args:
        fileName (str, optional): 파일 이름. Defaults to "".

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    return str(DATA_DIR / fileName)

def getJsonData(jsonFileName:str, rootKey:str=False, subKey:str=False, needPath:bool=False):
    """allTimetable.json 데이터를 주는 함수

    Args:
        choice (str, optional): 키 값(없으면 allTimetable.json의 모든 data를 반환). Defaults to None.

    Returns:
        str, dict: allTimetable.json의 경로를 str로 data를 dict로 반환
    """
    
    JSONDATA_PATH = data_dir_func(jsonFileName)
    
    with open(JSONDATA_PATH, "r", encoding="utf-8") as f:
        jsonData = json.load(f)
        
    
    if rootKey != False and subKey != False:
        if needPath:
            return jsonData[rootKey][subKey], JSONDATA_PATH
        return jsonData[rootKey][subKey]
    else:
        if needPath:
            return jsonData, JSONDATA_PATH
        return jsonData

def toasterFunc(title:str, comments:str, duration:int=5, threaded:bool=True):
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

def pushNotification(message:str):
    """폰으로 알림 보내는 함수

    Args:
        message (str): 폰으로 보낼 메세지
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
    loggingFunc(title="program", comment="OFF")
    logging.shutdown()
    sys.exit()

def makeLogFolder():
    # 로그 폴더 경로
    log_folder = "logs"

    # 로그 폴더가 없으면 생성
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)

    # 하루마다 새로운 로그 파일 생성, 최대 7개 유지
    handler = TimedRotatingFileHandler(
        os.path.join(log_folder, "app.log"), when="D", interval=1, backupCount=7, encoding="utf-8"
    )
    handler.suffix = "%Y-%m-%d.log"

    logging.basicConfig(
        filename="logs/app.log",
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )
    
    loggingFunc(title="makeLogFolder", comment="GOOD :)")