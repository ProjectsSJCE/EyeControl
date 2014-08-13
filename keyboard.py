import wx
from pykeyboard import PyKeyboard
import time
import threading
import thread
import multiprocessing as mp
import time
import pymouse

GAZE_RADIUS = 5
            
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
    test()

