from win10toast import ToastNotifier
from data.all_data import BIRTHDAY
import logging

toaster = ToastNotifier()
oneNotification = set()

def isBirthday(today:str):
    """오늘이 생일이면 축하해주는 함수

    Args:
        today (str): 오늘 요일(num_today(ex. 01-01))을 받아옴 
    """
    if today == BIRTHDAY and today not in oneNotification:
        logging.info("HAPPY BIRTHDAY TO YOU!!!")
        toaster.show_toast(
            "HAPPY BIRTHDAY TO YOU!!!",
            "Today is your birthday!!🎂",
            duration=None,
            threaded=True
        )
        oneNotification.add(today)