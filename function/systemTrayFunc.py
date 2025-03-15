import tkinter as tk
from tkinter import messagebox
import json, sys, os, logging
from function.reminder import data_dir_func

def settings(tray):
    # 변수
    entries = {}

    # 시간표 불러오기
    FILE_PATH = data_dir_func("timetable.json")
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            timetable = json.load(f)
    else:
        timetable = {"BASIC_TIMETABLE": {}}

    BASIC_TIMETABLE = timetable["BASIC_TIMETABLE"]

    # 창 띄우기
    root = tk.Tk()
    root.title("시간표")
    root.geometry("500x500")

    # 요일과 시간 리스트 생성
    days = list(BASIC_TIMETABLE.keys())
    times = sorted({time for schedule in BASIC_TIMETABLE.values() for time in schedule.keys()})

    # 프로그램 종료 함수
    def exit_program():
        sys.exit()

    # 시간표 설정 함수
    def set_timetable():
        def save_timetable():
            result = messagebox.askquestion("질문", "저장하시겠습니까?")
            if result == "yes":
                updated = False  # 변경 여부 체크
                
                for day, schedule in entries.items():
                    for time, entry in schedule.items():
                        new_value = entry.get().strip()
                        old_value = BASIC_TIMETABLE.get(day, {}).get(time, "")

                        # 값이 변경되었을 경우만 업데이트
                        if new_value != old_value:
                            if day not in BASIC_TIMETABLE:
                                BASIC_TIMETABLE[day] = {}
                            BASIC_TIMETABLE[day][time] = new_value
                            updated = True

                if updated:  # 변경 사항이 있을 때만 파일 저장
                    with open(FILE_PATH, "w", encoding="utf-8") as f:
                        json.dump(timetable, f, ensure_ascii=False, indent=4)
                    messagebox.showinfo("timetable", "저장 성공")
                    
                    # 시간표를 저장한 후 툴팁 업데이트
                    tray.update_tooltip()
                else:
                    messagebox.showinfo("timetable", "변경된 내용이 없습니다.")

                second_root.destroy()

        # 두 번째 창 생성
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
                text = BASIC_TIMETABLE.get(day, {}).get(time, "")
                entry = tk.Entry(second_root, width=15)
                entry.insert(0, text)
                entry.grid(row=j+1, column=i+1)
                entries.setdefault(day, {})[time] = entry

        save_button = tk.Button(second_root, text="저장", command=save_timetable)
        save_button.grid(row=len(times) + 1, column=0, columnspan=len(days) + 1, sticky="ew", pady=10)

    # 메인 창 버튼들
    edit_button = tk.Button(root, text="시간표 설정", command=set_timetable, width=20)
    edit_button.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)

    exit_button = tk.Button(root, text="종료", command=exit_program, width=20)
    exit_button.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

    root.mainloop()
