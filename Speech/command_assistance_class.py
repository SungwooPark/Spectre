"""Command assistance module"""

from Tkinter import *

class speechText(Frame): #NOT FULLY IMPLEMENTED YET
	"""Command assistance widget class that helps user format commands correctly."""
	def __init__(self, master, text_color):
		"""Creates command assistance widget with placeholder text value of "na".
		Params: master - Tkinter frame in which the widget is placed
				text_color - string color name for font
		"""		
		Frame.__init__(self, master, bg = 'black')
		self.speechText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='na')
		self.speechText.pack(side = TOP, anchor = 'c')
		self.widget_formats = {'timezone':'Change timezone to Madrid, Spain', 'weather': 'Get weather for Boston', 'news': 'Get news from The Huffington Post', 'trip': 'Get length of trip from A to B by driving, walking, bicycling, or transit', 'box': 'Put bob in NewsBox', 'direction': 'Close mirror. Open mirror'}
	def misheard(self, command_type):
		"""Updates command-related Tkinter Label widget with information about the command Spectre thinks it heard and that command's format.
		Params: command_type - string command type
		"""
		message = "I don't understand. It sounds like you want the " + command_type + " widget.\nTry using this format: " + self.widget_formats[command_type]
		self.speechText.config(text = message)
	def echoAction(self, command_type, command_val):
		"""Updates command-related Tkinter Label widget with information about the command Spectre just executed.
		Params: command_t	ype - string command type
				command_val - string command value
		"""
		if type(command_val) == str:
			message = "You requested " + command_type + ". Your input was " + command_val + ".\nIf this didn't work, try using the format: \n" + self.widget_formats[command_type]
		elif type(command_val) == list:
			inputs = "";
			for val in command_val:
				inputs += val + ", "
			message = "You requested " + command_type + ". Your inputs were " + inputs[0:-2] + ".\nIf this didn't work, try using the format: \n" + self.widget_formats[command_type]
		self.speechText.config(text = message)

