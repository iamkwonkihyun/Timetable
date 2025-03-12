import tkinter as tk
import json, sys
import os
from function.filePath import data_dir_func

def settings():
    # 저장할 파일 경로
    FILE_PATH = data_dir_func("timetable.json")

    # 기존 시간표 데이터 불러오기
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            TIMETABLE = json.load(f)

    # tkinter 윈도우 생성
    root = tk.Tk()
    root.title("시간표")
    root.geometry("1600x600")

    # 요일 및 시간 추출
    days = list(TIMETABLE.keys())  # 요일 리스트
    times = sorted({time for schedule in TIMETABLE.values() for time in schedule.keys()})  # 모든 시간 정렬

    # Entry 저장할 딕셔너리
    entries = {}

    # 헤더 (시간 & 요일)
    tk.Label(root, text="요일", width=10, borderwidth=0, relief="solid").grid(row=0, column=0)  # 좌측 상단
    for i, day in enumerate(days):
        tk.Label(root, text=day, width=20, borderwidth=0, relief="solid").grid(row=0, column=i+1)  # 요일 가로 정렬

    for j, time in enumerate(times):
        tk.Label(root, text=time, width=10, borderwidth=0, relief="solid").grid(row=j+1, column=0)  # 시간 세로 정렬
        entries[time] = {}

        for i, day in enumerate(days):
            text = TIMETABLE.get(day, {}).get(time, "")  # 시간표에 해당 시간이 없으면 빈칸
            entry = tk.Entry(root, width=20)
            entry.insert(0, text)
            entry.grid(row=j+1, column=i+1)  # 시간별로 세로 정렬
            entries[time][day] = entry


    # 저장 함수 (덮어쓰기)
    def save_timetable():
        for day, schedule in entries.items():
            for time, entry in schedule.items():
                TIMETABLE[time][day] = entry.get()
        
        # JSON 파일로 저장 (덮어쓰기)
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(TIMETABLE, f, ensure_ascii=False, indent=4)
            
    def exit_program():
        sys.exit()

    # 저장 버튼 추가
    save_button = tk.Button(root, text="저장", command=save_timetable)
    save_button.grid(row=len(times) + 1, column=0, columnspan=len(days) + 1, sticky="ew", pady=10)
    
    exit_button = tk.Button(root, text="종료", command=exit_program)
    exit_button.grid(row=len(times) + 2, column=0, columnspan=len(days) + 2, sticky="ew", pady=10)

    root.mainloop()
