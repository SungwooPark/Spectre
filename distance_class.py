from Tkinter import *
import requests
from APPID_keys import googleAPPID

class distanceFrom(Frame):
	def __init__(self, master, text_color):
		Frame.__init__(self, master, bg = 'black')
		self.tripText = Label(self, font=('Helvetica',40), fg= text_color, bg="black",text='Trip Information')
		self.tripText.pack(side = TOP, anchor = E)
		self.durationText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='Logistics')
		self.durationText.pack(side = TOP, anchor = W)
		self.distanceText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='Logistics')
		self.distanceText.pack(side = TOP, anchor = W)
		self.request = requests
	def getDistanceFrom(self, origin_city, origin_state, final_city, final_state):
		distURL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + origin_city + ',' + origin_state + "&destinations=" + final_city + ',' + final_state + '&key=' + googleAPPID
		distData = self.request.get(distURL)
		distJSON = distData.json()
		if distJSON['status'] == 'OK': #make sure user used correct format (city, country)
			distance = distJSON['rows'][0]['elements'][0]['distance']['text']
			duration = distJSON['rows'][0]['elements'][0]['duration']['text']
			print distance, duration
			return ((distance, duration))
		else: #in case command's format was wrong, etc
			return ((0,0))
	def setWidget(self, origin_city, origin_state, final_city, final_state):
		distance, duration = self.getDistanceFrom(origin_city, origin_state, final_city, final_state)
		overviewMessage = origin_city + " to " + final_city
		durationMessage = "Duration: " + duration
		distanceMessage = "Distance: " + distance
		self.tripText.config(text = overviewMessage)
		self.durationText.config(text = durationMessage)
		self.distanceText.config(text = distanceMessage)

