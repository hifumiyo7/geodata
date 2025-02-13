
def isIP(ipAddress: str) -> bool:
    ip = ipAddress.split(".")
    if len(ip) != 4:
        return False
    for i in ip:
        if not i.isdigit():
            return False
        i = int(i)
        if i < 0 or i > 255:
            return False
    return True
