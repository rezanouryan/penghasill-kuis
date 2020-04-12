import pytz


def local_time(utc):
    local_timezone = pytz.timezone('Asia/Jakarta')
    local = utc.astimezone(local_timezone)
    return local.strftime('%B %d, %Y %X %Z')
