import time
from function.mainFunctions import (todayVariable, resetVariable,isBirthday, isWeekday, isMWF, 
                                    getAllTimetable, toasterFunc, loggingFunc, pushNotification,
                                    testFunc)

notified_times = set()

def timetableReminder(isTest=testFunc(), want=testFunc()):
    """시간표 알림 함수

    Args:
        isTest (bool): 테스트 할 때
        want (bool): 주중 주말 선택
    """
    
    _, allTimetable = getAllTimetable()
    basicTimetable = allTimetable["BASIC_TIMETABLE"]
    breaktime = allTimetable["BREAKTIME"]
    
    while True:
        
        # 모든 today, time 값 받아오기(isTest=True: 시간 설정 가능, isTest=False: 현실 시간)
        num_today, txt_today, now_time, end_time = todayVariable(isTest=isTest)
        
        # 하루가 지날 때 마다 notified_times 변수 초기화
        if resetVariable(txt_today):
            notified_times.clear()
        
        # 오늘이 생일인지 확인하는 함수
        isBirthday(num_today, notified_times)

        # 오늘이 주말인지 주중인지 확인 (isTest=True: 조종 가능, isTest=False: 조종 불가 )
        if isWeekday(today=txt_today, isTest=isTest, want=want):
            loggingFunc(title="weekdays", comment="KEEP RUNNING")
            if now_time in basicTimetable[txt_today] and now_time not in notified_times:
                subject = basicTimetable[txt_today][now_time]
                toasterFunc(
                    title=f"{txt_today} Class Notification",
                    comments=f"Next Class: {subject}",
                )
                pushNotification(f"Next Class: {subject}")
                loggingFunc(title="notified", comment=f"{txt_today} | {now_time} | {subject}")
                notified_times.add(now_time)
            
            # 오늘이 월수금인지 확인 후, 해당하는 BREAKTIME 선택
            break_time_key = "MWF" if isMWF(txt_today) else "TT"
            
            if end_time in breaktime[break_time_key] and end_time not in notified_times:
                nClass = breaktime[break_time_key][end_time]
                toasterFunc(
                    title=f"{txt_today} Class Notification",
                    comments=f"10 minutes left until the {nClass} rest time",
                    )
                pushNotification(f"10 minutes left until the {subject} rest time")
                loggingFunc(title="notified", comment=f"{txt_today} | {now_time} | {subject}")
                notified_times.add(end_time)
                
        else:
            loggingFunc(title="weekend", comment="KEEP RUNNING")
        
        time.sleep(1)