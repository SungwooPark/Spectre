"""Mirror status module"""

from Tkinter import *

class direction(Frame):
    """Mirror direction widget class that shows status of mirror (i.e. opening or closing)."""
    def __init__(self, master, text_color):
        """Creates mirror direction widget with placeholder status value ("Closed").
        Params: master - Tkinter frame in which the widget is placed
                text_color - string color name for font
        """
        Frame.__init__(self, master, bg = 'black')
        self.dirText = Label(self, font=('Helvetica',100), fg= text_color, bg="black",text='Closed')
        self.dirText.pack(side = TOP, anchor = NW)
        self.direction = 2 #0 is closed, 1 is open
    def updateDirection(self, text):
        """Updates direction-related Tkinter Label widget with new status.
        Params: text - string status
        """
        self.dirText.config(text = text)
