import time
import datetime
from win10toast_persist  import ToastNotifier

toaster = ToastNotifier()

timetable = {
    "월요일": {"08:30": "네트워크 구축", "09:30": "네트워크 구축", "10:30": "네트워크 구축", "11:30": "네크워크 구축","12:00":"점심시간", "13:10": "일본어", "14:10": "미적분"},
    "화요일": {"08:30": "자료구조", "09:30": "자료구조", "10:30": "자료구조", "11:30": "일본어","12:00":"점심시간", "13:10": "성공적인 직업생활", "14:10": "응용프로그래밍", "15:10":"응용 프로그래밍"},
    "수요일": {"08:30": "스포츠", "09:30": "진로", "10:30": "성공적인 직업생활", "11:30": "응용 프로그래밍","12:00":"점심시간", "13:10": "응용 프로그래밍", "14:10": "미적분"},
    "목요일": {"08:32": "클라우드 보안", "09:30": "클라우드 보안", "10:30": "클라우드 보안", "11:30": "미적분","12:00":"점심시간", "13:10": "성공적인 직업생활", "14:10": "일본어", "15:10":"일본어"},
    "금요일": {"08:30": "빅데이터 분석", "09:30": "빅데이터 분석", "10:30": "빅데이터 분석", "11:30": "미적분","12:00":"점심시간", "13:10": "음악"},
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
        now = datetime.datetime.now().strftime("%H:%M")
        
        if now in timetable[today_kor]:
            subject = timetable[today_kor][now]
            toaster.show_toast(
                f"{today_kor} 수업 알림",
                f"다음 교시: < {subject} >",
                duration=None,
                icon_path=None,
                threaded=True
            )
        
        time.sleep(20)
        
        