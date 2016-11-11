from Tkinter import *
import serial
import time
import requests
from PIL import ImageTk, Image
from cStringIO import StringIO
from io import BytesIO
from APPID_keys import newsAPPID, weatherAPPID
from rec_commands import get_microphone_output #speech rec program
import speech_recognition as sr
from threading import Thread
from Queue import Queue
from chat_bot import ChatBotInterface

# Set up serial interface, at 9600 bps
##ser = serial.Serial('/dev/ttyUSB0',9600)

class direction(Frame):
	def __init__(self, master):
		Frame.__init__(self, master, bg = 'black')
		self.dirText = Label(self, font=('Helvetica',100), fg= text_color, bg="black",text='Closed')
		self.dirText.pack(side = TOP, anchor = E)
		self.direction = 0 #0 is closed, 1 is open
	def sendToArduino(self):
		pass
		# write to Arduino

class clock(Frame):
	def __init__(self, master):
		Frame.__init__(self, master, bg = 'black')
		self.clockText = Label(self, font=('Helvetica',100), fg= text_color, bg="black",text='TIME')
		self.clockText.pack(side = TOP, anchor = E)
	def getTime(self):
		currentTime = time.strftime('%I: %M %p')
		return currentTime

class weather(Frame):
	def __init__(self, master):
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

class news(Frame):
	def __init__(self, master):
		Frame.__init__(self, master, bg = 'black')
		#CREATE TITLE LABEL
		self.trendingNews = Label(self, font=('Helvetica',40), fg= text_color, bg="black",text='Trending News')
		self.trendingNews.pack(side = TOP, anchor = E)
		self.headlines = Label(self, font=('Helvetica',15), fg= text_color, bg="black",text='Headlines')
		self.headlines.pack(side = LEFT, anchor = SE)
		self.request = requests
	def getNews(self):
		source = 'cnn'
		sortBy = 'top'
		newsURL = 'https://newsapi.org/v1/articles?source=' + source + '&sortBy=' + sortBy + '&apiKey=' + newsAPPID
		newsData = self.request.get(newsURL)
		newsJSON = newsData.json()
		newsHeadlines = newsJSON['articles']
		headlinesString = ''
		for article in newsHeadlines[1:4]: #first item is repeated, grab first three unique headlines
			headlinesString += (article['title'] + '\n')
		return headlinesString
	def updateNews(self):
		gatheredData = self.getNews()
		self.headlines.config(text = gatheredData)

class speechText(Frame): #NOT IMPLEMENTED YET
	def __init__(self, master):
		Frame.__init__(self, master, bg = 'black')
		self.speechText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='Boston')
		self.speechText.pack(side = TOP, anchor = E)

class speechListener(Thread): #constantly checking on its own, outside of main thread
	def __init__(self, queue):
		Thread.__init__(self)
		self.speech_rec = sr.Recognizer() #initialize speech recognition object
		self.speechQueue = queue
		self.chatbot = ChatBotInterface()
		self.daemon = True #speechListener quits when fullWindow quits
		self.start()
	def run(self): #threading automatically calls the run method
		count = 0
		while True:
			print count
			count += 1
			command = get_microphone_output(self.speech_rec)
			print command
			if "question" in command:
				self.chatbot.say_output("How can I help you?")
				question = get_microphone_output(self.speech_rec)
				if "mind" in command: #I mean "never mind"
					pass
				else:
					self.chatbot.chatbot_response(question)
			elif "weather" in command: #"get weather for Boston"
				split_command = command.split(" ")
				city_name = split_command[len(split_command)-1] #assumes city name is last word
				self.speechQueue.put(("weather", city_name)) #assumes city is one word
			elif "open" in command:
				self.speechQueue.put(("direction","open"))
			elif "shut" in command:
				self.speechQueue.put(("direction","closed"))

class fullWindow():
	def __init__(self):
		self.rootWin = Tk()
		self.rootWin.configure(background='black')
		self.rootWin.attributes("-fullscreen", True)
		self.time = time.time() - 5*60; #this makes the loop below update weather right away
		self.rootWin.bind('<Return>',self.escape) #exits program

		#SETUP FRAMES
		self.leftFrame = Frame(self.rootWin, background = 'black') #create first frame
		self.leftFrame.pack(expand=False, fill = 'both', side = LEFT) #put frame against LEFT side, fill frame in x and y directions
		self.rightFrame = Frame(self.rootWin, background = 'black') #create a second frame
		self.rightFrame.pack(expand=False, fill = 'both', side = RIGHT) #put frame against RIGHT side, fill frame in x and y directions		
		
		#DIRECTION
		self.direction = direction(self.leftFrame) #create direction object in leftFrame
		self.direction.pack(side = BOTTOM, anchor = SW) #put direction object in frame (against LEFT side)
		#CLOCK
		self.clock = clock(self.leftFrame) #create clock object in rightFrame
		self.clock.pack(side = TOP , anchor = NW) #put clock object in frame (against RIGHT side)
		#WEATHER
		self.city_name = "Needham"
		self.weather = weather(self.rightFrame) #create clock object in rightFrame
		self.weather.pack(side = TOP ) #put clock object in frame (against RIGHT side)
		#NEWS
		self.news = news(self.rightFrame)
		self.news.pack(side = BOTTOM)
		#SPEECH
		self.speechText = speechText(self.leftFrame)
		self.speechText.pack(side = BOTTOM)
		#SPEECH
		self.queue = Queue()
		self.speech = speechListener(self.queue)

	def update(self): #update widgets
		#DIRECTION UPDATE
##        self.direction.dirText.config(text = read_serial)
		#TIME UPDATE
		currentTime = self.clock.getTime()
		self.clock.clockText.config(text = currentTime)
		if not self.queue.empty():
			command_type, command_val = self.queue.get()
			print command_type, command_val
			if command_type == "direction":
				self.direction.dirText.config(text = command_val)
				if command_val == "open":
					self.direction.direction = 1
				elif command_val == "closed":
					self.direction.direction = 0
			if command_type == "weather":
				self.city_name = command_val
				self.time = time.time() - 5*61 #make change now by changing time
			self.speechText.speechText.config(text = command_val)
		#WEATHER UPDATE
		if time.time() - self.time > 5*60: #if it's been 5 minutes, check weather again
			self.weather.updateWeather(self.city_name)
			self.news.updateNews()
			self.time = time.time()

	def escape(self, event): #exit tkinter program
		self.rootWin.destroy()

if __name__ == '__main__':
	text_color = "white"
	sung = fullWindow()
	while True:
##        read_serial = str(ser.readline())
		sung.rootWin.update_idletasks()
		sung.rootWin.update()
		sung.update()
		#SEND DIRECTION TO SERIAL


