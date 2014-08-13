#eye detetction and moving mouse position according to gaze gesture
# requrement: numpy + opencv2.7.3 + scipy + pymouse or pyserinput 
import sys
import time
import random
import multiprocessing as mp
import cv2
import numpy as np
import scipy.optimize as so
import pymouse
import math
from datetime import datetime
import wx
from pykeyboard import PyKeyboard

CALIB_WINDOW = 'CALIBRATION WINDOW'
PUPIL_WINDOW = 'PUPIL_WINDOW'
PUPIL_THRESH_WINDOW = 'PUPIL_THRESH_WINDOW'
cam_index = 0

# instantiate objects
ESC = u'\x1b'
VIDEO_INTERVAL = 20
FRAME_WIDTH = 320
FRAME_HEIGHT = 240
CIRCLE_RADIUS = 15
CIRCLE_PADDING = 20
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
YELLOW = (30, 255, 255)

CALIBRATION_WAIT_TIME = 1000
GAZE_TIME = 5
INIT_POINT = None
GAZE_RADIUS = 50 #Where each unit is approx. the length of a pixel diagonal of the screen
BASE_TIME = datetime.now()

mouse = pymouse.PyMouse()

START_SAVING_POINT = 'START_SAVING_POINT'
STOP_SAVING_POINT = 'STOP_SAVING_POINT'
CALIBRATION_DONE = 'CALIBRATION_DONE'
VALIDATION_DONE = 'VALIDATION_DONE'

class CalibPoint:
    def __init__(self, sx, sy):
        self.sx = sx
        self.sy = sy
        self.ex = []
        self.ey = []

def draw_circle(image, x, y, radius, color1, color2):
    cv2.circle(image, (x, y), radius, color1, -1)
    cv2.circle(image, (x, y), 5, color2, -1)
    cv2.imshow(CALIB_WINDOW, image)

def save_calib_points(sx, sy, queue, calib_point):
    for r in range(0, 10):
        while queue.empty():
            cv2.waitKey(20)
        pupil_center = queue.get()
        calib_point.ex.append(pupil_center[0])
        calib_point.ey.append(pupil_center[1])
        # cv2.waitKey(20)

def model(X, a0, a1, a2, a3, a4, a5):
    x = X[:, 0]
    y = X[:, 1]

    return a0 + a1 * x + a2 * y + a3 * x * y + a4 * x ** 2 + a5 * y ** 2

def moveMouse(mouse, point):

    global INIT_POINT, GAZE_RADIUS, BASE_TIME
    
    x1, y1 = mouse.position()
    elapsed_time = (datetime.now() - BASE_TIME).seconds
    x2, y2 = point
    # print x1, y1, x2, y2
    x_distance = float(x2 - x1)
    y_distance = float(y2 - y1)
    
    if INIT_POINT is None:
        INIT_POINT = x1, y1
    
    #we first calculate how much the mouse has moved from the initial point
    init_x_distance = float(x2 - INIT_POINT[0])
    init_y_distance = float(y2 - INIT_POINT[1])    
    
    #we are interested in determining if the mouse lies inside a circle of GAZE_RADIUS for GAZE_TIME
    distance_moved = (math.sqrt(init_x_distance ** 2 + init_y_distance ** 2))
    
    if distance_moved < GAZE_RADIUS:
        if elapsed_time >= GAZE_TIME:
            mouse.click(INIT_POINT[0], INIT_POINT[1], 1)            
    else:
        INIT_POINT = x1, y1
        BASE_TIME = datetime.now()
        #Since the mouse has moved away from that cirlce, we keep a new base time and repeat the process
        
    intervals = 10
    delay = 0.2
    for r in range(0, intervals):
        x = int(x1 + r * (x_distance / intervals))
        y = int(y1 + r * (y_distance / intervals))
        mouse.move(x, y)
        time.sleep(delay / intervals)

# Calibration Screen #
# This function shows the calibration Screen in order to record 
# the vision range with respect to the eye video frame
def showCalibrationScreen(screen_width, screen_height, calib_pipe, calib_queue):
    cv2.namedWindow(CALIB_WINDOW)#, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(CALIB_WINDOW, cv2.WND_PROP_FULLSCREEN, cv2.cv.CV_WINDOW_FULLSCREEN)

    shape = screen_height, screen_width, 3
    calib = np.zeros(shape, dtype=np.uint8)

    text = 'Gaze at the Circles'
    (text_width, text_height), text_baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, 3.0, 4)
    text_x = screen_width / 2 - text_width / 2
    text_y = screen_height / 2 - text_height / 2
    cv2.putText(calib, text, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN, 3.0, YELLOW, 4, cv2.CV_AA)
    cv2.imshow(CALIB_WINDOW, calib)
    cv2.waitKey(1500)
    cv2.rectangle(calib, (text_x, text_y - text_height * 2), (text_x + text_width, text_y + text_height * 2), (0, 0, 0), -1)
    cv2.imshow(CALIB_WINDOW, calib)

    # create an empty dictionary for 10 calibration points
    calib_points = {}

    # 1. centre
    sx, sy = screen_width / 2, screen_height / 2 
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(CALIBRATION_WAIT_TIME)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[1] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[1])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    # 2. up
    sx, sy = screen_width / 2, CIRCLE_RADIUS + CIRCLE_PADDING
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(CALIBRATION_WAIT_TIME)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[2] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[2])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    # 3. bottom
    sx, sy = screen_width / 2, screen_height - CIRCLE_RADIUS - CIRCLE_PADDING
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(CALIBRATION_WAIT_TIME)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[3] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[3])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    # 4. left
    sx, sy = CIRCLE_RADIUS + CIRCLE_PADDING, screen_height / 2
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(CALIBRATION_WAIT_TIME)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[4] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[4])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    # 5. right
    sx, sy = screen_width - CIRCLE_RADIUS - CIRCLE_PADDING, screen_height / 2
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(CALIBRATION_WAIT_TIME)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[5] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[5])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    # 6. upper left
    sx, sy = CIRCLE_RADIUS + CIRCLE_PADDING, CIRCLE_RADIUS + CIRCLE_PADDING
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(1000)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[6] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[6])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    # 7. upper right
    sx, sy = screen_width - CIRCLE_RADIUS - CIRCLE_PADDING, CIRCLE_RADIUS + CIRCLE_PADDING
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(CALIBRATION_WAIT_TIME)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[7] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[7])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    # 8. lower left
    sx, sy = CIRCLE_RADIUS + CIRCLE_PADDING, screen_height - CIRCLE_RADIUS - CIRCLE_PADDING
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(CALIBRATION_WAIT_TIME)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[8] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[8])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    # 9. lower right
    sx, sy = screen_width - CIRCLE_RADIUS - CIRCLE_PADDING, screen_height - CIRCLE_RADIUS - CIRCLE_PADDING
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(CALIBRATION_WAIT_TIME)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[9] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[9])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    # 10. centre
    sx, sy = screen_width / 2, screen_height / 2
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, WHITE, RED)
    cv2.waitKey(CALIBRATION_WAIT_TIME)
    calib_pipe.send(START_SAVING_POINT)
    calib_points[10] = CalibPoint(sx, sy)
    save_calib_points(sx, sy, calib_queue, calib_points[10])
    calib_pipe.send(STOP_SAVING_POINT)
    draw_circle(calib, sx, sy, CIRCLE_RADIUS, BLACK, BLACK)

    text = 'Calibration Is Done.'
    (text_width, text_height), text_baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_PLAIN, 3.0, 4)
    text_x = screen_width / 2 - text_width / 2
    text_y = screen_height / 2 - text_height / 2
    cv2.putText(calib, text, (text_x, text_y), cv2.FONT_HERSHEY_PLAIN, 3.0, YELLOW, 4, cv2.CV_AA)
    cv2.imshow(CALIB_WINDOW, calib)
    cv2.waitKey(1000)

    cv2.destroyWindow(CALIB_WINDOW)

    return calib_points

def normalize(n, limit):
    return (n - limit / 2.) / (limit / 2.)

def denormalize(n, limit):
    d = (n * limit / 2.) + (limit / 2.)
    if d < CIRCLE_PADDING:
        d = CIRCLE_PADDING
    if d > limit - CIRCLE_PADDING:
        d = limit - CIRCLE_PADDING
    return d

def calibrate(screen_width, screen_height, calib_pipe, calib_queue):
    calib_points = showCalibrationScreen(
        screen_width, screen_height, calib_pipe, calib_queue)
    
    ex = np.array([], dtype=float)
    ey = np.array([], dtype=float)
    sx = np.array([], dtype=float)
    sy = np.array([], dtype=float)
    for p in [1, 2, 3, 4, 5, 6]:
        ex = np.append(ex, sum(calib_points[p].ex) / len(calib_points[p].ex))
        ey = np.append(ey, sum(calib_points[p].ey) / len(calib_points[p].ey))
        sx = np.append(sx, calib_points[p].sx)
        sy = np.append(sy, calib_points[p].sy)
    ex = normalize(ex, FRAME_WIDTH)
    ey = normalize(ey, FRAME_HEIGHT)
    sx = normalize(sx, screen_width)
    sy = normalize(sy, screen_height)
    # print ex; print ey; print sx; print sy

    epoints = np.column_stack([ex, ey])
    
    a, pcov = so.curve_fit(model, epoints, sx)
    b, pcov = so.curve_fit(model, epoints, sy)
    # print a, b
 
    calib_pipe.send([a, b])

    calib_pipe.send(CALIBRATION_DONE)

def mapPoint(ex, ey, a, b):
    zx =  a[0] + a[1] * ex + a[2] * ey + a[3] * ex * ey + a[4] * ex ** 2 + a[5] * ey ** 2
    zy =  b[0] + b[1] * ex + b[2] * ey + b[3] * ex * ey + b[4] * ex ** 2 + b[5] * ey ** 2
    return zx, zy

def validate(screen_width, screen_height, calib_pipe, calib_queue, a, b):
    valid_points = showCalibrationScreen(
        screen_width, screen_height, calib_pipe, calib_queue)

    ex = np.array([], dtype=float)
    ey = np.array([], dtype=float)
    sx = np.array([], dtype=float)
    sy = np.array([], dtype=float)
    for p in [1, 2, 3, 4, 5, 6]:
        ex = np.append(ex, sum(valid_points[p].ex) / len(valid_points[p].ex))
        ey = np.append(ey, sum(valid_points[p].ey) / len(valid_points[p].ey))
        sx = np.append(sx, valid_points[p].sx)
        sy = np.append(sy, valid_points[p].sy)
    ex = normalize(ex, FRAME_WIDTH)
    ey = normalize(ey, FRAME_HEIGHT)
    sx = normalize(sx, screen_width)
    sy = normalize(sy, screen_height)

    zx, zy = mapPoint(ex, ey, a, b)

    err_x = zx - sx
    err_y = zy - sy

    err_dist = np.sqrt(err_x ** 2 + err_y ** 2)
    err_rms = np.sum(err_dist * err_dist) / len(err_dist)

    print '-----------------------'
    print 'Mean Square Error: %.2f' % err_rms
    print '-----------------------'

    calib_pipe.send(float(err_rms))
    calib_pipe.send(VALIDATION_DONE)

class MyFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'EYE Typing Keypad', pos=(0, 0), size=wx.DisplaySize())
        self.panel = wx.Panel(self)
        self.keyboard_control = PyKeyboard()
        
        #place to store what is being entered
        font1 = wx.Font(10, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.BOLD)
        self.text = wx.TextCtrl(self.panel, 30, "", size=wx.DLG_SZE(self, 500, 40))
        self.text.SetFont(font1)
        self.outer_box = wx.BoxSizer(wx.VERTICAL)
        self.outer_box.Add(self.text, border=5, flag=wx.ALL)
        
        #place to make the actual keyboard
        self.keyboard = wx.BoxSizer(wx.VERTICAL)
        self.keys = [chr(ord('a') + i) for i in range(10)]
        self.keys.append('space')

#        chr(ord('a')) + i
        self.keys = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'space', 'p', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm']
        
        i = 1
        self.hash = {}
        self.hash_label = {}
        self.key_buttons = []
        for key in self.keys:
            b = wx.Button(self.panel, i, key, size=wx.DLG_SZE(self, 50, 50))
            self.key_buttons.append(b)
            self.Bind(wx.EVT_BUTTON, self.connect_keys, b)
            self.hash_label[i] = key
            self.hash[i] = b
            if key == "space":
                self.hash_label[i] = 'spc'
            i += 1

        i = 0
        j = 0
        self.keybox = []
        font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.BOLD)
        
        k = 1
        self.flag = [False] * 28
        for button in self.key_buttons:
            if i % 7 == 0:
                if self.keybox != []:
                    self.keyboard.AddSpacer(40)
                    self.keyboard.Add(self.keybox[j])
                    j += 1
                self.keybox.append(wx.BoxSizer(wx.HORIZONTAL))
            button.Bind(wx.EVT_ENTER_WINDOW, self.change_colour)
            button.Bind(wx.EVT_LEAVE_WINDOW, self.revert_colour)
            button.SetFont(font)
            self.keybox[j].Add(button)
            self.keybox[j].AddSpacer(40)
            i += 1
            k += 1       

        self.keyboard.AddSpacer(40)
        self.keyboard.Add(self.keybox[j])
        self.outer_box.Add(self.keyboard, border=5, flag=wx.ALL)    
        self.panel.SetSizer(self.outer_box)
        
    def change_colour(self, event_change_colour):
        
        global GAZE_RADIUS
        i = event_change_colour.GetId()
        self.colour_changed = i
        button = self.hash[i]
        self.flag[i] = True
        button.SetBackgroundColour('red')
        if self.flag[i] is True:
            wx.CallLater(int((GAZE_RADIUS/3)*1000), self.colour_change, i, "yellow")
        
    def colour_change(self, i, colour):
        
        button = self.hash[i]
        if self.flag[i] is True:
            button.SetBackgroundColour(colour)
            if self.flag[i] is True:
                wx.CallLater(int((GAZE_RADIUS/3)*1000), self.connect_keys, i)
        
    def revert_colour(self, event_revert_colour):
        
        i = self.colour_changed
        self.flag[i] = False
        button = self.hash[self.colour_changed]
        button.SetBackgroundColour('lightgrey')

    def connect_keys(self, i):
        
        self.colour_changed = i
        label = self.hash_label[i]
        button = self.hash[i]
        if label == "spc":
                label = "__"
        if self.flag[i] is True:
            button.SetBackgroundColour("green")
        if self.flag[i] is True:
            self.keyboard_control.type_string(label)
            self.initial_text = self.text.GetValue()
            self.text.SetValue(self.initial_text + label)
        return    
    
    def update_text(self, letter):
        
        initial_text = self.text.GetValue()
        self.text.SetValue(initial_text + letter)

class MyApp (wx.App) :
    
    def OnInit (self) :
        frame = MyFrame()
        frame.Show(True)
        return True
        
def test () :
    app_our = MyApp(0)
    app_our.MainLoop()

if __name__ == '__main__':
    '''
    main module for detecting the pupil
    '''
    # instantiate a mouse object
#    mouse = pymouse.PyMouse()

    screen_width, screen_height = mouse.screen_size()
    screen_rect = (0, 0, screen_width, screen_height)

    # create pipe between main and clibration
    # processes to exchange data between them
    main_pipe, calib_pipe = mp.Pipe()

    calib_queue = mp.Queue()

    calib_process = None
    calib_message = None
    is_calib_process_done = False
    is_valid_process_done = False
    err_rms = 1

    cam = cv2.VideoCapture(cam_index)

    while True:
        try:
            # video capture
            ret, frame = cam.read()
            if frame is None:
                continue
            
            # resize the image
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

            # flip the frame 
            frame = cv2.flip(frame, 1)
            
            # fram gray scale
            frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 

            # reverted the grayscaled image
            frame_gray = cv2.bitwise_not(frame_gray)
            
            # do the binary threshold to have a black & white image
            ret,thresh = cv2.threshold(frame_gray, 200, 255, cv2.THRESH_BINARY)

            # findContours changes the input so use a copy
            thresh_copy = np.copy(thresh)

            contours, hierarchy = cv2.findContours(thresh_copy,cv2.cv.CV_RETR_EXTERNAL,cv2.cv.CV_CHAIN_APPROX_NONE)
            
            if len(contours) == 0:
                continue
            # draw contours
            draw_contours = cv2.drawContours(thresh,contours, -1, WHITE, -1)
            
            # -------------------------------------------------
            # max ellipse with NO axis ratio treshold
            # -------------------------------------------------
            # find max contour
            # area_max = 0
            # for contour in contours:
            #     area = cv2.contourArea(contour)
            #     if area > area_max:
            #         area_max = area
            #         contour_max = contour

            # contours with 4 or less points cannot fit an ellipse
            # if len(contour_max) < 5:
            #     continue

            # fit an ellipse within max contour
            # ellipse = cv2.fitEllipse(contour_max)

            # -------------------------------------------------
            # BEGIN max ellipse with axis ratio treshold
            # -------------------------------------------------
            # sort contours by area
            for i in range(0, len(contours)):
                for j in range(1, len(contours)):
                    area1 = cv2.contourArea(contours[i])
                    area2 = cv2.contourArea(contours[j])
                    if area1 < area2:
                        contour_tmp = contours[i]
                        contours[i] = contours[j]
                        contours[j] = contour_tmp

            # select the first contour with axis ratio > threshold
            for contour in contours:
                if len(contour) < 5:
                    continue
                e = cv2.fitEllipse(contour)
                axis_a = min(e[1][0], e[1][1])
                axis_b = max(e[1][0], e[1][1])
                ratio = axis_a / axis_b
                # print ratio
                if ratio > 0.6:
                    ellipse = e
                    break

            if ellipse is None:
                continue
            # -------------------------------------------------
            # max ellipse with axis ratio treshold END
            # -------------------------------------------------

            ellipse_centre = (int(ellipse[0][0]), int(ellipse[0][1]))
            
            # draw green ellipse around iris and pupil centre      
            cv2.ellipse(frame, ellipse, GREEN, 2)
            cv2.circle(frame, ellipse_centre, 2, GREEN, 1)

            # Display the thresh window
            cv2.imshow(PUPIL_THRESH_WINDOW, thresh)
            # display the frame with detected eye
            cv2.imshow(PUPIL_WINDOW, frame)

            # key to exit or run the calibration or validation process
            key = cv2.waitKey(VIDEO_INTERVAL)
            if key > -1:
                key = unichr(key).upper()
            if key == ESC:
                break
            elif key == u'C':
                calib_process = mp.Process(target=calibrate,
                    args=(screen_width, screen_height, calib_pipe, calib_queue))
                calib_process.start()
                is_calib_process_done = False
            elif key == u'V' and is_calib_process_done:
                valid_process = mp.Process(target=validate,
                    args=(screen_width, screen_height, calib_pipe, calib_queue, a, b))
                valid_process.start()
                is_calib_process_done = True
            
            elif key == u'K':# and is_calib_process_done:
                mp.Process(target=test).start()
            
            if main_pipe.poll():
                data_recv = main_pipe.recv()
                if type(data_recv) == str:
                    if data_recv == START_SAVING_POINT or data_recv == STOP_SAVING_POINT:
                        calib_message = data_recv
                    elif data_recv == CALIBRATION_DONE:
                        is_calib_process_done = True
                    elif data_recv == VALIDATION_DONE:
                        is_valid_process_done = True
                elif type(data_recv) == list:
                    [a, b] = data_recv
                    # print a, b
                elif type(data_recv) == float:
                    err_rms = data_recv

            if calib_message == START_SAVING_POINT:
                # add the detected center to the queue
                calib_queue.put(ellipse_centre)
            else:
                # clear the queue
                while not calib_queue.empty():
                    calib_queue.get()

            if is_calib_process_done and is_valid_process_done and err_rms <= 0.5:
                x, y = ellipse_centre
                x = normalize(x, FRAME_WIDTH)
                y = normalize(y, FRAME_HEIGHT)
                sx, sy = mapPoint(x, y, a, b)
                sx = denormalize(sx, screen_width)
                sy = denormalize(sy, screen_height)
#                 print sx, sy

                moveMouse(mouse, (sx, sy))
#                moveMouse(mouse, (x, y))
        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise
            pass

    cv2.destroyAllWindows()
