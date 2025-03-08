yesterday = None

def resetVariable(today):
    global yesterday
    
    if yesterday == None:
        yesterday = today
    
    if yesterday != today:
        yesterday = today
        return True
    else:
        return False