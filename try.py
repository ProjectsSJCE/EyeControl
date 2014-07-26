#import numpy as np
#import cv2

#WHITE = (255, 255, 255)
#RED = (0, 0, 255)
#BLACK = (0, 0, 0)


import thread
import threading
import math
import time
import pymouse
import multiprocessing as mp

mouse = pymouse.PyMouse()
GAZE_TIME = 5
INIT_POINT = None
GAZE_RADIUS = 50
GAZE_ITER = 0
is_GAZE = True
x1, y1 = mouse.position()
#time.sleep(1)
INIT_POINT = x1, y1

class SelfTimer(threading.Thread):

    def __init__(self, time):
    
        threading.Thread.__init__(self)
        self.stop_time = time
        self.x = INIT_POINT[0]
        self.y = INIT_POINT[1]
        
    def run(self):
    
        global is_GAZE, mouse
        i = 1
        while is_GAZE:
            print i
            if i == self.stop_time:
                mouse.click(self.x, self.y, 1)
                is_GAZE = False
                break
            i += 1
            time.sleep(2)
        
    def restart(self, x, y):
    
        global INIT_POINT
        INIT_POINT = x, y
        self.__init__(self.stop_time)
        self.run()

def run(timer_pipe):
    
        global is_GAZE,GAZE_TIME, mouse
        while True:
            data = timer_pipe.recv()
            if type(data) == bool:
                condition = data
            else:
                x, y = data
            i = 1
            while condition:
                print i
                data = timer_pipe.recv()
                if type(data) == bool:
                    condition = data
                else:
                    x, y = data
                if i == GAZE_TIME:
                    print x, y, "Fro click"
                    mouse.click(x, y, 1)
                    print "I clicked"
                    is_GAZE = False
                    break
                i += 1
                time.sleep(1)
                

#timer_thread = SelfTimer(GAZE_TIME)


def moveMouse():

    global INIT_POINT, GAZE_ITER, GAZE_RADIUS, mouse, is_GAZE
    INIT_POINT = None
    is_GAZE = False
    main_pipe, timer_pipe = mp.Pipe()
    a =  mp.Process(target=run, args=(timer_pipe, ))
    a.start()    
    while True:
        x, y = mouse.position()
        print x, y
        if INIT_POINT is None:
            INIT_POINT = x, y
            continue
        
        distance_moved = math.sqrt((x - INIT_POINT[0]) ** 2 + (y - INIT_POINT[1]) ** 2)
        if distance_moved < GAZE_RADIUS:
            is_GAZE = True
        else:
            INIT_POINT = x, y
            is_GAZE = False
        print "Gaze = ", is_GAZE
        time.sleep(1)
        main_pipe.send(is_GAZE)
        main_pipe.send(INIT_POINT)
    
moveMouse()
#class SelfTimer(threading.Thread):

#    def __init__(self, time, point):
#    
#        threading.Thread.__init__(self)
#        self.stop_time = time
#        self.point = point
#        
#    def run(self):
#    
#        i = 1
#        while True:
#            i += 1
#            x, y = mouse.position()
#            print x, y
#            time.sleep(1)
#            if i == self.stop_time:
#                mouse.click(x, y, 1)
#                break
##        self.restart()

#    def restart(self):
#    
#        self.__init__(self.stop_time, self.point)
#        self.run()
#        
#a = 100, 100
#timer_thread = SelfTimer(10, a)
#print timer_thread.start()
