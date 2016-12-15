"""Weather module"""

from Tkinter import *
import requests
from APPID_keys import weatherAPPID
from PIL import ImageTk, Image
from cStringIO import StringIO
from io import BytesIO

class weather(Frame):
	"""Weather widget class that can be set to a certain location."""
	def __init__(self, master, text_color):
		"""Creates weather widget with placeholder labels and picture.
		Params: master - Tkinter frame in which the widget is placed
				text_color - string color name for font
		"""
		Frame.__init__(self, master, bg = 'black')
		#CREATE TEMP LABEL
		self.weatherTemp = Label(self, font=('Helvetica',80), fg= text_color, bg="black",text='TEMP')
		self.weatherTemp.pack(side = TOP, anchor = NE)
		#CREATE DESCRIPTION LABEL
		self.weatherDescription = Label(self, font=('Helvetica',40), fg= text_color, bg="black",text='Description')
		self.weatherDescription.pack(side = TOP, anchor = NE)
		#CREATE IMAGE LABEL
		pic = Image.open('Widgets/img.png')
		self.weatherImage = ImageTk.PhotoImage(pic)
		self.weatherPane = Label(self, image = self.weatherImage)
		self.weatherPane.pack(side = BOTTOM, anchor = NE)
		#CREATE REQUESTS OBJECT
		self.request = requests
	def getWeather(self, city_name):
		"""Gets temperature, short description of sky, and weather icon ID.
		Params: city_name - string name of a city
		Returns: list of three items (int temperature in Fahrenheit, string description, and string iconID)
		"""
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
		"""Updates weather-related Tkinter Label widgets with the information returned by getWeather.
		Params: city_name - string name of a city
		"""
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