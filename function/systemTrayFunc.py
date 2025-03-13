import tkinter as tk
from tkinter import messagebox
import json, sys
import os
from function.reminder import data_dir_func

def settings():
    FILE_PATH = data_dir_func("timetable.json")

    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            TIMETABLE = json.load(f)

    root = tk.Tk()
    root.title("시간표")
    root.geometry("500x500")
    
    days = list(TIMETABLE.keys())
    times = sorted({time for schedule in TIMETABLE.values() for time in schedule.keys()})

    entries = {}
        
    def exit_program():
        sys.exit()
    
    def set_timetable():
        
        def save_timetable():
            result = messagebox.askquestion("질문", "저장하시겠습니까?")
            if result == "yes":
                for day, schedule in entries.items():
                    for time, entry in schedule.items():
                        TIMETABLE[time][day] = entry.get()
                with open(FILE_PATH, "w", encoding="utf-8") as f:
                    json.dump(TIMETABLE, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("timetable", "저장 성공")
                second_root.destroy()
            else:
                messagebox.showinfo("timetable", "저장 실패")
        
        second_root = tk.Tk()
        second_root.title("timetable")
        second_root.geometry("1600x500")
        tk.Label(second_root, text="요일", width=10, borderwidth=0, relief="solid").grid(row=0, column=0)
        for i, day in enumerate(days):
            tk.Label(second_root, text=day, width=20, borderwidth=0, relief="solid").grid(row=0, column=i+1)

        for j, time in enumerate(times):
            tk.Label(second_root, text=time, width=10, borderwidth=0, relief="solid").grid(row=j+1, column=0)
            entries[time] = {}

            for i, day in enumerate(days):
                text = TIMETABLE.get(day, {}).get(time, "")
                entry = tk.Entry(second_root, width=20)
                entry.insert(0, text)
                entry.grid(row=j+1, column=i+1)
                entries[time][day] = entry
        
        save_button = tk.Button(second_root, text="저장", command=save_timetable)
        save_button.grid(row=len(times) + 1, column=0, columnspan=len(days) + 1, sticky="ew", pady=10)
        
    
    edit_button = tk.Button(root, text="시간표 설정", command=set_timetable, width=20)
    edit_button.grid(row=len(times) + 1, column=0, columnspan=len(days) + 1, sticky="ew", pady=10)
    
    exit_button = tk.Button(root, text="종료", command=exit_program, width=20)
    exit_button.grid(row=len(times) + 2, column=0, columnspan=len(days) + 2, sticky="ew", pady=10)

    root.mainloop()
