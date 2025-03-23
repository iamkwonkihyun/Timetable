import datetime, logging, json, requests, win32com.client, sys, os, shutil, subprocess
from logging.handlers import TimedRotatingFileHandler
from win10toast import ToastNotifier
from pathlib import Path

# 토스터 객체 생성
toaster = ToastNotifier()

# 테스트 변수
isWeek, isTest = True, False 

# global 변수
yesterday = None
isActivated = False

# 상대경로
FUNCTION_DIR = Path(__file__).resolve().parent
BASE_DIR = FUNCTION_DIR.parent
ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"

def watchLogFunc(isTest=isTest):
    cmd = ["powershell", "-Command", "Get-Content logs/app.log -Wait"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if isTest:
        try:
            for line in process.stdout:
                print(line, end="")
        except KeyboardInterrupt:
                process.terminate()

def programCheck(isTest:bool=isTest):
    """프로그램 실행 검사 함수

    Args:
        isTest (bool, optional): 테스트 인자. Defaults to isTest.
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

def notifyFunc(title:str, message:str, timeKey:str, notifiedTimes:set):
    """알림 함수

    Args:
        title (str): 제목
        message (str): 내용
        timeKey (str): 시간
        notifiedTimes (set): notifiedTimes 변수
    """
    
    if timeKey not in notifiedTimes:
        toasterFunc(title=title, comments=message)
        pushNotification(message=f"{title}\n{message}")
        loggingFunc(title="notified", comment=f"{title} | {timeKey}")
        notifiedTimes.add(timeKey)

def todayVariable(isTest:bool=isTest):
    """오늘 날짜, 요일, 시간을 반환하는 함수

    Args:
        isTest (bool, optional): 테스트 인자.

    Returns:
        allReturns: numToday(MM-DD), txtToday(Monday), nextTime(HH:MM) 날짜, 요일, 시간을 str로 반환
    """
    
    today = datetime.datetime.today()
    
    if isTest:
        loggingFunc(title="todayVariable", comment="TEST MODE")
        numToday = "03-22"
        txtToday = "Monday"
        nextTime = "08:40"
        return numToday, txtToday, nextTime
    else:
        numToday = today.strftime("%m-%d")
        txtToday = today.strftime("%A")
        nextTime = (today + datetime.timedelta(minutes=10)).strftime("%H:%M")
        return numToday, txtToday, nextTime

def resetVariable(today:str):
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

def isWeekday(today:str, isTest:bool=isTest, isWeek:bool=isWeek):
    """오늘이 주말인지 주중인지 확인하는 함수

    Args:
        today (str): 오늘 날짜
        isTest (bool, optional): 테스트 인자. Defaults to isTest.
        isWeek (bool, optional): 테스트 인자 주말 주중 선택. Defaults to isWeek.

    Returns:
        bool: 주말이면 True를 주말이면 False를 반환
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
        bool: !isActicated
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
    """오늘이 생일인지 확인해주는 함수

    Args:
        today (str): 오늘 날짜
        oneNotified (set): set 변수
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
        fileName (str): 파일 이름.

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    
    return str(ASSETS_DIR / fileName)

def data_dir_func(fileName:str):
    """data 상대경로 함수

    Args:
        fileName (str): 파일 이름.

    Returns:
        str: 파일까지의 상대경로를 str로 반환
    """
    return str(DATA_DIR / fileName)

def getJsonData(jsonFileName:str, rootKey:str=None, subKey:str=None, needPath:bool=False):
    """json 데이터를 반환하는 함수

    Args:
        jsonFileName (str): json 파일 이름
        rootKey (str, optional): 루트키. Defaults to False.
        subKey (str, optional): 서브키. Defaults to False.
        needPath (bool, optional): 파일 경로 필요하면 True. Defaults to False.

    Returns:
        allReturns: 
    """
    
    JSONDATA_PATH = data_dir_func(jsonFileName)
    
    with open(JSONDATA_PATH, "r", encoding="utf-8") as f:
        jsonData = json.load(f)
    
    if rootKey is None:
        result = jsonData
    elif subKey is None:
        result = jsonData[rootKey]
    else:
        result = jsonData[rootKey][subKey]

    return (result, JSONDATA_PATH) if needPath else result

def toasterFunc(title:str, comments:str, duration:int=0, threaded:bool=True):
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

def loggingFunc(title:str, comment:str, level:str="info"):
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

def pushNotification(message:str):
    """폰으로 알림 보내는 함수

    Args:
        message (str): 폰으로 보낼 메세지
    """

    requests.post(f"https://ntfy.sh/Timetable", data=message.encode("utf-8"))
    loggingFunc(title="pushNotification", comment="SUCCESE :)")
    
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

def exitProgramFunc():
    """프로그램 종료 함수
    """
    loggingFunc(title="program", comment="OFF")
    logging.shutdown()
    sys.exit()

def makeLogFolder(isTest=isTest):
    """로그 생성 함수

    Args:
        isTest (bool, optional): 테스트 인자. Defaults to isTest.
    """
    
    log_folder = "logs"
    
    if isTest:
        shutil.rmtree(log_folder, ignore_errors=True)
        loggingFunc(title="makeLogFolder", comment="TEST MODE")
    
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
        
    loggingFunc(title="makeLogFolder", comment="GOOD :)")