# import library, package
import threading
from function.systemTray import systemTray
from function.notificationFunc import notificationFunc
from function.mainFunctions import programRunningCheck

if __name__ == "__main__":
    # 프로그램 실행 체크
    programRunningCheck()
    
    # timetableReminderFunc 백그라운드에서 단독 실행
    timetableReminderFunc = threading.Thread(target=notificationFunc, args=(), daemon=True)
    timetableReminderFunc.start()
    
    # system tray 설정
    app = systemTray()
    app.run()
