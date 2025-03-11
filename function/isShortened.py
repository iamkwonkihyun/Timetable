import logging

isActivated = False

def isShortened(): 
    """단축 수업 인지 확인하는 함수

    Returns:
        bool: systemTray에서 클릭할 때 마다 isActivated가 바뀜
    """
    global isActivated
    
    if isActivated == True:
        isActivated = False
        return True
    elif isActivated == False:
        isActivated = True
        return False