import time
from function.mainFunctions import (
    todayVariable, resetVariable, isBirthday, isWeekday, isMWF, getJsonData, loggingFunc, notifyFunc
)

notifiedTimes = set()

def notificationFunc():
    allTimetable = getJsonData(jsonFileName="allTimetable.json")
    basicTimetable, breaktime = allTimetable["BASIC_TIMETABLE"], allTimetable["BREAKTIME"]
    while True:
        # 오늘 날짜, 요일, 시간 불러오기
        numToday, txtToday, nextTime = todayVariable()
        
        # notifiedTime 변수 초기화 ( 하루가 지날때만 )
        if resetVariable(txtToday):
            notifiedTimes.clear()
        
        # 생일 확인 함수
        isBirthday(numToday, notifiedTimes)
        
        # 주말 주중 확인 함수
        if isWeekday(txtToday):
            if nextTime in basicTimetable[txtToday]:
                notifyFunc(title=f"{txtToday} Class Notification",
                    message=f"Next Class: {basicTimetable[txtToday][nextTime]}",
                    timeKey=nextTime,
                    notifiedTimes=notifiedTimes)
            breakKey = "MWF" if isMWF(txtToday) else "TT"
            if nextTime in breaktime[breakKey]:
                notifyFunc(title=f"{txtToday} Break Notification",
                    message=f"10 minutes left until the {breaktime[breakKey][nextTime]}",
                    timeKey=nextTime,
                    notifiedTimes=notifiedTimes)
            loggingFunc(title="weekdays", comment=f"{txtToday} KEEP RUNNING")
        else:
            loggingFunc(title="weekends", comment=f"{txtToday} KEEP RUNNING")
        
        time.sleep(1)