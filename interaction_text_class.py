from Tkinter import *

class speechText(Frame): #NOT IMPLEMENTED YET
	def __init__(self, master, text_color):
		Frame.__init__(self, master, bg = 'black')
		self.speechText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='NA')
		self.speechText.pack(side = TOP, anchor = E)
