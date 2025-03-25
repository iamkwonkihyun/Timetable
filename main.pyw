if __name__ == "__main__":
    
    import os, subprocess, sys, threading
    
    req_file = "requirements.txt"
    
    if os.path.exists(req_file):
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)
        
    from function.mainFunctions import programRunningCheck
    from function.systemTray import systemTray
    from function.notificationFunc import notificationFunc
    
    # 프로그램 실행 체크
    programRunningCheck()
    
    # timetableReminderFunc 백그라운드에서 단독 실행
    timetableReminderFunc = threading.Thread(target=notificationFunc, args=(), daemon=True)
    timetableReminderFunc.start()
    
    # system tray 설정
    app = systemTray()
    app.run()
