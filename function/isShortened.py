import logging

isActivated = False

def isShortened(): 
    global isActivated
    logging.debug(1)
    
    if isActivated == True:
        isActivated = False
        logging.debug(2)
        return True
    elif isActivated == False:
        isActivated = True
        logging.debug(3)
        return False