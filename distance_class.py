from Tkinter import *
import requests
from APPID_keys import googleAPPID

class distanceFrom(Frame):
	def __init__(self, master, text_color):
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
	def getDistanceFrom(self, origin_address, final_address, travel_mode):
		# distURL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + origin_city + ',' + origin_state + "&destinations=" + final_city + ',' + final_state + '&key=' + googleAPPID
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
			return ((0,0))
	def setWidget(self, origin_address, final_address, travel_mode = 'driving'):
		distance, duration = self.getDistanceFrom(origin_address, final_address, travel_mode)
		overviewMessage = origin_address.split(",")[0] + "\nto " + final_address.split(",")[0]
		durationMessage = "Duration: " + duration
		distanceMessage = "Distance: " + distance
		modeMessage = "Travel mode: " + travel_mode
		self.tripText.config(text = overviewMessage)
		self.durationText.config(text = durationMessage)
		self.distanceText.config(text = distanceMessage)
		self.modeText.config(text = modeMessage)
