import wx
from pykeyboard import PyKeyboard
import time
import threading
import thread
import multiprocessing as mp
import time

MOUSE_HOVER = False
init = [1]
flag_g = [1]

class HoverTimer(threading.Thread):

    def __init__(self, button):
    
        threading.Thread.__init__(self)
        self.button = button
        self.main_pipe, self.timer_pipe = mp.Pipe()
        
    def run(self):
    
        global MOUSE_HOVER
        colour = ['red', 'yellow', 'green']
        i = 0
        while MOUSE_HOVER and i < 3:            
            self.button.SetBackgroundColour(colour[i%3])
#            self.button.SetBackgroundColour(colour[i])
            i += 1
#            time.sleep(0.25)

    def restart(self, button):
    
        self.button = button
        self.__init__(self.button)
        self.run()
        
def colour_timer(timer_pipe, colour_pipe):
    
    condition = timer_pipe.recv()
    colours = ['red', 'yellow', 'green']
    while True:
        condition = timer_pipe.recv()
        print condition, "cdon"
        i = 0
        while condition and i < 3:
            colour_pipe.send(colours[i])
#            time.sleep(0.5)
            condition = timer_pipe.recv()
            i += 1
            
class MyFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'EYE Typing Keypad', pos=(0, 0), size=wx.DisplaySize())
        self.panel = wx.Panel(self)
        self.keyboard_control = PyKeyboard()
        
        self.main_pipe_time, self.timer_pipe = mp.Pipe()
        self.main_pipe_colour, self.colour_pipe = mp.Pipe()
        mp.Process(target=colour_timer, args=(self.timer_pipe, self.colour_pipe)).start()
        
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
        for i in range(10,26):
            self.keys.append(chr(ord('a') + i))
        #self.keys.append('enter')
        
        i = 1
        self.hash = {}
        self.hash_label = {}
        self.key_buttons = []
        for key in self.keys:
            b = wx.Button(self.panel, i, key, size=wx.DLG_SZE(self, 50, 50))
            self.key_buttons.append(b)
#            self.Bind(wx.EVT_BUTTON, self.connect_keys, b)
            self.hash_label[i] = key
            self.hash[i] = b
#            if key == "space":
#                self.hash_label[i] = 'space'
#            elif key == "enter":
#                self.hash_label[i] = "\n"
            i += 1
#        print self.hash_label
#        assert False         
        i = 0
        j = 0
        self.keybox = []
        font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.BOLD)
        
        k = 1
        for button in self.key_buttons:
            if i % 7 == 0:
                if self.keybox != []:
                    self.keyboard.AddSpacer(40)
                    self.keyboard.Add(self.keybox[j])
                    j += 1
                self.keybox.append(wx.BoxSizer(wx.HORIZONTAL))
            button.Bind(wx.EVT_BUTTON, self.connect_keys)
#            button.Bind(wx.EVT_ENTER_WINDOW, self.change_colour)
#            button.Bind(wx.EVT_LEAVE_WINDOW, self.revert_colour)
            button.SetFont(font)
            self.keybox[j].Add(button)
            self.keybox[j].AddSpacer(40)
            i += 1
            k += 1       
#        print "done"        
#        self.init_keys()
#        button.Bind(wx.EVT_BUTTON, self.connect_keys)
        print "overwritten"
        self.keyboard.AddSpacer(40)
        self.keyboard.Add(self.keybox[j])
        self.outer_box.Add(self.keyboard, border=5, flag=wx.ALL)    
        self.panel.SetSizer(self.outer_box)  
        
    def change_colour(self, event_change_colour):
        
        global MOUSE_HOVER
        i = event_change_colour.GetId()
        self.colour_changed = i
        button = self.hash[i]
        print "enter ",self.colour_changed
#        print "entered"
        button.SetBackgroundColour('red')
#        button.Bind(wx.EVT_BUTTON, self.connect_keys)#add key to the textbox
#        wx.CallLater(20, self.change_colour, event)
#        self.main_pipe_time.send(True)
#        colour = self.main_pipe_colour.recv()
#        print colour
#        button.SetBackgroundColour(colour)
        return
        
    def revert_colour(self, event_revert_colour):
        
#        print "left"
        global MOUSE_HOVER
        MOUSE_HOVER = False
        print "left ", self.colour_changed
#        self.main_pipe_time.send(False)
        button = self.hash[self.colour_changed]
        button.SetBackgroundColour('lightgrey')
        button.Bind(wx.EVT_BUTTON, self.connect_keys)
        return
        
    def init_keys(self):
    
#        for k in self.hash_label.keys():
#            button = self.hash[k]
        for button in self.key_buttons:
#                print "simulating"
            event = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, button.GetId())
            wx.PostEvent(button, event)
        return
        
    def connect_keys(self, event_connect_keys):
        
        i = event_connect_keys.GetId()
        self.colour_changed = i
#        self.colour_changed = i
        print "clicked ", i        
#        self.colour_changed = i
        label = self.hash_label[i]
        button = self.hash[i]
#        if init[0] == 0:
#        if True:
#           if label == "space":
#                label = " "
#           else:
#                label = "\n"
        self.keyboard_control.type_string(label)
        self.initial_text = self.text.GetValue()
        self.text.SetValue(self.initial_text + label)
#           print "pressed"
#            self.colour_changed = i
#            button.SetBackgroundColour('red')
#            print init[0]
#        else:
#            print "came here binded"
        button.Bind(wx.EVT_ENTER_WINDOW, self.change_colour)
        button.Bind(wx.EVT_LEAVE_WINDOW, self.revert_colour)
#        if button.GetId() == len(self.key_buttons):
#            init[0] = 0
        return    
    
    def update_text(self, letter):
        
        initial_text = self.text.GetValue()
        self.text.SetValue(initial_text + letter)

    def dummy(self, event_dummy):
    
        print "howdy"
        i = event_dummy.GetId()
        label = self.hash_label[i]
        button = self.hash[i]
        button.Bind(wx.EVT_ENTER_WINDOW, self.change_colour)
        button.Bind(wx.EVT_LEAVE_WINDOW, self.revert_colour)
                        
class MyApp (wx.App) :
    
    def OnInit (self) :
        frame = MyFrame()
#        frame.init_keyboard()
        frame.Show(True)
        return True
        
def test () :
    app_our = MyApp(0)
    app_our.MainLoop()

if __name__ == '__main__':
    test()

