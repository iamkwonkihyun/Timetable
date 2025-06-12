import sys
import json
import tkinter as tk
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from timetable.functions import assets_dir_func, exit_program_func
from PyQt5.QtCore import QTimer
from functools import partial
from tkinter import messagebox
from timetable.functions import (
    assets_dir_func, get_json_data, exit_program_func, convert_timetable, get_api_func, today_variable
)


class systemTray:
    """Windows System Tray Function"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        menuIconPath = assets_dir_func("remy_icon.ico")
        self.menuIcon = QSystemTrayIcon(QIcon(menuIconPath), self.app)
        self.menu = QMenu()

        # 프로필 트레이 ( 생일, 이름 수정할 수 있게 코드 추가 예정 )
        make_tray_menu(self, "profile_icon.ico", "profile", show_profile, "profile")
        
        # 단축 수업 트레이 ( 추후 수정 예정 ) ( 수정할 필요 없을지도 )
        # makeTrayMenu(self, "time_icon.ico", "Shortened_Timetable", lambda: setShortenedTimetableMode(self), "shortenedTimetable")
        
        # 세팅 트레이
        make_tray_menu(self, "timetable_icon.ico", "Watch_Timetable", lambda: show_timetable_window(self), "settings")
        
        # 프로그램 종료 트레이
        make_tray_menu(self, "exit_icon.ico", "Exit", exit_program_func, "exit")

        self.menuIcon.setContextMenu(self.menu)
        update_tooltip(self)
        self.menuIcon.show()
        
        set_refresh(self)


    def run(self):
        if self.app.exec_() == 0:
            exit_program_func()


def make_tray_menu(tray:any, icon:str, title:str, function:any, action:any):
    """트레이 생성 함수"""
    iconPath = assets_dir_func(icon)
    
    setattr(tray, action, QAction(QIcon(iconPath), title, tray.menu))
    
    tray_action = getattr(tray, action)
    tray_action.triggered.connect(function)
    tray.menu.addAction(tray_action)


def update_tooltip(tray):
    """트레이 아이콘의 툴팁 업데이트"""
    ymd, _, _, _ = today_variable()
    
    api_timetable = get_json_data(json_file_name = "api_timetable.json")
    
    converted_timetable = convert_timetable(api_timetable)
    
    timetable_message = "\n".join([f"{time}: {task}" for time, task in converted_timetable.items()]) or "No schedule available"
    
    timetable_message = f"{ymd}\n{timetable_message}"
    
    tray.menuIcon.setToolTip(timetable_message)


def set_refresh(tray):
    tray.refreshTimer = QTimer()
    tray.refreshTimer.timeout.connect(lambda: update_tooltip(tray=tray))
    tray.refreshTimer.start(60 * 1000)  # 60초
    get_api_func()


def show_profile():
    """프로필 설정 함수"""
    root = tk.Tk()
    root.title("profile")
    root.geometry("1000x1000")
    root.mainloop()


def save_timetable_func(entries, basicTimetable, allTimetablePath, allTimetable, tray, root):
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
            update_tooltip(tray)
        else:
            messagebox.showinfo("timetable", "변경된 내용이 없습니다.")

        root.destroy()


def set_timetable_func(days, times, entries, basicTimetable, allTimetable, allTimetablePath, tray):
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
        command=partial(save_timetable_func, entries, basicTimetable, allTimetablePath, allTimetable, tray, root)
    )
    save_button.grid(row=len(times) + 1, column=0, columnspan=len(days) + 1, sticky="ew", pady=10)


def show_timetable_window(tray):
    """settings tray 함수"""
    entries = {}

    allTimetable, allTimetablePath = get_json_data(json_file_name="hard_timetable.json", need_path=True)
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
        text="모든 시간표 보기",
        command=partial(set_timetable_func, days, times, entries, basicTimetable, allTimetable, allTimetablePath, tray),
        width=35)
    edit_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

    exit_button = tk.Button(root, text="종료", command=exit_program_func)
    exit_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

    root.mainloop()


# 추후 수정 예정
# def setShortenedTimetableMode(tray):
#     """단축 시간표 모드 알림"""
#     isActivated = is_shortened()
#     comment = "Activated" if isActivated else "Deactivated"
#     updateTooltip(tray, isShortened=isActivated)
#     notification_func(
#         title="shortened timetable",
#         comment=f"Shortened Timetable Mode is {comment}"
#     )