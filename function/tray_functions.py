import json, tkinter as tk
from functools import partial
from tkinter import messagebox
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from function.main_functions import (
    assets_dir_func, today_variable, is_mwf, is_shortened, get_json_data, convert_timetable, exitProgramFunc, toaster_func,
    logging_func
)

def makeTrayMenu(tray:any, icon:str, title:str, function:any, action:any):
    """트레이 생성 함수"""
    iconPath = assets_dir_func(icon)
    
    setattr(tray, action, QAction(QIcon(iconPath), title, tray.menu))
    
    tray_action = getattr(tray, action)
    tray_action.triggered.connect(function)
    tray.menu.addAction(tray_action)
    
    logging_func(title=f"make{title}", comment="SUCCESS")

def updateTooltip(tray, isShortened=False):
    """트레이 아이콘의 툴팁 업데이트"""
    allTimetable = get_json_data(jsonFileName="mainData.json")
    basicTimetable = convert_timetable(allTimetable["BASIC_TIMETABLE"])
    shortenedTimetable = allTimetable["SHORTENED_TIMETABLE"]
    _, txt_today, _ = today_variable()

    today_schedule = (
        shortenedTimetable.get("MWF" if is_mwf(today=txt_today) else "TT", {})
        if isShortened else basicTimetable.get(txt_today, {})
    )

    timetable_message = "\n".join([f"{time}: {task}" for time, task in today_schedule.items()]) or "No schedule available"
    tray.menuIcon.setToolTip(timetable_message)
    logging_func(title="updateTooltip", comment="SUCCESS")

def setRefresh(tray):
    updateTooltip(tray=tray)
    logging_func(title="setRefresh", comment="SUCCESS")

def setShortenedTimetableMode(tray):
    """단축 시간표 모드 알림"""
    isActivated = is_shortened()
    comment = "Activated" if isActivated else "Deactivated"
    updateTooltip(tray, isShortened=isActivated)
    toaster_func(
        title="shortened timetable",
        comment=f"Shortened Timetable Mode is {comment}"
    )
    logging_func(title="setShortenedTimetableMode", comment=comment)

def showProfile():
    """프로필 설정 함수"""
    root = tk.Tk()
    root.title("profile")
    root.geometry("1000x1000")
    root.mainloop()

def saveTimetableFunc(entries, basicTimetable, allTimetablePath, allTimetable, tray, root):
    """시간표 저장 함수"""
    result = messagebox.askquestion("질문", "저장하시겠습니까?")
    if result == "yes":
        updated = False
        
        for day, schedule in entries.items():
            for time, entry in schedule.items():
                new_value = entry.get().strip()
                old_value = basicTimetable.get(day, {}).get(time, "")

                if new_value != old_value:
                    basicTimetable.setdefault(day, {})[time] = new_value
                    updated = True

        if updated:
            with open(allTimetablePath, "w", encoding="utf-8") as f:
                json.dump(allTimetable, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("timetable", "저장 성공")
            updateTooltip(tray)
        else:
            messagebox.showinfo("timetable", "변경된 내용이 없습니다.")

        root.destroy()

def setTimetableFunc(days, times, entries, basicTimetable, allTimetable, allTimetablePath, tray):
    """시간표 수정 창 띄우는 함수"""
    root = tk.Tk()
    root.title("시간표 편집")
    root.geometry("1600x400")

    tk.Label(root, text="요일", width=10, borderwidth=1, relief="solid").grid(row=0, column=0)

    for i, day in enumerate(days):
        tk.Label(root, text=day, width=20, borderwidth=1, relief="solid").grid(row=0, column=i+1)

    for j, time in enumerate(times):
        tk.Label(root, text=time, width=10, borderwidth=1, relief="solid").grid(row=j+1, column=0)

        for i, day in enumerate(days):
            text = basicTimetable.get(day, {}).get(time, "")
            entry = tk.Entry(root, width=20)
            entry.insert(0, text)
            entry.grid(row=j+1, column=i+1)
            entries.setdefault(day, {})[time] = entry

    save_button = tk.Button(
        root,
        text="저장",
        command=partial(saveTimetableFunc, entries, basicTimetable, allTimetablePath, allTimetable, tray, root)
    )
    save_button.grid(row=len(times) + 1, column=0, columnspan=len(days) + 1, sticky="ew", pady=10)

def showSettingsWindow(tray):
    """settings tray 함수"""
    entries = {}

    allTimetable, allTimetablePath = get_json_data(jsonFileName="mainData.json", needPath=True)
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