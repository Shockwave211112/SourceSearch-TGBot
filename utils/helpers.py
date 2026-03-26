from core.config import settings

def check_useless_hostname(current_value: str):
    if current_value in settings.USELESS_HOSTS:
        return True
    return False