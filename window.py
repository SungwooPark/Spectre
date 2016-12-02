from Tkinter import *
import serial
import time
import sys
from Queue import Queue
from Widgets.news_class import news
from Widgets.weather_class import weather
from Widgets.clock_class import clock
from Widgets.direction_class import direction
from Widgets.distance_class import distanceFrom
#from Widgets.newsbox_class import newsBox
from Speech.speech_listener_class import speechListener
from Speech.interaction_text_class import speechText

# Set up serial interface, at 9600 bps
##ser = serial.Serial('/dev/ttyUSB0',9600)

class fullWindow():
	def __init__(self):
		self.rootWin = Tk()
		self.rootWin.configure(background='black')
		self.rootWin.attributes("-fullscreen", True)
		self.time = time.time() - 5*60; #this makes the loop below update weather right away
		self.rootWin.bind('<Return>',self.escape) #enter key exits program

		#SETUP FRAMES
		self.leftFrame = Frame(self.rootWin, background = 'black') #create first frame
		self.leftFrame.pack(expand=False, fill = 'both', side = LEFT) #put frame against LEFT side, fill frame in x and y directions
		self.rightFrame = Frame(self.rootWin, background = 'black') #create a second frame
		self.rightFrame.pack(expand=False, fill = 'both', side = RIGHT) #put frame against RIGHT side, fill frame in x and y directions		
		
		#WIDGETS
		#DIRECTION
		self.direction = direction(self.rightFrame, text_color) #create direction object in leftFrame
		#CLOCK
		self.address = "Needham, US"
		self.clock = clock(self.leftFrame, text_color) #create clock object in rightFrame
		self.clock.pack(side = TOP , anchor = NW) #put clock object in frame (against RIGHT side)
		self.timezoneDiff = self.clock.getTimezoneDiff(self.address)
		#WEATHER
		self.weather = weather(self.rightFrame, text_color) #create clock object in rightFrame
		#NEWS
		self.news = news(self.rightFrame, text_color)
		self.newsSources = self.news.getSources() #returns dictionary, dict[name] = id
		self.newsOutlet = "cnn" #default news source
		#INTERACTION TEXT
		self.speechText = speechText(self.leftFrame, text_color)
		self.speechText.pack(anchor = W, pady = 100)
		#SPEECH
		self.queue = Queue()
		self.speech = speechListener(self.queue, self.newsSources)
		#TRIP DISTANCE/DURATION
		self.trip = distanceFrom(self.rightFrame, text_color)
		#NEWSBOX
		self.newsbox = None;#newsBox(self.rightFrame, text_color)

		#SET NON-PINNED WIDGET LIST
		self.temp_widget_list = [self.direction, self.weather, self.news, self.trip, self.newsbox]
		self.pinned_widgets = []

	def update(self): #update widgets
		#VOICE RECOGNITION QUEUE
		if not self.queue.empty():
			command_type, command_val = self.queue.get()
			print command_type, command_val
			#SET MIRROR MOVEMENT DIRECTION
			if command_type == "direction":
				text = "Unfamiliar command"
				if command_val == "open":
					self.direction.direction = 1
					text = "open"
				elif command_val == "closed":
					self.direction.direction = 0
					text = "closed"
				self.direction.dirText.config(text = text)
				self.showWidget(self.direction)
			#SET WEATHER LOCATION
			if command_type == "weather":
				self.address = command_val
				self.weather.updateWeather(self.address)
				self.showWidget(self.weather)
			#SET NEWS SOURCE
			if command_type == "news":
				self.newsOutlet = command_val
				self.news.trendingNews.config(text = command_val)
				self.news.updateNews(self.newsOutlet)
				self.showWidget(self.news)
			#SET TIMEZONE
			if command_type == "timezone":
				self.address = command_val
				self.timezoneDiff = self.clock.getTimezoneDiff(self.address)
				self.time = time.time() - 5*61 #make change now by changing time
			#SHOW TRIP
			if command_type == "trip":
				origin_address, final_address = command_val
				self.trip.setWidget(origin_address, final_address)
				self.showWidget(self.trip)
			#SHOW NEWSBOX
			if command_type == "newsbox":
				search_term = command_val
				self.newsbox.produce_map(search_term)
				self.showWidget(self.newsbox)			
			#PIN WIDGET
			if command_type == "add":
				if command_val == "weather":
					self.pinWidget(self.weather)
				elif command_val == "news":
					self.pinWidget(self.news)
				elif command_val == "trip":
					self.pinWidget(self.trip)
				elif command_val == "direction":
					self.pinWidget(self.direction)
			#UNPIN WIDGET
			if command_type == "remove":
				if command_val == "weather":
					self.unPinWidget(self.weather)
				elif command_val == "news":
					self.unPinWidget(self.news)
				elif command_val == "trip":
					self.unPinWidget(self.trip)
				elif command_val == "direction":
					self.unPinWidget(self.direction)
			#SHOW WIDGET
			if command_type == "show":
				if command_val == "weather":
					self.showWidget(self.weather)
				elif command_val == "news":
					self.showWidget(self.news)
				elif command_val == "trip":
					self.showWidget(self.trip)
				elif command_val == "direction":
					self.showWidget(self.direction)
			#HIDE WIDGET
			if command_type == "hide":
				if command_val == "weather":
					self.hideWidget(self.weather)
				elif command_val == "news":
					self.hideWidget(self.news)
				elif command_val == "trip":
					self.hideWidget(self.trip)
				elif command_val == "direction":
					self.hideWidget(self.direction)
			self.speechText.speechText.config(text = command_val)
		#WEATHER/NEWS UPDATE
		if time.time() - self.time > 5*60: #if it's been 5 minutes, check weather again
			self.weather.updateWeather(self.address)
			self.news.updateNews(self.newsOutlet)
			self.time = time.time()
		#DIRECTION UPDATE
##        self.direction.dirText.config(text = read_serial)
		#TIME UPDATE
		currentTime = self.clock.updateTime(self.timezoneDiff)

	def showWidget(self, new_widget):
		for widget in self.temp_widget_list: #bc we don't have many widgets and this makes it so we don't have
			widget.pack_forget() #to remember the current visible widget which we now need to make invisible
		for widget in self.pinned_widgets:
			widget.pack(side = BOTTOM, anchor = NE)
		new_widget.pack(side = TOP, anchor = NE) #this will also move a pinned widget up to the top right (focus)

	def hideWidget(self, selected_widget):
		if selected_widget not in self.pinned_widgets:
			selected_widget.pack_forget()
		else: #if it's in self.pinned_widgets
			selected_widget.pack(side = BOTTOM, anchor = NE) #put pinned widget back at bottom

	def pinWidget(self, pinned_widget): #just removes it from temporary widget list
		if pinned_widget not in self.pinned_widgets:
			self.temp_widget_list.remove(pinned_widget)
			self.pinned_widgets.append(pinned_widget)
		pinned_widget.pack(side = BOTTOM, anchor = NE) #put pinned widget at bottom right of screen

	def unPinWidget(self, unpinned_widget): #just adds it back to temporary widget list
		if unpinned_widget not in self.temp_widget_list:
			self.temp_widget_list.append(unpinned_widget)
		unpinned_widget.pack_forget()
		self.pinned_widgets.remove(unpinned_widget)

	def escape(self, event): #exit tkinter program
 		self.rootWin.destroy()

if __name__ == '__main__':
	text_color = "white"
	sung = fullWindow()
	while True:
		sung.rootWin.update_idletasks()
		sung.rootWin.update()
		sung.update()
##        read_serial = str(ser.readline())
		#SEND DIRECTION TO SERIAL
