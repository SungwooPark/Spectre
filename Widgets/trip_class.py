"""Trip module"""

from Tkinter import *
import requests
from APPID_keys import googleAPPID

class trip(Frame):
	"""Trip widget class that can get distance and duration for trip between two points using a given mode of transportation."""
	def __init__(self, master, text_color):
		"""Creates trip widget with placeholder origin, destination, distance, duration, and travel mode values.
		Params: master - Tkinter frame in which the widget is placed
				text_color - string color name for font
		"""
		Frame.__init__(self, master, bg = 'black')
		self.tripText = Label(self, font=('Helvetica',40), fg= text_color, bg="black",text='Trip Information')
		self.tripText.pack(side = TOP, anchor = E)
		self.durationText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='Duration')
		self.durationText.pack(side = TOP, anchor = W)
		self.distanceText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='Distance')
		self.distanceText.pack(side = TOP, anchor = W)
		self.modeText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='Travel Mode')
		self.modeText.pack(side = TOP, anchor = W)
		self.request = requests
		self.acceptableModes = ['driving', 'walking', 'bicycling', 'transit']
	def getDistanceFrom(self, origin_address, final_address, travel_mode):
		"""Gets distance and duration of trip from one address to another using a given mode of travel.
		Params: origin_address - string starting point address
				final_address - string end point address
				travel_mode - string mode of travel (driving, walking, bicycling, or public transit)
		Returns: tuple with string distance in miles and string duration in hours and minutes
		"""
		distURL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + origin_address + "&destinations=" + final_address + '&key=' + googleAPPID + '&mode=' + travel_mode
		distData = self.request.get(distURL)
		distJSON = distData.json()
		print distJSON
		if distJSON['status'] == 'OK': #make sure user used correct format (city, country)
			distance = distJSON['rows'][0]['elements'][0]['distance']['text']
			duration = distJSON['rows'][0]['elements'][0]['duration']['text']
			print distance, duration
			return ((distance, duration))
		else: #in case command's format was wrong, etc
			return (("0 mi","0 mins"))
	def setWidget(self, origin_address, final_address, travel_mode = 'driving'):
		"""Updates trip-related Tkinter Label widgets with trip origin and destination adresses, distance, duration, and mode of travel values
		Params: origin_address - string starting point address
				final_address - string end point address
				travel_mode - string mode of travel (driving (default), walking, bicycling, or public transit)
		"""
		if travel_mode not in self.acceptableModes:
			travel_mode = 'driving'
		distance, duration = self.getDistanceFrom(origin_address, final_address, travel_mode)
		overviewMessage = origin_address.split(",")[0] + "\nto " + final_address.split(",")[0]
		durationMessage = "Duration: " + duration
		distanceMessage = "Distance: " + distance
		modeMessage = "Travel mode: " + travel_mode
		self.tripText.config(text = overviewMessage)
		self.durationText.config(text = durationMessage)
		self.distanceText.config(text = distanceMessage)
		self.modeText.config(text = modeMessage)
