import cv2
import os
from datetime import datetime

from threading import Thread
from queue import Queue

QueueFinished = object()

filename_tmpl = "video-{:%Y%m%d-%H%M%S}-{:03d}.{}"

class VideoWriter():
    def __init__(self, size, fps, date, codec, extension):
        self.date = date
        self.extension = extension
        self.fourcc = cv2.VideoWriter_fourcc(*codec) if codec else 0
        self.fps = fps
        self.size = size
        self.queue = Queue(maxsize = 32)
        thread = Thread(target=self.run)
        thread.start()

    def write(self, frame):
        self.queue.put(frame)

    def run(self):
        filename = '.' + filename_tmpl.format(self.date, 0, self.extension)
        print('Starting new video File [{}]'.format(filename))
        video = cv2.VideoWriter(filename, self.fourcc, self.fps, self.size)
        while True:
            f = self.queue.get()
            if f is QueueFinished:
                self.queue.task_done()
                break
            video.write(f)
            self.queue.task_done()
        duration = (datetime.now() - self.date).total_seconds()
        new_filename = filename_tmpl.format(self.date, round(duration), self.extension)
        print('Releasing resources for [{}] and renaming it to [{}]'.format(filename, new_filename))
        video.release()
        os.rename(filename, new_filename)

    def close(self, wait=False):
        self.queue.put(QueueFinished)
        if wait:
            self.queue.join()
