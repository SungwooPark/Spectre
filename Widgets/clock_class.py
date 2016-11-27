from Tkinter import *
from datetime import datetime, timedelta
import requests
from APPID_keys import googleAPPID

class clock(Frame):
	def __init__(self, master, text_color):
		Frame.__init__(self, master, bg = 'black')
		self.clockText = Label(self, font=('Helvetica',100), fg= text_color, bg="black",text='TIME')
		self.clockText.pack(side = TOP, anchor = W)
		self.dayText = Label(self, font=('Helvetica',100), fg= text_color, bg="black",text='DAY')
		self.dayText.pack(side = TOP, anchor = W)
		self.request = requests
	def getCoordinates(self, address):
		coordsURL = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + googleAPPID
		coordsData = self.request.get(coordsURL)
		coordsJSON = coordsData.json()
		if coordsJSON['status'] == 'OK': #make sure user used correct format (city, country)
			latCoord = coordsJSON['results'][0]['geometry']['location']['lat']
			lonCoord = coordsJSON['results'][0]['geometry']['location']['lng']
			return ((latCoord,lonCoord))
		else:
			return ((42.2809, 71.2378)) #Needham's coordinates
	def getTimezoneDiff(self, address):
		lat, lon = self.getCoordinates(address) #tuple --> lat, lon
		coords = str(lat) + ',' + str(lon)
		timeSinceEpoch = str((datetime.utcnow() - datetime(1970,1,1)).total_seconds()) #time since the epoch (1/1/1970) in seconds
		timezoneURL = 'https://maps.googleapis.com/maps/api/timezone/json?location=' + coords + '&timestamp=' + timeSinceEpoch + '&key=' + googleAPPID
		timezoneData = self.request.get(timezoneURL)
		timezoneJSON = timezoneData.json()
		rawOffset = timezoneJSON['rawOffset'] #raw timezone offset
		dstOffset = timezoneJSON['dstOffset'] #daylight savings time
		return rawOffset + dstOffset
	def updateTime(self, timezoneDiff):
		currentUTC = datetime.utcnow()
		rawLocalTime = currentUTC + timedelta(seconds = timezoneDiff)
		localTime = rawLocalTime.strftime('%I: %M %p') #hour, mins, am/pm
		day = rawLocalTime.strftime('%a') #abbreviated day
		self.clockText.config(text = localTime)
		self.dayText.config(text = day)

