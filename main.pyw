# import library, package
import threading
from function.mainTray import mainTray
from function.notificationFunc import notificationFunc
from function.mainFunctions import programCheck, makeLogFolder

if __name__ == "__main__":
    # 로그 생성
    makeLogFolder()
    
    # 프로그램 실행 체크
    programCheck()
    
    #timetableReminderFunc 백그라운드에서 단독 실행
    timetableReminderFunc = threading.Thread(target=notificationFunc, args=(), daemon=True)
    timetableReminderFunc.start()
    
    #system tray 설정
    app = mainTray()
    app.run()
