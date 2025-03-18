import win32com.client
from function.mainFunctions import toasterFunc, loggingFunc
from function.trayFunctions import exitProgramFunc

# 프로그램 실행 검사
def programCheck(programName, isTest:bool=False):
    """프로그램 실행 검사 함수

    Args:
        programName (str): 실행되는 프로그램 이름
        isTest (bool): 테스트 할 때
    """
    
    checkTime = 0
    
    if isTest == True:
        loggingFunc(title="programCheck", comment="TEST MODE")
        pass
    else:
        for program in programName:
            loggingFunc(title="programCheck", comment="···")
            wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            service = wmi.ConnectServer(".", "root\\cimv2")
            process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{program}'")
            if len(process_list) > 0:
                toasterFunc(
                    title="Hello!",
                    comments="Timetable.pyw is Running!\nNice To Meet you :)",
                    duration=3,
                )
                loggingFunc(title="programCheck", comment="GOOD :)")
                loggingFunc(title="programCheck", comment="PROGRAM START")
                break
            else:
                checkTime += 1
                if checkTime == 2:
                    toasterFunc(
                        title="WHAT?!",
                        comments="oh.. bad news..\nsomething went wrong.. :(",
                        duration=3,
                    )
                    loggingFunc(title="programCheck", comment="BAD :(")
                    exitProgramFunc()