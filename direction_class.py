from Tkinter import *

class direction(Frame):
	def __init__(self, master, text_color):
		Frame.__init__(self, master, bg = 'black')
		self.dirText = Label(self, font=('Helvetica',100), fg= text_color, bg="black",text='Closed')
		self.dirText.pack(side = TOP, anchor = NW)
		self.direction = 0 #0 is closed, 1 is open
	def sendToArduino(self):
		pass # write to Arduino