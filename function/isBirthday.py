from win10toast import ToastNotifier
from data.data import BIRTHDAY
import logging

toaster = ToastNotifier()
oneNotification = set()

def isBirthday(today):
    if today == BIRTHDAY and today not in oneNotification:
        logging.info("HAPPY BIRTHDAY TO YOU!!!")
        toaster.show_toast(
            "HAPPY BIRTHDAY!!!",
            "Today is your birthday!!🎂",
            duration=None,
            threaded=True
        )
        oneNotification.add(today)