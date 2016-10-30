import os
import functools
from datetime import datetime, timedelta

def formatDateTime(d, t):
    return '{}-{}-{} {}:{}:{}'.format(
        d[:4], d[4:6], d[6:8], t[:2], t[2:4], t[4:6])

def formatTitle(name):
    name, _ = os.path.splitext(name)
    prefix, strdate, strtime, duration = name.split('-')
    date = formatDateTime(strdate, strtime)
    duration = str(timedelta(seconds=int(duration)))
    return '{} {} ({})'.format(prefix.capitalize(), date, duration[2:])

@functools.lru_cache(maxsize=2048)
def video_to_dict(filename):
    return {
        'filename': filename,
        'title': formatTitle(filename),
        'm4v': '/media-lib/' + filename
    }
