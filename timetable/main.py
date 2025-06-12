def main():
    # 모듈/라이브러리
    import threading
    from timetable.system_tray import system_tray
    from timetable.functions import (
        program_running_check, timetable_func
    )
    
    # 프로그램 실행 체크 및
    if program_running_check():
        threading.Thread(target=timetable_func, daemon=True).start()
        app = system_tray()
        app.run()