import wx
from pykeyboard import PyKeyboard

class MyFrame(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, 'Keypad', pos=(0, 0), size=wx.DisplaySize())
        self.panel = wx.Panel(self)
        self.keyboard_control = PyKeyboard()
        
        #place to store what is being entered
        self.text = wx.TextCtrl(self.panel, 10, "Data", size=wx.DLG_SZE(self, 500, 20))
        self.outer_box = wx.BoxSizer(wx.VERTICAL)
        self.outer_box.Add(self.text, border=5, flag=wx.ALL)
        
        #place to make the actual keyboard
        self.keyboard = wx.BoxSizer(wx.VERTICAL)
        self.keys = [chr(ord('a') + i) for i in range(26)]
        self.keys.append('space')
        self.keys.append('enter')
        
        i = 1
        self.hash = {}
        self.key_buttons = []
        for key in self.keys:
            b = wx.Button(self.panel, i, key, size=wx.DLG_SZE(self, 71, 70))
            self.key_buttons.append(b)
            self.Bind(wx.EVT_BUTTON, self.connect_keys, b)
            self.hash[i] = key
            i += 1
         
        i = 0
        j = 0
        self.keybox = []
        for button in self.key_buttons:
            if i % 7 == 0:
                if self.keybox != []:
                    self.keyboard.AddSpacer(10)
                    self.keyboard.Add(self.keybox[j])
                    j += 1
                self.keybox.append(wx.BoxSizer(wx.HORIZONTAL))
              
            self.keybox[j].Add(button)
            self.keybox[j].AddSpacer(10)
            i += 1       
        
        self.keyboard.AddSpacer(10)
        self.keyboard.Add(self.keybox[j])
        self.outer_box.Add(self.keyboard, border=5, flag=wx.ALL)    
        self.panel.SetSizer(self.outer_box)    
        
    def connect_keys(self, event):
        
        i = event.GetId()
        label = self.hash[i]
#        if label == "space":
#            label = " "
#        else:
#            label = "\n"
        self.keyboard_control.type_string(label)
        self.update_text(label)
        
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

