from Tkinter import *
import serial
import time
import requests
from PIL import ImageTk, Image
from cStringIO import StringIO
from io import BytesIO

#Somehow getting a direction input from Arduino, ME stuff thing
direction = 'UP'

# Set up serial interface, at 9600 bps
##ser = serial.Serial('/dev/ttyUSB0',9600)

class direction(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg = 'black')
        self.dirText = Label(self, font=('Helvetica',100), fg="blue", bg="black",text='UP')
        self.dirText.pack(side = TOP, anchor = E)

class clock(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg = 'black')
        self.clockText = Label(self, font=('Helvetica',100), fg="blue", bg="black",text='TIME')
        self.clockText.pack(side = TOP, anchor = E)
    def getTime(self):
        currentTime = time.strftime('%I: %M %p')
        return currentTime

class weather(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg = 'black')
        #CREATE TEMP LABEL
        self.weatherTemp = Label(self, font=('Helvetica',100), fg="blue", bg="black",text='TEMP')
        self.weatherTemp.pack(side = TOP, anchor = NE)
        #CREATE DESCRIPTION LABEL
        self.weatherDescription = Label(self, font=('Helvetica',40), fg="blue", bg="black",text='Description')
        self.weatherDescription.pack(side = TOP, anchor = NE)
        #CREATE IMAGE LABEL
        pic = Image.open('weather_placeholder.png')
        self.weatherImage = ImageTk.PhotoImage(pic)
        self.weatherPane = Label(self, image = self.weatherImage)
        self.weatherPane.pack(side = BOTTOM, anchor = NE)
        #CREATE REQUESTS OBJECT
        self.request = requests
    def getWeather(self):
        self.cityName = 'Needham'
        weatherAPPID = '11dee608927c6bc5f293a9ee96e5ad91'
        weatherURL = 'http://api.openweathermap.org/data/2.5/weather?q=' + self.cityName + '&APPID=' + weatherAPPID 
        weatherData = self.request.get(weatherURL)
        weatherJSON = weatherData.json()
        weatherTemp = weatherJSON['main']['temp'] #example: 282.56 -- in Kelvin
        weatherFahr = int(round((weatherTemp - 273)*9/5 + 32)) #convert to degrees Fahrenheit
        weatherSky = weatherJSON['weather'][0]['description'] #example: 'Clear', 'Rain', 'Snow'
        weatherIconID = weatherJSON['weather'][0]['icon'] #returns id of icon (example: 'Old'?)
        return weatherFahr, weatherSky, weatherIconID
    def updateWeather(self):
            processedData = self.getWeather()
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

class  news(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg = 'black')
        #CREATE TITLE LABEL
        self.trendingNews = Label(self, font=('Helvetica',40), fg="blue", bg="black",text='Trending News')
        self.trendingNews.pack(side = TOP, anchor = E)
##        self.headlines = Message(self, font=('Helvetica',15), fg="blue", bg="black",text='Headlines')
        self.headlines = Label(self, font=('Helvetica',15), fg="blue", bg="black",text='Headlines')
        self.headlines.pack(side = LEFT, anchor = SE)
        self.request = requests
    def getNews(self):
        newsAPPID = '2732feee8baf45db8d5022a47ca5c4fe'
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

class calendar(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg = 'black')

class fullWindow:
    def __init__(self):
        self.rootWin = Tk()
        self.rootWin.configure(background='black')
        self.rootWin.attributes("-fullscreen", True)
        self.time = time.time() - 5*60; #this makes the loop below update weather right away

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
        self.weather = weather(self.rightFrame) #create clock object in rightFrame
        self.weather.pack(side = TOP ) #put clock object in frame (against RIGHT side)

        #NEWS
        self.news = news(self.rightFrame)
        self.news.pack(side = BOTTOM)

        #CALENDAR
        self.calendar = calendar(self.leftFrame)
        self.calendar.pack(side = BOTTOM)

if __name__ == '__main__':
    sung = fullWindow()
    while True:
##        read_serial = str(ser.readline())
        sung.rootWin.update_idletasks()
        sung.rootWin.update()
        #DIRECTION UPDATE
##        sung.direction.dirText.config(text = read_serial)
        #CLOCK UPDATE
        currentTime = sung.clock.getTime()
        sung.clock.clockText.config(text = currentTime)
        #WEATHER UPDATE
        if time.time() - sung.time > 5*60: #if it's been 5 minutes, check weather again
            sung.weather.updateWeather()
            sung.news.updateNews()
            sung.time = time.time()
            
