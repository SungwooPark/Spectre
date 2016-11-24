from Tkinter import *
import serial
import time
from Queue import Queue
from news_class import news
from weather_class import weather
from clock_class import clock
from direction_class import direction
from speech_listener_class import speechListener
from interaction_text_class import speechText
from distance_class import distanceFrom

# Set up serial interface, at 9600 bps
##ser = serial.Serial('/dev/ttyUSB0',9600)

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
		self.direction = direction(self.leftFrame, text_color) #create direction object in leftFrame
		self.direction.pack(side = BOTTOM, anchor = SW) #put direction object in frame (against LEFT side)
		#CLOCK
		self.city_name = "Needham"
		self.country_name = "US"
		self.clock = clock(self.leftFrame, text_color) #create clock object in rightFrame
		self.clock.pack(side = TOP , anchor = NW) #put clock object in frame (against RIGHT side)
		self.timezoneDiff = self.clock.getTimezoneDiff(self.city_name, self.country_name)
		#WEATHER
		self.weather = weather(self.rightFrame, text_color) #create clock object in rightFrame
		self.weather.pack(side = TOP ) #put clock object in frame (against RIGHT side)
		#NEWS
		self.news = news(self.rightFrame, text_color)
		self.news.pack(side = BOTTOM)
		# self.newsSources = self.news.getSources() #returns dictionary, dict[name] = id
		self.newsOutlet = "cnn" #default news source
		#INTERACTION TEXT
		self.speechText = speechText(self.leftFrame, text_color)
		self.speechText.pack(side = BOTTOM)
		#SPEECH
		self.queue = Queue()
		self.speech = speechListener(self.queue, [])#self.newsSources)
		#TRIP DISTANCE/DURATION
		self.trip = distanceFrom(self.rightFrame, text_color)
		self.trip.pack(side = BOTTOM)
		self.trip.setWidget('Needham', 'MA', 'Seattle', 'WA')

	def update(self): #update widgets
		self.news.pack_forget()
		#DIRECTION UPDATE
##        self.direction.dirText.config(text = read_serial)
		#TIME UPDATE
		currentTime = self.clock.updateTime(self.timezoneDiff)
		if not self.queue.empty():
			command_type, command_val = self.queue.get()
			print command_type, command_val
			#SET MIRROR MOVEMENT DIRECTION
			if command_type == "direction":
				self.direction.dirText.config(text = command_val)
				if command_val == "open":
					self.direction.direction = 1
				elif command_val == "closed":
					self.direction.direction = 0
			#SET WEATHER LOCATION
			if command_type == "weather":
				self.city_name = command_val
				self.time = time.time() - 5*61 #make change now by changing time
			#SET NEWS SOURCE
			if command_type == "news":
				self.newsOutlet = command_val
				self.news.trendingNews.config(text = command_val)
				self.time = time.time() - 5*61 #make change now by changing time
			#SET TIMEZONE
			if command_type == "timezone":
				self.city_name, self.country_name = command_val
				self.timezoneDiff = self.clock.getTimezoneDiff(self.city_name, self.country_name)
				self.time = time.time() - 5*61 #make change now by changing time
			self.speechText.speechText.config(text = command_val)
		#WEATHER/NEWS UPDATE
		if time.time() - self.time > 5*60: #if it's been 5 minutes, check weather again
			self.weather.updateWeather(self.city_name)
			self.news.updateNews(self.newsOutlet)
			self.time = time.time()

	def escape(self, event): #exit tkinter program
		self.rootWin.destroy()

	def replaceWidget(self, old_widget, new_widget):
		old_widget.pack_forget()
		new_widget.pack()

if __name__ == '__main__':
	text_color = "white"
	sung = fullWindow()
	while True:
		sung.rootWin.update_idletasks()
		sung.rootWin.update()
		sung.update()
##        read_serial = str(ser.readline())
		#SEND DIRECTION TO SERIAL
