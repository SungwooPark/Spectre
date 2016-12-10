"""News module"""

from Tkinter import *
import requests
from APPID_keys import newsAPPID

class news(Frame):
	"""News widget class that can get headlines from a specific news source."""
	def __init__(self, master, text_color = "white"):
		"""Creates news widget with placeholder headline values.
		Params: master - Tkinter frame in which the widget is placed
				text_color - string color name for font
		"""
		Frame.__init__(self, master, bg = 'black')
		self.trendingNews = Label(self, font=('Helvetica',40), fg= text_color, bg="black",text='Trending News')
		self.trendingNews.pack(side = TOP, anchor = E)
		self.headlines = Label(self, font=('Helvetica',15), fg= text_color, bg="black",text='Headlines')
		self.headlines.pack(side = LEFT, anchor = SE)
		self.request = requests
	def getSources(self):
		"""Gets dictionary of news sources using News API.
		Returns: dictionary of news sources with name as key and id as value
		"""
		sourceData = self.request.get('https://newsapi.org/v1/sources?language=en')
		sourceJSON = sourceData.json()
		sourceDict = dict()
		for source in sourceJSON['sources']:
			sourceName = source['name'] #some of the names have (AU) or (UK) at the end
			sourceId = source['id']
			sourceDict[sourceName] = sourceId
		sourceDict['ABC News'] = sourceDict['ABC News (AU)']
		return sourceDict
	def getNews(self, news_source):
		"""Gets top three headlines for specified news source.
		Params: news_source - string news source id
		Returns: string of headlines, each on a different line
		"""
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
		"""Updates news-related Tkinter Label widget with new headlines.
		Params: news_source - string news source id
		"""
		gatheredData = self.getNews(news_source)
		self.headlines.config(text = gatheredData)