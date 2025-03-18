import json, sys, tkinter as tk
from functools import partial
from tkinter import messagebox
from PyQt5.QtWidgets import QAction
from PyQt5.QtGui import QIcon
from function.mainFunctions import assets_dir_func

# mainTray.py

# 프로그램 종료 함수
def exitProgramFunc():
    """프로그램 종료 함수
    """
    sys.exit()

# timetable 저장 함수
def saveTimetableFunc(entries, basicTimetable, allTimetablePath, allTimetable, tray, second_root):
    
    result = messagebox.askquestion("질문", "저장하시겠습니까?")
    if result == "yes":
        updated = False  # 변경 여부 체크
        
        for day, schedule in entries.items():
            for time, entry in schedule.items():
                new_value = entry.get().strip()
                old_value = basicTimetable.get(day, {}).get(time, "")

                # 값이 변경되었을 경우만 업데이트
                if new_value != old_value:
                    if day not in basicTimetable:
                        basicTimetable[day] = {}
                    basicTimetable[day][time] = new_value
                    updated = True

        if updated:  # 변경 사항이 있을 때만 파일 저장
            with open(allTimetablePath, "w", encoding="utf-8") as f:
                json.dump(allTimetable, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("timetable", "저장 성공")
            tray.updateTooltip()
        else:
            messagebox.showinfo("timetable", "변경된 내용이 없습니다.")

        second_root.destroy()

# 시간표 설정 함수
def setTimetableFunc(days, times, entries, basicTimetable, allTimetable, allTimetablePath, tray):
    second_root = tk.Tk()
    second_root.title("시간표 편집")
    second_root.geometry("1200x500")

    tk.Label(second_root, text="요일", width=10, borderwidth=1, relief="solid").grid(row=0, column=0)

    for i, day in enumerate(days):
        tk.Label(second_root, text=day, width=15, borderwidth=1, relief="solid").grid(row=0, column=i+1)

    for j, time in enumerate(times):
        tk.Label(second_root, text=time, width=10, borderwidth=1, relief="solid").grid(row=j+1, column=0)
        entries[time] = {}

        for i, day in enumerate(days):
            text = basicTimetable.get(day, {}).get(time, "")
            entry = tk.Entry(second_root, width=15)
            entry.insert(0, text)
            entry.grid(row=j+1, column=i+1)
            entries.setdefault(day, {})[time] = entry

    save_button = tk.Button(second_root, text="저장", command=partial(saveTimetableFunc, entries, basicTimetable, allTimetablePath, allTimetable, tray, second_root))
    save_button.grid(row=len(times) + 1, column=0, columnspan=len(days) + 1, sticky="ew", pady=10)

# tray 메뉴 생성 함수
def makeTrayMenu(self, icon:str, title:str, function=None, action=None):
    iconPath = assets_dir_func(icon)
    
    setattr(self, action, QAction(QIcon(iconPath), title, self.menu))
    
    tray_action = getattr(self, action)
    tray_action.triggered.connect(function)
    self.menu.addAction(tray_action)
    
    
# settingsTray.py

