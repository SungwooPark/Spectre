from Tkinter import *

class speechText(Frame): #NOT IMPLEMENTED YET
	def __init__(self, master, text_color):
		Frame.__init__(self, master, bg = 'black')
		self.speechText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='NA')
		self.speechText.pack(side = TOP, anchor = 'c')
		self.widget_formats = {'timezone':'Change timezone to Madrid, Spain', 'weather': 'Get weather for Boston', 'news': 'Get news from BBC', 'trip': 'Get length of trip from A to B', 'box': 'Put bob in NewsBox', 'direction': 'Shut mirror. Open mirror'}
	def misheard(self, command_type):
		message = "I don't understand. It sounds like you want the " + command_type + ".\nTry using this format: " + self.widget_formats[command_type]
		self.speechText.config(text = message)
	def echoAction(self, command_type, command_val):
		message = "You requested " + command_type + ". Your input was " + command_val + ".\nIf this didn't work, try using the format: \n" + self.widget_formats[command_type]
		self.speechText.config(text = message)

