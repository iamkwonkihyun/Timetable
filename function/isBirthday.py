from win10toast import ToastNotifier
from data.data import BIRTHDAY

toaster = ToastNotifier()
oneNotification = set()

def isBirthday(today):
    if today == BIRTHDAY and today not in oneNotification:
        toaster.show_toast(
            "HAPPY BIRTHDAY!!!",
            "Today is your birthday!!🎂",
            duration=None,
            threaded=True
        )
        oneNotification.add(today)
        return True
    return False