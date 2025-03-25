import datetime, logging, json, requests, win32com.client, sys, os, shutil, subprocess, threading
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

def programRunningCheck(isTest:bool=isTest):
    """프로그램 실행 검사 함수

    Args:
        isTest (bool, optional): 테스트 인자. Defaults to isTest.
    """
    checkTime = 0
    programName = getJsonData(jsonFileName="etcData.json", rootKey="PROGRAM_DATA", subKey="PROGRAM_NAME")
    
    # 로그 생성 함수
    makeLogFolder()
    
    if isTest == True:
        toasterFunc(
            title="isTest is True",
            comment="now, Test Mode",
        )
        pushNotification(title="This is Test Mode", comment="test mode")
        loggingFunc(title="programRunningCheck", comment="TEST MODE")
        
        log_thread = threading.Thread(target=watchLogFunc, args=(True,), daemon=True)
        log_thread.start()
        
        return True
    
    for program in programName:
        loggingFunc(title="programRunningCheck", comment="···")
        wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        service = wmi.ConnectServer(".", "root\\cimv2")
        process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{program}'")
        if len(process_list) > 0:
            toasterFunc(
                title="😀 Hello!",
                comment="Timetable is Running!\nNice to meet you :)",
            )
            pushNotification(title="😀 Hello", comment="Timetable is Running! Nice to meet you")
            loggingFunc(title="programRunningCheck", comment="GOOD")
            break
        else:
            checkTime += 1
            if checkTime == len(programName):
                toasterFunc(
                    title="🤯 What?!",
                    comment="oh No.. bad news..\nsomething went wrong.. :(",
                )
                pushNotification(title="🤯 What?!", comment="oh No.. bad news..\nsomething went wrong.. :(",)
                loggingFunc(title="programRunningCheck", comment="FAILED")
                exitProgramFunc()

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
        
    loggingFunc(title="makeLogFolder", comment="SUCCESS")

def notifyFunc(title:str, message:str, time:str, notifiedTimes:set):
    """알림 함수

    Args:
        title (str): 제목
        message (str): 내용
        timeKey (str): 시간
        notifiedTimes (set): notifiedTimes 변수
    """
    
    if time not in notifiedTimes:
        toasterFunc(title=title, comment=message)
        pushNotification(title=title, comment=message)
        loggingFunc(title="notified", comment=f"{title} | {time}")
        notifiedTimes.add(time)

def todayVariable(isTest:bool=isTest):
    """오늘 날짜, 요일, 시간을 반환하는 함수

    Args:
        isTest (bool, optional): 테스트 인자.

    Returns:
        allReturns: numToday(MM-DD), txtToday(Monday), nextTime(HH:MM) 날짜, 요일, 시간을 str로 반환
    """
    
    today = datetime.datetime.today()
    
    if isTest:
        return "03-22", "Monday", "09:30"

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
        return isWeek
    return today not in ["Saturday", "Sunday"]

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
        toasterFunc(title="HAPPY BIRTHDAY TO YOU!!!", comment="Today is your birthday!!🎂")
        pushNotification(message="HAPPY BIRTHDAY TO YOU!!!\nToday is your birthday!!🎂")
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

def getJsonData(jsonFileName: str, rootKey: str = None, subKey: str = None, needPath: bool = False):
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
        jsonData = json.load(f)

    if rootKey is None:
        result = jsonData
    elif subKey is None:
        result = jsonData.get(rootKey, None)
    else:
        result = jsonData.get(rootKey, {}).get(subKey, None)

    return (result, JSONDATA_PATH) if needPath else result

def toasterFunc(title:str="", comment:str="", duration:int=3, threaded:bool=True, iconPath:str=None):
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

def pushNotification(title:str, comment:str):
    """폰으로 알림 보내는 함수

    Args:
        message (str): 폰으로 보낼 메세지
    """
    comments = f"{title}\n{comment}"
    requests.post(f"https://ntfy.sh/Timetable", data=comments.encode("utf-8"))
    loggingFunc(title="pushNotification", comment="SUCCESE")

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

def watchLogFunc(isTest:bool=isTest):
    if isTest:
        loggingFunc(title="isWeekday", comment="TEST MODE")
        loggingFunc(title="todayVariable", comment="TEST MODE")
        cmd = ["powershell", "-Command", "Get-Content logs/app.log -Wait"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            for line in process.stdout:
                print(line, end="")
        except KeyboardInterrupt:
                process.terminate()