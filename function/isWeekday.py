import logging

def isWeekday(today:str, isTest:bool, want:bool):
    """오늘이 주말인지 주중인지 확인하는 함수

    Args:
        today (str): 오늘 요일을 받음
        isTest (bool): 테스트 할 때
        want (bool): 주중, 주말을 설정할 수 있음( isTest=True 일 때 )

    Returns:
        bool: 오늘이 주말이면 False를 주중이면 True를 반환
    """
    if isTest:
        logging.debug("isWeekday Function: TEST MODE")
        if want:
            return True
        else:
            return False
    else:
        if today not in ["Saturday", "Sunday"]:
            return True
        else:
            return False
        