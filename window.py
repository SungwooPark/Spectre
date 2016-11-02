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
        Frame.__init__(self, master, bg = 'white')
        self.dirText = Label(self, font=('Helvetica',100), fg="black", bg="white",text='UP')
        self.dirText.pack(side = TOP, anchor = E)

class clock(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg = 'blue')
        self.clockText = Label(self, font=('Helvetica',100), fg="blue", bg="white",text='TIME')
        self.clockText.pack(side = TOP, anchor = E)
    def getTime(self):
        currentTime = time.strftime('%I: %M %p')
        return currentTime

class weather(Frame):
    def __init__(self, master):
        Frame.__init__(self, master, bg = 'blue')
        #CREATE TEMP LABEL
        self.weatherTemp = Label(self, font=('Helvetica',100), fg="black", bg="white",text='TEMP')
        self.weatherTemp.pack(side = TOP, anchor = E)
        #CREATE IMAGE LABEL
        pic = Image.open('weather_placeholder.png')
        self.weatherImage = ImageTk.PhotoImage(pic)
        self.weatherPane = Label(self, image = self.weatherImage)
        self.weatherPane.pack(side = BOTTOM, anchor = E)
        #CREATE DESCRIPTION LABEL
        self.weatherDescription = Label(self, font=('Helvetica',40), fg="black", bg="white",text='Description')
        self.weatherDescription.pack(side = TOP, anchor = E)
        #CREATE REQUESTS OBJECT
        self.request = requests
    def getWeather(self):
        self.cityName = 'Needham'
        APPID = '11dee608927c6bc5f293a9ee96e5ad91'
        weatherURL = 'http://api.openweathermap.org/data/2.5/weather?q=' + self.cityName + '&APPID=' + APPID 
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
            currentTemp = str(processedData[0]) + ' F'
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

class fullWindow:
    def __init__(self):
        self.rootWin = Tk()
        self.rootWin.configure(background='black')
        self.rootWin.attributes("-fullscreen", True)
        self.time = time.time() - 5*60; #this makes the loop below update weather right away

        #DIRECTION
        self.leftFrame = Frame(self.rootWin, background = 'white') #create frame for direction label
        self.leftFrame.pack(expand=False, fill = 'both', side = LEFT) #put frame against LEFT side, fill frame in x and y directions
        self.direction = direction(self.leftFrame) #create direction object in leftFrame
        self.direction.pack(side = TOP) #put direction object in frame (against LEFT side)

        #CLOCK
        self.rightFrame = Frame(self.rootWin, background = 'white') #create frame for clock label
        self.rightFrame.pack(expand=False, fill = 'both', side = LEFT) #put frame against RIGHT side, fill frame in x and y directions
        self.clock = clock(self.rightFrame) #create clock object in rightFrame
        self.clock.pack(side = BOTTOM ) #put clock object in frame (against RIGHT side)                                

        #WEATHER
        self.rightFrame = Frame(self.rootWin, background = 'white') #create frame for clock label
        self.rightFrame.pack(expand=False, fill = 'both', side = RIGHT) #put frame against RIGHT side, fill frame in x and y directions
        self.weather = weather(self.rightFrame) #create clock object in rightFrame
        self.weather.pack(side = TOP ) #put clock object in frame (against RIGHT side)        

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
            sung.time = time.time()
