import wx
from pykeyboard import PyKeyboard
import time
import threading
import thread
import multiprocessing as mp

MOUSE_HOVER = False

#class HoverTimer(threading.Thread):

#    def __init__(self, button):
#    
#        threading.Thread.__init__(self)
#        self.button = button
#        self.main_pipe, self.timer_pipe = mp.Pipe()
#        
#    def run(self):
#    
#        global MOUSE_HOVER
#        colour = ['red', 'yellow', 'green']
#        i = 0
#        while MOUSE_HOVER and i < 3:            
#            self.button.SetBackgroundColour(colour[i%3])
#            i += 1
##            time.sleep(0.25)

#    def restart(self, button):
#    
#        self.button = button
#        self.__init__(self.button)
#        self.run()
        
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
        self.keys = [chr(ord('a') + i) for i in range(26)]
        self.keys.append('space')
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
            if key == "space":
                self.hash_label[i] = 'space'
            elif key == "enter":
                self.hash_label[i] = "\n"
            i += 1
         
        i = 0
        j = 0
        self.keybox = []
        font = wx.Font(20, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.BOLD)
        
        for button in self.key_buttons:
            if i % 7 == 0:
                if self.keybox != []:
                    self.keyboard.AddSpacer(40)
                    self.keyboard.Add(self.keybox[j])
                    j += 1
                self.keybox.append(wx.BoxSizer(wx.HORIZONTAL))
            button.Bind(wx.EVT_ENTER_WINDOW, self.change_colour)
            button.Bind(wx.EVT_LEAVE_WINDOW, self.revert_colour)
#            button.Bind(wx.EVT_BUTTON, self.connect_keys)
            button.SetFont(font)
            self.keybox[j].Add(button)
            self.keybox[j].AddSpacer(40)
            i += 1       
        
        self.keyboard.AddSpacer(40)
        self.keyboard.Add(self.keybox[j])
        self.outer_box.Add(self.keyboard, border=5, flag=wx.ALL)    
        self.panel.SetSizer(self.outer_box)  
        
    def change_colour(self, event):
        
        global MOUSE_HOVER
        i = event.GetId()
        self.colour_changed = i
        button = self.hash[i]
        button.Bind(wx.EVT_BUTTON, self.connect_keys)
        button.SetBackgroundColour('red')
#        wx.CallLater(20, self.change_colour, event)
#        self.main_pipe_time.send(True)
#        colour = self.main_pipe_colour.recv()
#        print colour
#        button.SetBackgroundColour(colour)
                
    def revert_colour(self, event):
        
        global MOUSE_HOVER
        MOUSE_HOVER = False
#        self.main_pipe_time.send(False)
        button = self.hash[self.colour_changed]
        button.SetBackgroundColour('grey')
        
    def connect_keys(self, event):
        
        i = event.GetId()
        label = self.hash_label[i]
#        if label == "space":
#            label = " "
#        else:
#            label = "\n"
        self.keyboard_control.type_string(label)
        initial_text = self.text.GetValue()
        self.text.SetValue(initial_text + label)
        
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
    test()

