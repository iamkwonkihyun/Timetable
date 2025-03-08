import logging

def isWeekday(today, isTest, want):
    if isTest:
        logging.debug("isWeekday MODE: TEST")
        if want:
            return True
        else:
            return False
    else:
        if today in ["Saturday", "Sunday"]:
            return False
        else:
            return True
        