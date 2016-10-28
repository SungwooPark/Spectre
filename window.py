from Tkinter import *

#Somehow getting a direction input from Arduino, ME stuff thing
# Blah blah
direction = 'UP'


class direction(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg = 'white')
        self.dirText = Label(self, font=('Helvetica',400), fg="black", bg="white",text='UP')
        self.dirText.pack(side = TOP, anchor = E)


class fullWindow:
    def __init__(self):
        self.rootWin = Tk()
        self.rootWin.configure(background='black')
        self.rootWin.attributes("-fullscreen", True)
        self.leftFrame = Frame(self.rootWin, background = 'white') #create frame for direction label
        self.leftFrame.pack(expand=False, fill = 'both', side = LEFT) #put frame against LEFT side, fill frame in x and y directions
        self.direction = direction(self.leftFrame) #create direction object in leftFrame
        self.direction.pack(side = TOP) #put direction object in frame (against LEFT side)
        

if __name__ == '__main__':
    sung = fullWindow()
    while True:
        sung.rootWin.update_idletasks()
        sung.rootWin.update()
        sung.direction.dirText.config(text = 'DOWN')
