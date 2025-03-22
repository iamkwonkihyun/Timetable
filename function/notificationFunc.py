import time
from function.mainFunctions import (
    todayVariable, resetVariable, isBirthday, isWeekday, isMWF, 
    getJsonData, toasterFunc, loggingFunc, pushNotification
)

notified_times = set()

def notify(title, message, time_key):
    if time_key not in notified_times:
        toasterFunc(title=title, comments=message)
        pushNotification(message=f"{title}\n{message}")
        loggingFunc(title="notified", comment=f"{title} | {time_key}")
        notified_times.add(time_key)

def notificationFunc():
    allTimetable = getJsonData(jsonFileName="allTimetable.json")
    basicTimetable, breaktime = allTimetable["BASIC_TIMETABLE"], allTimetable["BREAKTIME"]
    
    while True:
        numToday, txtToday, nextTime = todayVariable()
        
        if resetVariable(txtToday):
            notified_times.clear()
        
        isBirthday(numToday, notified_times)
        
        if isWeekday(txtToday):
            loggingFunc(title="weekdays", comment=f"{txtToday} KEEP RUNNING")
            
            if nextTime in basicTimetable[txtToday]:
                notify(title=f"{txtToday} Class Notification",
                    message=f"Next Class: {basicTimetable[txtToday][nextTime]}",
                    time_key=nextTime)
            break_key = "MWF" if isMWF(txtToday) else "TT"
            if nextTime in breaktime[break_key]:
                notify(title=f"{txtToday} Break Notification",
                    message=f"10 minutes left until {breaktime[break_key][nextTime]} rest time",
                    time_key=nextTime)
        else:
            loggingFunc(title="weekend", comment=f"{txtToday} KEEP RUNNING")
        
        time.sleep(1)
