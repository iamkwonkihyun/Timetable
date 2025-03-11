yesterday = None

def resetVariable(today:str):
    """하루가 지나면 특정 변수를 초기화 시키는 함수

    Args:
        today (str): 오늘 요일의 값을 받고 어제와 요일이 다르면 변수를 초기화 시킴 

    Returns:
        boolean: 어제와 요일이 같으면 False를, 어제와 요일이 다르면 True를 반환
    """
    global yesterday
    
    if yesterday == None:
        yesterday = today
    
    if yesterday != today:
        yesterday = today
        return True
    else:
        return False