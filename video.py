import cv2
import os

from threading import Thread
from queue import Queue

# codec = 'MJPG'
# container = 'mkv'

codec = 'XVID'
container = 'mkv'

# codec = 'VP90'
# container = 'webm'

fourcc = cv2.VideoWriter_fourcc(*codec)

QueueFinished = object()

class VideoWriter():
    def __init__(self, size, fps, date):
        self.filename = ".video-{:%Y%m%d-%H%M%S}.{}".format(date, container)
        self.video = cv2.VideoWriter(self.filename, fourcc, fps, size)
        self.queue = Queue(maxsize = 32)
        self.thread = Thread(target=self.run)
        self.thread.start()

    def write(self, frame):
        self.queue.put(frame)

    def run(self):
        print('Starting new video File [{}]'.format(self.filename[1:]))
        while True:
            f = self.queue.get()
            if f is QueueFinished:
                break
            self.video.write(f)
            self.queue.task_done()
        self.queue.task_done()
        print('Releasing resources for [{}]'.format(self.filename[1:]))
        self.video.release()
        os.rename(self.filename, self.filename[1:])

    def close(self, wait=False):
        self.queue.put(QueueFinished)
        if wait:
            self.queue.join()
