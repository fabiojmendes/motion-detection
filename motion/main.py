#!/usr/bin/env python3

import time as tm
import cv2
import signal

from datetime import datetime
from video import VideoWriter

class Monitor:
    def __init__(self):
        self.running = True

    def stop_running(self, signum, frame):
        print("Stopping execution due to a {} signal".format(signal.Signals(signum).name))
        self.running = False

    def is_running(self):
        return self.running

def detect_motion(bgsub, frame):
    threshold = 127
    blurk = 13
    min_area = 100

    fgmask = bgsub.apply(frame)
    # cv2.imshow('Mask', fgmask) # cv2.resize(fgmask, (0,0), fx = 0.5, fy = 0.5))
    cv2.GaussianBlur(fgmask, (blurk, blurk), 0, dst = fgmask)
    # cv2.imshow('MaskBlur', fgmask) # cv2.resize(fgmask, (0,0), fx = 0.5, fy = 0.5))
    cv2.threshold(fgmask, threshold, 255, cv2.THRESH_BINARY, dst = fgmask)
    # cv2.imshow('Thresh', fgmask) # cv2.resize(fgmask, (0,0), fx = 0.5, fy = 0.5))

    cnts = cv2.findContours(fgmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
    cnts = [c for c in cnts if cv2.contourArea(c) > min_area]
    return cnts

def draw_text(frame, text):
    cv2.putText(frame, text, (10, frame.shape[0]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 1, cv2.LINE_AA)

def draw_countours(frame, cnts):
    for c in cnts:
        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        (x, y, w, h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

def main(args):
    frameSize = args.size
    frameRate = args.fps

    last_occupied = 0

    bgsub = cv2.createBackgroundSubtractorMOG2()

    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, frameSize[0])
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, frameSize[1])
    cam.set(cv2.CAP_PROP_FPS, frameRate)
    # cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

    mom = Monitor()
    signal.signal(signal.SIGTERM, mom.stop_running)
    signal.signal(signal.SIGINT, mom.stop_running)

    out = None
    template = "{:%A %d %B %Y %H:%M:%S} Frame Time: {:.0f}ms FPS: {:.1f}"

    try:
        if not cam.isOpened():
            raise IOError('Camera not open')

        # Discard first few frames
        for i in range(10):
            cam.read()

        print('Starting Motion Detection')
        start = tm.time()
        while mom.is_running():
            # Read next image
            ret, frame = cam.read()
            timestamp = tm.time()
            current_date = datetime.now()
            if not ret:
                raise IOError('Error reading frame')

            cnts = detect_motion(bgsub, frame)

            if cnts:
                last_occupied = timestamp
                draw_countours(frame, cnts)

            # draw the text and timestamp on the frame
            end = tm.time()
            frame_time = end - start
            start = end
            text = template.format(current_date, frame_time * 1000, 1/frame_time)
            draw_text(frame, text)
            # print(text, end = '\r')

            # cv2.imshow("mov", frame)
            if timestamp - last_occupied <= 1:
                if not out:
                    out = VideoWriter(frameSize, frameRate, current_date, args.codec, args.ext)
                out.write(frame)
            else:
                if out:
                    out.close()
                    out = None

    finally:
        cam.release()
        if out: out.close(wait=True)
        print("Goodbye")
