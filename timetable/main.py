def main():
    # 표준 라이브러리
    import threading

    from timetable.functions import program_running_check, timetable_func
    
    from timetable.system_tray import system_tray

    # 프로그램 실행 체크 및
    if program_running_check():
        app = system_tray()
        threading.Thread(target=timetable_func, daemon=True).start()
        app.run()