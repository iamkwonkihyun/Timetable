import json, tkinter as tk
from functools import partial
from tkinter import messagebox
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction
from function.mainFunctions import (
    assets_dir_func, todayVariable, isMWF, isShortened, getJsonData, convert_timetable, exitProgramFunc, toasterFunc
)

# - - - - - - - - - mainTray.py functions - - - - - - - - - - - - - - -

def makeTrayMenu(tray, icon:str, title:str, function=None, action=None):
    iconPath = assets_dir_func(icon)
    
    setattr(tray, action, QAction(QIcon(iconPath), title, tray.menu))
    
    tray_action = getattr(tray, action)
    tray_action.triggered.connect(function)
    tray.menu.addAction(tray_action)

def updateTooltip(tray, isShortened=False):
    """트레이 아이콘의 툴팁 업데이트"""
    allTimetable = getJsonData(jsonFileName="allTimetable.json")
    basicTimetable = convert_timetable(allTimetable["BASIC_TIMETABLE"])
    shortenedTimetable = allTimetable["SHORTENED_TIMETABLE"]
    _, txt_today, _ = todayVariable()

    today_schedule = (
        shortenedTimetable.get("MWF" if isMWF(today=txt_today) else "TT", {})
        if isShortened else basicTimetable.get(txt_today, {})
    )

    timetable_message = "\n".join([f"{time}: {task}" for time, task in today_schedule.items()]) or "No schedule available"
    tray.menuIcon.setToolTip(timetable_message)

def showHansei():
    toasterFunc(
        comments="한세사이버보안고등학교 교가 1절\n유유히 흐르는 한강을\n가슴에 담고",
    )

def showShortenedTimetable(tray):
    """단축 시간표 모드 알림"""
    isActivated = isShortened()
    comment = "Activated" if isActivated else "Deactivated"
    updateTooltip(tray, isShortened=isActivated)
    toasterFunc(
        comments=f"Shortened Timetable Mode is {comment}"
    )

def showSettings(tray):
    """설정창 열기"""
    from function.settingsTray import settingsTray
    settingsTray(tray)

def exitApp():
    """프로그램 종료"""
    exitProgramFunc()

def showProfile():
    """프로필 설정 함수
    """
    
    root = tk.Tk()
    root.title("profile")
    root.geometry("1000x1000")

# - - - - - - - - - settingsTray.py functions - - - - - - - - - - - - - - -

def saveTimetableFunc(entries, basicTimetable, allTimetablePath, allTimetable, tray, secondRoot):
    result = messagebox.askquestion("질문", "저장하시겠습니까?")
    if result == "yes":
        updated = False  # 변경 여부 체크
        
        for day, schedule in entries.items():
            for time, entry in schedule.items():
                new_value = entry.get().strip()
                old_value = basicTimetable.get(day, {}).get(time, "")

                # 값이 변경되었을 경우만 업데이트
                if new_value != old_value:
                    basicTimetable.setdefault(day, {})[time] = new_value
                    updated = True

        if updated:  # 변경 사항이 있을 때만 파일 저장
            with open(allTimetablePath, "w", encoding="utf-8") as f:
                json.dump(allTimetable, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("timetable", "저장 성공")
            updateTooltip(tray)  # 🔥 tray 객체 전달!
        else:
            messagebox.showinfo("timetable", "변경된 내용이 없습니다.")

        secondRoot.destroy()

def setTimetableFunc(days, times, entries, basicTimetable, allTimetable, allTimetablePath, tray):
    second_root = tk.Tk()
    second_root.title("시간표 편집")
    second_root.geometry("1600x400")

    tk.Label(second_root, text="요일", width=10, borderwidth=1, relief="solid").grid(row=0, column=0)

    for i, day in enumerate(days):
        tk.Label(second_root, text=day, width=20, borderwidth=1, relief="solid").grid(row=0, column=i+1)

    for j, time in enumerate(times):
        tk.Label(second_root, text=time, width=10, borderwidth=1, relief="solid").grid(row=j+1, column=0)

        for i, day in enumerate(days):
            text = basicTimetable.get(day, {}).get(time, "")
            entry = tk.Entry(second_root, width=20)
            entry.insert(0, text)
            entry.grid(row=j+1, column=i+1)
            entries.setdefault(day, {})[time] = entry  # 🔥 entries 초기화 수정

    save_button = tk.Button(
        second_root,
        text="저장",
        command=partial(saveTimetableFunc, entries, basicTimetable, allTimetablePath, allTimetable, tray, second_root)
    )
    save_button.grid(row=len(times) + 1, column=0, columnspan=len(days) + 1, sticky="ew", pady=10)