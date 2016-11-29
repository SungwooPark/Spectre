from Tkinter import *
import requests
from APPID_keys import weatherAPPID
from PIL import ImageTk, Image
from cStringIO import StringIO
from io import BytesIO

class weather(Frame):
	def __init__(self, master, text_color):
		Frame.__init__(self, master, bg = 'black')
		#CREATE TEMP LABEL
		self.weatherTemp = Label(self, font=('Helvetica',100), fg= text_color, bg="black",text='TEMP')
		self.weatherTemp.pack(side = TOP, anchor = NE)
		#CREATE DESCRIPTION LABEL
		self.weatherDescription = Label(self, font=('Helvetica',40), fg= text_color, bg="black",text='Description')
		self.weatherDescription.pack(side = TOP, anchor = NE)
		#CREATE IMAGE LABEL
		pic = Image.open('weather_placeholder.png')
		self.weatherImage = ImageTk.PhotoImage(pic)
		self.weatherPane = Label(self, image = self.weatherImage)
		self.weatherPane.pack(side = BOTTOM, anchor = NE)
		#CREATE REQUESTS OBJECT
		self.request = requests
	def getWeather(self, city_name):
		self.cityName = city_name
		weatherURL = 'http://api.openweathermap.org/data/2.5/weather?q=' + self.cityName + '&APPID=' + weatherAPPID 
		weatherData = self.request.get(weatherURL)
		weatherJSON = weatherData.json()
		weatherTemp = weatherJSON['main']['temp'] #example: 282.56 -- in Kelvin
		weatherFahr = int(round((weatherTemp - 273)*9/5 + 32)) #convert to degrees Fahrenheit
		weatherSky = weatherJSON['weather'][0]['description'] #example: 'Clear', 'Rain', 'Snow'
		weatherIconID = weatherJSON['weather'][0]['icon'] #returns id of icon (example: 'O1d'?)
		return weatherFahr, weatherSky, weatherIconID
	def updateWeather(self, city_name):
			processedData = self.getWeather(city_name)
			#UPDATE TEMPERATURE STRING
			currentTemp = str(processedData[0]) +  ' F'
			self.weatherTemp.config(text = currentTemp)
			#UPDATE ICON PICTURE
			iconURL = 'http://openweathermap.org/img/w/' + processedData[2] + '.png'
			iconData = self.request.get(iconURL)
			iconPicture = ImageTk.PhotoImage(Image.open(BytesIO(iconData.content)))
			self.weatherPane.config(image = iconPicture)
			self.weatherPane.image = iconPicture
			#UPDATE DESCRIPTION
			currentDesc = str(processedData[1])
			self.weatherDescription.config(text = currentDesc)