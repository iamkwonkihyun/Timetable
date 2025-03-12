import datetime, logging

def todayVariable(isTest):
    """오늘 요일, 시간 정보를 알려주는 함수

    Args:
        isTest (bool): 테스트 할 때

    Returns:
        all_returns(str): 오늘 요일, 날짜, 끝나는 시간 등 반환
        
        || num_today = "MM-DD" || txt_today = "Monday" || now_time  = "HH:MM" || end_time  = "HH:MM" + 10 minutes ||
    """
    today = datetime.datetime.today()
    if isTest:
        logging.debug("todayVariable MODE: TEST")
        num_today = "03-11"
        txt_today = "Tuesday"
        now_time = "12:2"
        end_time = "16:1"
        return num_today, txt_today, now_time, end_time
    else:
        num_today = today.strftime("%m-%d")
        txt_today = today.strftime("%A")
        now_time = today.strftime("%H:%M")
        end_time = (today + datetime.timedelta(minutes=10)).strftime("%H:%M")
        return num_today, txt_today, now_time, end_time