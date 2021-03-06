"""Main program"""

from Tkinter import *
import serial
import time
import sys
from Queue import Queue
from Widgets.news_class import news
from Widgets.weather_class import weather
from Widgets.clock_class import clock
from Widgets.direction_class import direction
from Widgets.trip_class import trip
#from Widgets.newsbox_class import newsBox
from Speech.speech_listener_class import speechListener
from Speech.command_assistance_class import speechText
from mic_parser import mic_input_parser

# Set up serial interface, at 9600 bps
##ser = serial.Serial('/dev/ttyUSB0',9600)

class fullWindow():
    """Window class that displays widgets and starts/interacts with speech recognition thread."""
    def __init__(self):
        """Creates Tkinter window and initializes its widgets."""
        self.rootWin = Tk()
        self.rootWin.configure(background='black')
        self.rootWin.attributes("-fullscreen", True)
        self.time = time.time() - 5*60; #this makes the loop below update weather right away
        self.rootWin.bind('<Return>',self.escape) #enter key exits program
        self.rootWin.bind('<Down>',self.restartSpeech) #down key restarts program
        #SETUP FRAMES
        self.leftFrame = Frame(self.rootWin, background = 'black') #create first frame
        self.leftFrame.pack(expand=False, fill = 'both', side = LEFT) #put frame against LEFT side, fill frame in x and y directions
        self.rightFrame = Frame(self.rootWin, background = 'black') #create a second frame
        self.rightFrame.pack(expand=False, fill = 'both', side = LEFT) #put frame against RIGHT side, fill frame in x and y directions     
        
        #WIDGETS
        #DIRECTION
        self.direction = direction(self.leftFrame, text_color) #create direction object in leftFrame
        #CLOCK
        self.address = "Needham, US"
        self.clock = clock(self.leftFrame, text_color) #create clock object in rightFrame
        self.clock.pack(side = TOP , anchor = NW) #put clock object in frame (against RIGHT side)
        self.timezoneDiff = self.clock.getTimezoneDiff(self.address)
        #WEATHER
        self.weather = weather(self.leftFrame, text_color) #create clock object in rightFrame
        #NEWS
        self.news = news(self.leftFrame, text_color)
        self.newsSources = self.news.getSources() #returns dictionary, dict[name] = id
        # self.newsSources = None
        self.newsOutlet = "cnn" #default news source
        #INTERACTION TEXT
        self.speechText = speechText(self.leftFrame, text_color)
        self.speechText.pack(anchor = W, pady = 100)
        #SPEECH
        self.queue = Queue()
        self.speech = mic_input_parser(self.queue, self.newsSources)
        #TRIP DISTANCE/DURATION
        self.trip = trip(self.leftFrame, text_color)
        #NEWSBOX
        #self.newsbox = newsBox(self.rightFrame, text_color)

        #SET NON-PINNED WIDGET LIST
        self.temp_widget_list = [self.direction, self.weather, self.news, self.trip]#, self.newsbox]
        self.pinned_widgets = []

    def update(self):
    	"""Updates widgets periodically or given user input."""
        #VOICE RECOGNITION QUEUE
        if not self.queue.empty():
            self.speechText.speechText.config(text = "")
            command_type, command_val = self.queue.get()
            print command_type, command_val
            #SET MIRROR MOVEMENT DIRECTION
            if command_type == "direction":
                if command_val == "open":
                    self.direction.direction = 1
                    text = "open"
                elif command_val == "closed":
                    self.direction.direction = 0
                    text = "closed"
                self.direction.updateDirection(text)
                self.showWidget(self.direction)
                self.speechText.echoAction(command_type, command_val)
            #SET WEATHER LOCATION
            if command_type == "weather":
                self.address = command_val
                self.weather.updateWeather(self.address)
                self.showWidget(self.weather)
                self.speechText.echoAction(command_type, command_val)
            #SET NEWS SOURCE
            if command_type == "news":
                self.newsOutlet = command_val
                self.news.trendingNews.config(text = command_val)
                self.news.updateNews(self.newsOutlet)
                self.showWidget(self.news)
                self.speechText.echoAction(command_type, command_val)
            #SET TIMEZONE
            if command_type == "timezone":
                self.address = command_val
                self.timezoneDiff = self.clock.getTimezoneDiff(self.address)
                self.time = time.time() - 5*61 #make change now by changing time
                self.speechText.echoAction(command_type, command_val)
            #SHOW TRIP
            if command_type == "trip":
                origin_address, final_address, travel_mode = command_val
                self.trip.setWidget(origin_address, final_address, travel_mode)
                self.showWidget(self.trip)
                self.speechText.echoAction(command_type, command_val)
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
            #COMMAND ASSISTANCE
            if command_type == "misheard":
                self.speechText.misheard(command_val)
        #WEATHER/NEWS UPDATE
        if time.time() - self.time > 5*60: #if it's been 5 minutes, check weather again
            self.weather.updateWeather(self.address)
            #self.news.updateNews(self.newsOutlet)
            self.time = time.time()
        #DIRECTION UPDATE
##        self.direction.dirText.config(text = read_serial)
        #TIME UPDATE
        currentTime = self.clock.updateTime(self.timezoneDiff)

    def showWidget(self, new_widget):
    	"""Makes specified widget visible in "focus" spot.
    	Params: new_widget - widget object user wants to see
    	"""
        for widget in self.temp_widget_list: #bc we don't have many widgets and this makes it so we don't have
            widget.pack_forget() #to remember the current visible widget which we now need to make invisible
        for widget in self.pinned_widgets:
            widget.pack(side = BOTTOM, anchor = SW)
        new_widget.pack(side = TOP, anchor = SW) #this will also move a pinned widget up to the top right (focus)

    def hideWidget(self, selected_widget):
    	"""Makes specified widget invisible in "focus" spot.
    	Params: selected_widget - widget object user no longer wants to see
    	"""
        if selected_widget not in self.pinned_widgets:
            selected_widget.pack_forget()
        else: #if it's in self.pinned_widgets
            selected_widget.pack(side = BOTTOM, anchor = SW) #put pinned widget back at bottom

    def pinWidget(self, pinned_widget): #just removes it from temporary widget list
    	"""Adds specified widget to list of pinned widgets and shows it at the bottom right corner of screen until widget is actively removed.
    	Params: pinned_widget - widget object user wants to keep on the screen
    	"""
    	if pinned_widget not in self.pinned_widgets:
            self.temp_widget_list.remove(pinned_widget)
            self.pinned_widgets.append(pinned_widget)
        pinned_widget.pack(side = BOTTOM, anchor = NW) #put pinned widget at bottom right of screen

    def unPinWidget(self, unpinned_widget): #just adds it back to temporary widget list
    	"""Removes specified widget from list of pinned widgets and stops showing it at the bottom right corner of screen.
    	Params: unpinned_widget - widget object user wants to remove from the screen
    	"""
        if unpinned_widget not in self.temp_widget_list:
            self.temp_widget_list.append(unpinned_widget)
        unpinned_widget.pack_forget()
        self.pinned_widgets.remove(unpinned_widget)

    def escape(self, event): #exit tkinter program
    	"""Destroys program given a keypress."""
        self.rootWin.destroy()

    def restartSpeech(self, event): #exit tkinter program
    	"""Restarts speech thread (in case it freezes or something) given a keypress."""
        self.speech = mic_input_parser(self.queue, self.newsSources)
        print "restarted speech thread"

if __name__ == '__main__':
    text_color = "white"
    sung = fullWindow()
    # arduino = serial.Serial('/dev/ttyUSB0',9600) #create arduino object
    if 'arduino' in locals():
        while True:
            sung.rootWin.update_idletasks()
            sung.rootWin.update()
            sung.update()
            #read_serial = str(arduino.readline())
            if sung.direction.direction == 1:
                for i in range(50):
                    arduino.write(str(sung.direction.direction)) #send direction to arduino (0 is closed; 1 is open)
                sung.direction.direction = 2
            elif sung.direction.direction == 0:
                for i in range(50):
                    arduino.write(str(sung.direction.direction))
                sung.direction.direction = 2
            else:
                arduino.write(str(sung.direction.direction))
    else:
        while True:
	        sung.rootWin.update_idletasks()
	        sung.rootWin.update()
	        sung.update()
