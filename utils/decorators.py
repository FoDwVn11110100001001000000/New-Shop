from functools import wraps
from utils.logs import log

def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.exception(f"💥 Error in func '{func.__name__}': {type(e).__name__} — {e}")
    return wrapper