def main():
    import os
    import sys
    import subprocess
    import threading
    from timetable.functions import program_running_check, notification_func
    from timetable.system_tray import systemTray
    
    req_file = "requirements.txt"
    
    # requirements 설치
    if not os.getenv("REQUIREMENTS_INSTALLED"):
        if os.path.exists(req_file):
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)
            
            os.environ["REQUIREMENTS_INSTALLED"] = "1"
            
            os.execl(sys.executable, sys.executable, *sys.argv)
            sys.exit()
    
    # 프로그램 실행 체크
    if program_running_check():
        
        # timetableReminderFunc 백그라운드에서 단독 실행
        timetableReminderFunc = threading.Thread(target=notification_func, daemon=True)
        timetableReminderFunc.start()
        
        # system tray 설정
        app = systemTray()
        app.run()
