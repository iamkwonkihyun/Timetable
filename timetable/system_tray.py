import sys
import tkinter as tk
import locale
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from timetable.functions import (
    assets_dir_func, get_json_data, exit_program_func, convert_timetable, today_variable, alert_func
)


locale.setlocale(locale.LC_TIME, "Korean_Korea")

class system_tray:
    """윈도우 시스템 트레이 클래스"""
    
    def __init__(self):
        self.app = QApplication(sys.argv)
        
        menuIconPath = assets_dir_func("remy_icon.ico")
        self.menuIcon = QSystemTrayIcon(QIcon(menuIconPath), self.app)
        self.menu = QMenu()

        # # 프로필 트레이 ( 생일, 이름 수정할 수 있게 코드 추가 예정 )
        # make_tray_menu(self, "profile_icon.ico", "profile", show_profile, "profile")
        
        make_tray_menu(self, "meal_icon.ico", "급식표", lambda: set_meal_func(self), "meal")
        
        # 세팅 트레이
        make_tray_menu(self, "timetable_icon.ico", "시간표", show_timetable_window, "settings")
        
        # 프로그램 종료 트레이
        make_tray_menu(self, "exit_icon.ico", "프로그램 종료", exit_program_func, "exit")

        self.menuIcon.setContextMenu(self.menu)
        update_tooltip(self)
        self.menuIcon.show()
        
        
    def set_refresh(self):
        update_tooltip(self, meal=getattr(self, 'meal_state', False))
        
        
    def run(self):
        if self.app.exec_() == 0:
            exit_program_func()


def make_tray_menu(self, icon: str, title: str, function: any, action: any):
    """트레이 생성 함수"""
    
    iconPath = assets_dir_func(icon)
    
    setattr(self, action, QAction(QIcon(iconPath), title, self.menu))
    
    tray_action = getattr(self, action)
    tray_action.triggered.connect(function)
    self.menu.addAction(tray_action)


def update_tooltip(self, meal: bool = False):
    """트레이 아이콘의 툴팁 업데이트"""
    
    api_ymd, _, txt, _ = today_variable(api=True)
    basic_ymd, _, _, _ = today_variable()
    
    api_timetable = get_json_data(json_file_name = "api_timetable.json")
    meal_list = get_json_data(json_file_name="api_meal.json")
    
    meal_list = meal_list[api_ymd]["중식"].split(",")
    converted_timetable = convert_timetable(api_timetable)
    
    meal_message = "\n".join([f"{food}" for food in meal_list])
    timetable_message = "\n".join([f"{time}: {task}" for time, task in converted_timetable.items()]) or "No schedule available"
    print(txt)
    
    timetable_message = f"""{basic_ymd}{txt}
{meal_message if meal else timetable_message}"""
    
    self.menuIcon.setToolTip(timetable_message)


def set_meal_func(self):
    self.meal_state = not getattr(self, 'meal_state', False)
    alert_func("show meal", "change state", only_toast=True)
    update_tooltip(self, meal=self.meal_state)


def show_timetable_window():
    """settings tray 함수"""
    entries = {}

    all_timetable, _ = get_json_data(json_file_name="hard_timetable.json", need_path=True)
    basic_timetable = all_timetable["BASIC_TIMETABLE"]

    root = tk.Tk()
    root.title("시간표 편집")
    root.geometry("1550x300")
    tk.Label(root, text="요일", width=10, borderwidth=1, relief="solid").grid(row=0, column=0)

    # 요일과 시간 리스트 생성
    days = list(basic_timetable.keys())
    times = sorted({time for schedule in basic_timetable.values() for time in schedule.keys()})

    for i, day in enumerate(days):
        tk.Label(root, text=day, width=20, borderwidth=1, relief="solid").grid(row=0, column=i+1)

    for j, time in enumerate(times):
        tk.Label(root, text=time, width=10, borderwidth=1, relief="solid").grid(row=j+1, column=0)

        for i, day in enumerate(days):
            text = basic_timetable.get(day, {}).get(time, "")
            entry = tk.Entry(root, width=20)
            entry.insert(0, text)
            entry.grid(row=j+1, column=i+1)
            entries.setdefault(day, {})[time] = entry

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


# def show_profile():
#     """프로필 설정 함수"""
#     root = tk.Tk()
#     root.title("profile")
#     root.geometry("1000x1000")
#     root.mainloop()


# def save_timetable_func(self, entries, basic_timetable, all_timetable_path, all_timetable, root):
#     """시간표 저장 함수"""
#     result = messagebox.askquestion("질문", "저장하시겠습니까?")
#     if result == "yes":
#         updated = False
        
#         for day, schedule in entries.items():
#             for time, entry in schedule.items():
#                 new_value = entry.get().strip()
#                 old_value = basic_timetable.get(day, {}).get(time, "")

#                 if new_value != old_value:
#                     basic_timetable.setdefault(day, {})[time] = new_value
#                     updated = True

#         if updated:
#             with open(all_timetable_path, "w", encoding="utf-8") as f:
#                 json.dump(all_timetable, f, ensure_ascii=False, indent=4)
#             messagebox.showinfo("timetable", "저장 성공")
#             update_tooltip(self)
#         else:
#             messagebox.showinfo("timetable", "변경된 내용이 없습니다.")

#         root.destroy()


# def set_timetable_func(self, days, times, entries, basic_timetable, all_timetable, all_timetable_path):
#     """시간표 수정 창 띄우는 함수"""
#     root = tk.Tk()
#     root.title("시간표 편집")
#     root.geometry("1600x400")
#     tk.Label(root, text="요일", width=10, borderwidth=1, relief="solid").grid(row=0, column=0)

#     for i, day in enumerate(days):
#         tk.Label(root, text=day, width=20, borderwidth=1, relief="solid").grid(row=0, column=i+1)

#     for j, time in enumerate(times):
#         tk.Label(root, text=time, width=10, borderwidth=1, relief="solid").grid(row=j+1, column=0)

#         for i, day in enumerate(days):
#             text = basic_timetable.get(day, {}).get(time, "")
#             entry = tk.Entry(root, width=20)
#             entry.insert(0, text)
#             entry.grid(row=j+1, column=i+1)
#             entries.setdefault(day, {})[time] = entry

#     save_button = tk.Button(
#         root,
#         text="저장",
#         command=partial(save_timetable_func, entries, basic_timetable, all_timetable_path, all_timetable, self, root)
#     )
#     save_button.grid(row=len(times) + 1, column=0, columnspan=len(days) + 1, sticky="ew", pady=10)