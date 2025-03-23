import tkinter as tk
from functools import partial
from function.trayFunctions import setTimetableFunc
from function.mainFunctions import getJsonData, exitProgramFunc

def settingsTray(tray):
    """settings tray 함수
    """

    # 변수
    entries = {}

    allTimetable, allTimetablePath = getJsonData(jsonFileName="allTimetable.json", needPath=True)
    basicTimetable = allTimetable["BASIC_TIMETABLE"]

    # 창 띄우기
    root = tk.Tk()
    root.title("시간표")
    root.geometry("500x200")

    # 요일과 시간 리스트 생성
    days = list(basicTimetable.keys())
    times = sorted({time for schedule in basicTimetable.values() for time in schedule.keys()})

    # 메인 창 버튼들
    edit_button = tk.Button(
        root,
        text="시간표 설정",
        command=partial(setTimetableFunc, days, times, entries, basicTimetable, allTimetable, allTimetablePath, tray),
        width=35)
    edit_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

    exit_button = tk.Button(root, text="종료", command=exitProgramFunc)
    exit_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

    root.mainloop()