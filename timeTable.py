import time
import datetime
from win10toast_persist  import ToastNotifier

toaster = ToastNotifier()

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
        strp_now = datetime.datetime.strptime(now, "%H:%M") + datetime.timedelta(minutes=10)
        endTime = strp_now.strftime("%H:%M")
        if now in timetable[today_kor]: # 현재 시간에 timetable[today_kor]에 있으면 아래 코드 실행
            subject = timetable[today_kor][now] # 현재 시간의 과목 가져오기
            toaster.show_toast(
                f"{today_kor} 수업 알림",
                f"다음 교시: {subject}",
                duration=None,
                icon_path=None,
                threaded=True
            )
            time.sleep(60)
        
        if endTime in timetable[today_kor]:
            toaster.show_toast(
                f"{today_kor} 수업 알림",
                f"수업 끝나기 10분 전",
                duration=None,
                icon_path=None,
                threaded=True
            )
            time.sleep(60)
        
        time.sleep(1)