import os
from datetime import datetime, timedelta

def formatTitle(name):
    name, _ = os.path.splitext(name)
    prefix, strdate, strtime, duration = name.split('-')
    date = datetime.strptime(strdate + strtime, '%Y%m%d%H%M%S')
    duration = str(timedelta(seconds=int(duration)))
    return '{} {:%Y-%m-%d %H:%M:%S} ({})'.format(prefix.capitalize(), date, duration[2:])

def video_to_dict(filename):
    return {
        'filename': filename,
        'title': formatTitle(filename),
        'm4v': '/media-lib/' + filename
    }
