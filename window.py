from Tkinter import *
import serial
import time
from rec_commands import get_microphone_output #speech rec program
import speech_recognition as sr
from threading import Thread
from Queue import Queue
from chat_bot import ChatBotInterface
from news_class import news
from weather_class import weather
from clock_class import clock

# Set up serial interface, at 9600 bps
##ser = serial.Serial('/dev/ttyUSB0',9600)

class direction(Frame):
	def __init__(self, master):
		Frame.__init__(self, master, bg = 'black')
		self.dirText = Label(self, font=('Helvetica',100), fg= text_color, bg="black",text='Closed')
		self.dirText.pack(side = TOP, anchor = E)
		self.direction = 0 #0 is closed, 1 is open
	def sendToArduino(self):
		pass # write to Arduino

class speechText(Frame): #NOT IMPLEMENTED YET
	def __init__(self, master):
		Frame.__init__(self, master, bg = 'black')
		self.speechText = Label(self, font=('Helvetica',25), fg= text_color, bg="black",text='Boston')
		self.speechText.pack(side = TOP, anchor = E)

class speechListener(Thread): #constantly checking on its own, outside of main thread
	def __init__(self, queue, newsSources):
		Thread.__init__(self)
		self.speech_rec = sr.Recognizer() #initialize speech recognition object
		self.speechQueue = queue
		self.newsSources = newsSources #dictionary[name] = id
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
			#ASK CHATBOT QUESTION
			if "question" in command:
				self.chatbot.say_output("How can I help you?")
				question = get_microphone_output(self.speech_rec)
				print question
				if "mind" in question: #I mean "never mind"
					pass
				else:
					self.chatbot.say_output(self.chatbot.chatbot_response(question))
			#CHANGE WEATHER LOCATION
			elif "weather" in command: #ie "get weather for Boston"
				split_command = command.split(" ")
				city_name = split_command[len(split_command)-1] #assumes city name is last word
				self.speechQueue.put(("weather", city_name)) #assumes city is one word
			#CHANGE NEWS SOURCE
			elif "news" in command: #ie "get news from BBC"
				for source in self.newsSources:
					if source in command:
						self.speechQueue.put(("news", self.newsSources[source]))
			elif "zone" in command: #ie "change timezone to Madrid, Spain"
				split_command = command.split(" ")
				city_name = split_command[len(split_command)-2]
				country_name = split_command[len(split_command)-1]
				self.speechQueue.put(("timezone", ((city_name, country_name))))
			#OPEN/CLOSE MIRROR
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
		self.newsSources = self.news.getSources() #returns dictionary, dict[name] = id
		self.newsOutlet = "cnn" #default news source
		#SPEECH
		self.speechText = speechText(self.leftFrame)
		self.speechText.pack(side = BOTTOM)
		#SPEECH
		self.queue = Queue()
		self.speech = speechListener(self.queue, self.newsSources)

	def update(self): #update widgets
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

if __name__ == '__main__':
	text_color = "white"
	sung = fullWindow()
	while True:
		sung.rootWin.update_idletasks()
		sung.rootWin.update()
		sung.update()
##        read_serial = str(ser.readline())
		#SEND DIRECTION TO SERIAL


