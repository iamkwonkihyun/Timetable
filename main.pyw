import os
import subprocess
import sys
import threading

if __name__ == "__main__":
    
    req_file = "requirements.txt"
    
    # requirements 설치
    if not os.getenv("REQUIREMENTS_INSTALLED"):
        if os.path.exists(req_file):
            print("📦 필요한 패키지 설치 중...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", req_file], check=True)

            os.environ["REQUIREMENTS_INSTALLED"] = "1"

            print("필요한 패키지가 설치되었습니다. 프로그램을 재시작합니다.")
            os.execl(sys.executable, sys.executable, *sys.argv)
            sys.exit()

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
