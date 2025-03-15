import logging, time, json, os
from win10toast import ToastNotifier
from function.functions import todayVariable, resetVariable, isBirthday, isWeekday, isMWF, data_dir_func

TIMETABLE_PATH = data_dir_func("timetable.json")

# 기존 시간표 데이터 불러오기
os.path.exists(TIMETABLE_PATH)

with open(TIMETABLE_PATH, "r", encoding="utf-8") as f:
    timetable = json.load(f)

BASIC_TIMETABLE = timetable["BASIC_TIMETABLE"]
BREAKTIME = timetable["BREAKTIME"]

# toaster 객체 생성
toaster = ToastNotifier()

# notification 한 번만 보내게 해줄 변수
notified_times = set()

def timetableReminder(isTest, want):
    
    # 저장할 파일 경로
    FILE_PATH = data_dir_func("timetable.json")

    # 기존 시간표 데이터 불러오기
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            TIMETABLE = json.load(f)
    
    """시간표 알림 함수

    Args:
        isTest (bool): 테스트 할 때
        want (bool): 주중 주말 선택
    """
    while True:
        
        # 모든 today, time 값 받아오기(isTest=True: 시간 설정 가능, isTest=False: 현실 시간)
        num_today, txt_today, now_time, end_time = todayVariable(isTest=isTest)
        
        # 하루가 지날 때 마다 notified_times 변수 초기화
        if resetVariable(txt_today):
            notified_times.clear()
        
        # 오늘이 생일인지 확인하는 함수
        isBirthday(num_today)

        # 오늘이 주말인지 주중인지 확인 (isTest=True: 조종 가능, isTest=False: 조종 불가 )
        if isWeekday(today=txt_today, isTest=isTest, want=want):
            
            logging.info(f"WEEKDAYS:{txt_today} KEEP RUNNING")
            
            if now_time in BASIC_TIMETABLE[txt_today] and now_time not in notified_times:
                subject = BASIC_TIMETABLE[txt_today][now_time]
                toaster.show_toast(
                    f"{txt_today} Class Notification",
                    f"Next Class: {subject}",
                    duration=None,
                    threaded=True,
                )
                logging.info(f"{txt_today} | {now_time} | {subject} ")
                notified_times.add(now_time)
            
            # 오늘이 월수금인지 확인 후, 해당하는 BREAKTIME 선택
            break_time_key = "MWF" if isMWF(txt_today) else "TT"
            
            if end_time in BREAKTIME[break_time_key] and end_time not in notified_times:
                nClass = BREAKTIME[break_time_key][end_time]
                toaster.show_toast(
                    f"{txt_today} Class Notification",
                    f"10 minutes left until the {nClass} rest time",
                    duration=None,
                    threaded=True,
                )
                logging.info(f"{txt_today} | {end_time} | {nClass}")
                notified_times.add(end_time)
                
            time.sleep(1)
        else:
            logging.info(f"WEEKEND:{txt_today} KEEP RUNNING")
            time.sleep(1)