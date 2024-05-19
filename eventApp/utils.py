
def isPhoneNumber(param):
    if param.isdigit() and len(param) == 10:
        return True
    else:
        return False
