def main():
    # 모듈/라이브러리
    import time
    from timetable.system_tray import systemTray
    from timetable.functions import (
        program_running_check, get_api_func, get_json_data, today_variable,
        is_yesterday, is_birthday, is_weekday, notify_func, is_mwf
    )
    
    # 변수
    notified_times = set()
    today_timetable = get_json_data(json_file_name="api_timetable.json")
    all_Timetable = get_json_data(json_file_name="hard_timetable.json")
    breaktime = all_Timetable["BREAKTIME"]
    
    # 프로그램 실행 체크 및
    if program_running_check() and get_api_func():
        # system tray 설정
        app = systemTray()
        app.run()
    
    while True:
        # 오늘 날짜, 요일, 시간 불러오기
        _, num_today, txt_today, next_time = today_variable()
        
        # notifiedTime 변수 초기화 ( 하루가 지날때만 )
        if is_yesterday(txt_today):
            # notified_times 변수 초기화
            notified_times.clear()
            
            # 시간표 갱신
            get_api_func()
            
            # 생일 확인 함수
            is_birthday(num_today)
        
        # 주말 주중 확인 함수
        if is_weekday(txt_today):
            
            # 다음 교시 과목 알려주는 로직
            if next_time in today_timetable:
                notify_func(title=f"{txt_today} Class Notification",
                    message=f"Next Class: {today_timetable[next_time]}",
                    time=next_time)
            
            # 쉬는 시간 10분 전 알림 보내는 로직
            break_key = "MWF" if is_mwf(txt_today) else "TT"
            if next_time in breaktime[break_key]:
                notify_func(title=f"{txt_today} Break Notification",
                    message=f"10 minutes left until the {breaktime[break_key][next_time]}",
                    time=next_time)
            
            time.sleep(1)