import logging, win32com.client, sys
from function.mainFunctions import toasterFunc

# 프로그램 실행 검사
def programCheck(programName, isTest:bool=False):
    checkTime = 0
    """프로그램 실행 검사 함수

    Args:
        programName (str): 실행되는 프로그램 이름
        isTest (bool): 테스트 할 때
    """
    if isTest == True:
        logging.info("programCheck   : TEST MODE")
        pass
    else:
        for program in programName:
            logging.info("programCheck   : ···")
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            service = wmi.ConnectServer(".", "root\\cimv2")
            process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{program}'")
            if len(process_list) > 0:
                toasterFunc(
                    title="Hello!",
                    comments="Timetable.pyw is Running!\nNice To Meet you :)",
                    duration=3,
                )
                logging.info("programCheck   : GOOD :)")
                logging.info("programCheck   : PROGRAM START")
                break
            else:
                checkTime += 1
                if checkTime == 2:
                    toasterFunc(
                        title="WHAT?!",
                        comments="oh.. bad news..\nsomething went wrong.. :(",
                        duration=3,
                    )
                    logging.info("programCheck   : BAD :(")
                    sys.exit()