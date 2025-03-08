import logging, win32com, sys
from win10toast import ToastNotifier

toaster = ToastNotifier()

# 프로그램 실행 검사
def isRunning(programName):
    logging.info("PROGRAM CHECKING: ···")
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    service = wmi.ConnectServer(".", "root\\cimv2")
    process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{programName}'")

    while True:
        print(len(process_list))
        if len(process_list) > 0:
            toaster.show_toast(
                "Hello!",
                "Timetable.pyw is Running!\nDon't worry, it is not hacking :)",
                duration=3,
                threaded=False,
            )
            logging.info("PROGRAM CHECKING: GOOD :)")
            break
        else:
            toaster.show_toast(
                "Error",
                "fucking Error\nI don't like Error",
                duration=3,
                threaded=False,
            )
            logging.ERROR("PROGRAM CHECKING: BAD :(")
            sys.exit()