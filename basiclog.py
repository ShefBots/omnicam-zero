from datetime import datetime

def _get_datetime_string():
    return str(datetime.now())

_time_len_spaces = " " * (len(str(_get_datetime_string()))+2)

def log(message = ""):
    print(f"[{_get_datetime_string()}] {message}")

# Log that has the same indentation as log, but doesn't display the time.
def log_nt(message = ""):
    print(f"{_time_len_spaces} {message}")
