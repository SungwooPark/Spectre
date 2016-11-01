from Tkinter import *
import serial
import time
import requests

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
        Frame.__init__(self, master, bg = 'red')
        self.weatherText = Label(self, font=('Helvetica',100), fg="black", bg="white",text='WEATHER')
        self.weatherText.pack(side = TOP, anchor = E)
        self.request = requests
    def getWeather(self): #TODO: change to temp -- getTemp, tempText, etc
        self.cityName = 'Needham'
        APPID = '11dee608927c6bc5f293a9ee96e5ad91'
        weatherURL = 'http://api.openweathermap.org/data/2.5/weather?q=' + self.cityName + '&APPID=' + APPID 
        weatherData = self.request.get(weatherURL)
        weatherJSON = weatherData.json()
        weatherTemp = weatherJSON['main']['temp'] #example: 282.56 -- in Kelvin
##        weatherSky = weatherJSON['weather']['main'] #example: 'Clear', 'Rain', 'Snow'
        #weatherIconID = weatherJSON['weather']['icon'] -- returns id of icon (example: 'Old'?)
        return weatherTemp
    

class fullWindow:
    def __init__(self):
        self.rootWin = Tk()
        self.rootWin.configure(background='black')
        self.rootWin.attributes("-fullscreen", True)

        self.leftFrame = Frame(self.rootWin, background = 'white') #create frame for direction label
        self.leftFrame.pack(expand=False, fill = 'both', side = LEFT) #put frame against LEFT side, fill frame in x and y directions
        self.direction = direction(self.leftFrame) #create direction object in leftFrame
        self.direction.pack(side = TOP) #put direction object in frame (against LEFT side)

        self.rightFrame = Frame(self.rootWin, background = 'white') #create frame for clock label
        self.rightFrame.pack(expand=False, fill = 'both', side = LEFT) #put frame against RIGHT side, fill frame in x and y directions
        self.clock = clock(self.rightFrame) #create clock object in rightFrame
        self.clock.pack(side = BOTTOM ) #put clock object in frame (against RIGHT side)                                

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
        sung.direction.dirText.config(text = 'bob') #read_serial)
        currentTime = sung.clock.getTime()
        sung.clock.clockText.config(text = currentTime)
        currentTemp = str(sung.weather.getWeather())
        sung.weather.weatherText.config(text = currentTemp)
