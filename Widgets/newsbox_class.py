"""NewsBox module"""

import twitter
import indicoio
from Tkinter import *
from PIL import ImageTk, Image
# import cairosvg
import sys
from indicoio import sentiment
from config import indico_key,consumer_key,consumer_secret,access_token_key,access_token_secret
import color_map
import os

class newsBox(Frame):
	"""NewsBox widget class that analyzes a search term and returns a choropleth map of the average polarity of tweets with that term."""
	def __init__(self, master, text_color):
		"""Creates NewsBox widget with placeholder search term and map picture.
		Params: master - Tkinter frame in which the widget is placed
				text_color - string color name for font
		"""		Frame.__init__(self, master, bg = 'black')
		#CREATE TEMP LABEL
		self.title = Label(self, font=('Helvetica',40), fg= text_color, bg="black",text='SEARCH TERM')
		self.title.pack(side = TOP, anchor = NE)
		#CREATE IMAGE LABEL
		#cairosvg.svg2png(url = 'Widgets/choropleth_map.svg', write_to = 'Widgets/map.png')
		pic = Image.open('Widgets/map.png')
		self.choroMapPic = ImageTk.PhotoImage(pic)
		self.choroMap = Label(self, image = self.choroMapPic, bg = "black")
		self.choroMap.pack(side = BOTTOM, anchor = NE)
		#SET UP API KEYS
		indicoio.config.api_key = indico_key
		self.api = twitter.Api(consumer_key = consumer_key,
			consumer_secret = consumer_secret,
			access_token_key = access_token_key,
			access_token_secret = access_token_secret)

	def geo_collect_tweets(self, search_term, latitude, longitude, radius):
		"""Searches for tweets within certain radius of latitude and longitude with certain keyword in them.
		Params: search_term - string term used to search tweets
				latitude - double latitude for search parameters
				longitude - double longitude for search parameters
				radius - int radius of search
		Returns: list of unique string tweets
		"""
		i = None
		tweets = []
		rep = 1
		for n in range(2): #can only search 100 tweets at a time, so run search multiple times
			results = self.api.GetSearch(term = search_term, 
				count = 10, 
				result_type = 'recent', 
				max_id = i, #start a search from the most recent tweet id, working backwards
				geocode =(latitude, longitude, radius))
			for tweet in results:
				tweets.append(tweet.text)
			i = tweet.id - 1 #want it to start at the tweet after the last tweet
			rep += 1
		return list(set(tweets)) #set gets rid of repititve tweets, but need to return a list

	def geo_data_analysis(self, search_term):
		"""Finds the average positive/negative sentiment of tweets for each region.
		Params: search_term - string term used to search tweets
		Returns: list of four doubles (average polarity for West, South, Northeast, and Midwest)
		"""
		map_pol = dict()

		#A list of tweet texts from each region
		NE_text = self.geo_collect_tweets(search_term,42.781158,-71.398729,'250mi')
		S_text = self.geo_collect_tweets(search_term,33.000000,-84.000000,'500mi')
		MW_text = self.geo_collect_tweets(search_term,40.000000,-100.000000,'1000mi')
		W_text = self.geo_collect_tweets(search_term,35.000000,-120.000000,'250mi')
		
		#A list of sentiment values for the tweets from each region 
		NE_sentiment_values = sentiment(NE_text)
		S_sentiment_values = sentiment(S_text)
		MW_sentiment_values = sentiment(MW_text)
		W_sentiment_values = sentiment(W_text)

		#find the average sentiment value for each region
		NE_avg = sum(NE_sentiment_values)/len(NE_sentiment_values)
		S_avg = sum(S_sentiment_values)/len(S_sentiment_values)
		MW_avg = sum(MW_sentiment_values)/len(MW_sentiment_values)
		W_avg = sum(W_sentiment_values)/len(W_sentiment_values)

		return [W_avg,S_avg,NE_avg,MW_avg]

	def produce_map(self, search_term):
		"""Updates NewsBox-related Tkinter Label widgets with new search term and its corresponding choropleth map.
		Params: search_term - string term used to search tweets
		"""
		average_sentiments = self.geo_data_analysis(search_term)
		color_map.map_states(average_sentiments[0],average_sentiments[1],average_sentiments[2],average_sentiments[3],search_term)
		#cairosvg.svg2png(url = 'Widgets/choropleth_map.svg', write_to = 'Widgets/map.png')
		pic = Image.open('Widgets/map.png')
		resized_pic = pic.resize((600,400),Image.ANTIALIAS) #resize image to whatever dimensions you want
		self.choroMapPic = ImageTk.PhotoImage(resized_pic)
		self.choroMap.config(image = self.choroMapPic)
		self.choroMap.image = self.choroMapPic
		self.title.config(text = search_term)
