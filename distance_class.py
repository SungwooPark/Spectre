from Tkinter import *
import requests
from APPID_keys import googleAPPID

class distanceFrom():
	def __init__(self, text_color):
		self.request = requests
	def getDistanceFrom(self, origin_city, origin_state, final_city, final_state):
		distURL = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial&origins=' + origin_city + ',' + origin_state + "&destinations=" + final_city + ',' + final_state + '&key=' + googleAPPID
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

