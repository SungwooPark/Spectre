from Tkinter import *
import requests
from APPID_keys import newsAPPID

class news(Frame):
	def __init__(self, master, text_color = "white"):
		Frame.__init__(self, master, bg = 'black')
		#CREATE TITLE LABEL
		self.trendingNews = Label(self, font=('Helvetica',40), fg= text_color, bg="black",text='Trending News')
		self.trendingNews.pack(side = TOP, anchor = E)
		self.headlines = Label(self, font=('Helvetica',15), fg= text_color, bg="black",text='Headlines')
		self.headlines.pack(side = LEFT, anchor = SE)
		self.request = requests
	def getSources(self): #returns dictionary of news sources
		rawSources = self.request.get('https://newsapi.org/v1/sources?language=en')
		sourceJSON = rawSources.json()
		sourceDict = dict()
		for source in sourceJSON['sources']:
			sourceName = source['name'] #some of the names have (AU) or (UK) at the end
			sourceId = source['id']
			sourceDict[sourceName] = sourceId
		return sourceDict
	def getNews(self, news_source):
		source = news_source
		sortBy = 'top'
		newsURL = 'https://newsapi.org/v1/articles?source=' + source + '&sortBy=' + sortBy + '&apiKey=' + newsAPPID
		newsData = self.request.get(newsURL)
		newsJSON = newsData.json()
		newsHeadlines = newsJSON['articles']
		headlinesString = ''
		for article in newsHeadlines[1:4]: #first item is repeated, grab first three unique headlines
			headlinesString += (article['title'] + '\n')
		return headlinesString
	def updateNews(self, news_source):
		gatheredData = self.getNews(news_source)
		self.headlines.config(text = gatheredData)