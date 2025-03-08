import datetime, logging

def todayVariable(isTest):
    # num_today = "MM-DD"
    # txt_today = "Monday"
    # now_time  = "HH:MM"
    # end_time  = "HH:MM" + 10 minutes
    today = datetime.datetime.today()
    if isTest:
        logging.debug("todayVariable MODE: TEST")
        num_today = "03-10"
        txt_today = "Tuesday"
        now_time = "12:21"
        end_time = "16:10"
        return num_today, txt_today, now_time, end_time
    else:
        num_today = today.strftime("%m-%d")
        txt_today = today.strftime("%A")
        now_time = today.strftime("%H:%M")
        end_time = (today + datetime.timedelta(minutes=10)).strftime("%H:%M")
        return num_today, txt_today, now_time, end_time