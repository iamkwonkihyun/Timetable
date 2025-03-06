import time
import datetime
from plyer import notification
import win32com.client

# 프로그램 오픈 확인 후 알림창
def check_if_running(process_name):
    wmi = win32com.client.Dispatch("WbemScripting.SWbemLocator")
    service = wmi.ConnectServer(".", "root\\cimv2")
    process_list = service.ExecQuery(f"SELECT * FROM Win32_Process WHERE Name = '{process_name}'")
    return len(process_list) > 0

if check_if_running("Timetable.exe") == True:
    notification.notify(
        title="Hello!",
        message="Timetable.exe is Running!\nDon't worry, it is not hacking :)",
        timeout=10,
        toast=True,
    )
else:
    notification.notify(
        title="Error",
        message="fucking Error",
        timeout=10,
        toast=True,
    )


timetable = {
    "월요일": {"08:30": "네트워크 구축", "09:30": "네트워크 구축", "10:30": "네트워크 구축", "11:30": "네크워크 구축","12:20":"점심시간", "13:10": "일본어", "14:10": "미적분"},
    "화요일": {"08:30": "자료구조", "09:30": "자료구조", "10:30": "자료구조", "11:30": "일본어","12:20":"점심시간", "13:10": "성공적인 직업생활", "14:10": "응용프로그래밍", "15:10":"응용 프로그래밍"},
    "수요일": {"08:30": "스포츠", "09:30": "진로", "10:30": "성공적인 직업생활", "11:30": "응용 프로그래밍","12:20":"점심시간", "13:10": "응용 프로그래밍", "14:10": "미적분"},
    "목요일": {"08:30": "클라우드 보안", "09:30": "클라우드 보안", "10:30": "클라우드 보안", "11:30": "미적분","12:20":"점심시간", "13:10": "성공적인 직업생활", "14:10": "일본어", "15:10":"일본어"},
    "금요일": {"08:30": "빅데이터 분석", "09:30": "빅데이터 분석", "10:30": "빅데이터 분석", "11:30": "미적분","12:20":"점심시간", "13:10": "음악"},
}

today = datetime.datetime.today().strftime("%A")

kor_days = {
    "Monday": "월요일",
    "Tuesday": "화요일",
    "Wednesday": "수요일",
    "Thursday": "목요일",
    "Friday": "금요일",
    "Saturday": "토요일",
    "Sunday": "일요일"
}

today_kor = kor_days[today]

if today_kor in timetable:
    while True:
        now = datetime.datetime.now().strftime("%H:%M") # 현재 시간 구해서 변수로
        if now in timetable[today_kor]: # 현재 시간에 timetable[today_kor]에 있으면 아래 코드 실행
            subject = timetable[today_kor][now] # 현재 시간의 과목 가져오기
            notification.notify(
                title=f"{today_kor} 수업 알림",
                message=f"다음 교시: {subject}",
                timeout=10,
                toast=True,
            )
            time.sleep(60)
        strp_now = datetime.datetime.strptime(now, "%H:%M") + datetime.timedelta(minutes=10)
        endTime = strp_now.strftime("%H:%M")
        if endTime in timetable[today_kor]:
            notification.notify(
                title=f"{today_kor} 수업 알림",
                message=f"수업 끝나기 10분 전",
                timeout=10,
                toast=True,
            )
            time.sleep(60)
        
        time.sleep(1)
        
